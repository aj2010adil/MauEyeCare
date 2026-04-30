"""
MauEyeCare AI Microservice
===========================
Flask application providing:
  POST /analyze   — Image triage (fundus/OCT) → condition suggestions + confidence
  POST /ocr       — Handwritten note OCR via Tesseract
  POST /rx-assist — Prescription suggestion via Ollama LLM (offline-capable)
  GET  /health    — Health check

⚠ DECISION SUPPORT ONLY — All outputs must be reviewed by a licensed clinician.
"""

import os
import io
import base64
import logging
import json
import time
from pathlib import Path
import pydicom

import numpy as np
from flask import Flask, request, jsonify
from PIL import Image
import pytesseract

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s"
)
logger = logging.getLogger("MauEyeCare.AI")

app = Flask(__name__)

# ── Config ─────────────────────────────────────────────────────────────────────
MODEL_VERSION = os.getenv("MODEL_VERSION", "1.0.0-demo")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")
USE_ONNX = os.getenv("USE_ONNX", "false").lower() == "true"
ONNX_MODEL_PATH = os.getenv("ONNX_MODEL_PATH", "models/eye_triage.onnx")

# ── Optional ONNX runtime ──────────────────────────────────────────────────────
onnx_session = None
if USE_ONNX and Path(ONNX_MODEL_PATH).exists():
    try:
        import onnxruntime as ort
        onnx_session = ort.InferenceSession(ONNX_MODEL_PATH)
        logger.info("ONNX model loaded: %s", ONNX_MODEL_PATH)
    except ImportError:
        logger.warning("onnxruntime not installed — using demo mode")

# ── Condition Labels ───────────────────────────────────────────────────────────
CONDITION_LABELS = [
    "Normal / No significant finding",
    "Diabetic Retinopathy (Mild)",
    "Diabetic Retinopathy (Moderate-Severe)",
    "Glaucoma Suspect",
    "Age-related Macular Degeneration",
    "Hypertensive Retinopathy",
    "Optic Disc Abnormality",
    "Retinal Detachment",
    "Choroidal Lesion",
    "Image Quality Insufficient",
]

AI_DISCLAIMER = (
    "DECISION SUPPORT ONLY — These AI suggestions do not constitute a medical "
    "diagnosis. Results must be reviewed and confirmed by a qualified ophthalmologist "
    "or optometrist before any clinical action is taken."
)


# ── Utility: preprocess image ──────────────────────────────────────────────────
def preprocess_image(img: Image.Image, size=(224, 224)) -> np.ndarray:
    """Resize, normalize to [0,1], return shape (1, 3, H, W)."""
    img = img.convert("RGB").resize(size)
    arr = np.array(img, dtype=np.float32) / 255.0
    mean = np.array([0.485, 0.456, 0.406])
    std = np.array([0.229, 0.224, 0.225])
    arr = (arr - mean) / std
    return arr.transpose(2, 0, 1)[np.newaxis]  # (1, C, H, W)


def assess_image_quality(img: Image.Image) -> float:
    """Simple quality heuristic: brightness variance proxy."""
    gray = np.array(img.convert("L"), dtype=np.float32)
    score = float(np.clip(gray.var() / 3000.0, 0.0, 1.0))
    return round(score, 4)


# ── /analyze ─────────────────────────────────────────────────────────────────
@app.route("/analyze", methods=["POST"])
def analyze():
    if "image" not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    file = request.files["image"]
    image_type = request.form.get("image_type", "unknown")

    try:
        if file.filename and file.filename.lower().endswith('.dcm'):
            ds = pydicom.dcmread(io.BytesIO(file.read()))
            pixel_array = ds.pixel_array
            pixel_array = ((pixel_array - pixel_array.min()) / (pixel_array.max() - pixel_array.min()) * 255.0)
            pixel_array = pixel_array.astype(np.uint8)
            if len(pixel_array.shape) == 2:
                img = Image.fromarray(pixel_array).convert("RGB")
            else:
                img = Image.fromarray(pixel_array)
        else:
            img = Image.open(io.BytesIO(file.read()))

        quality_score = assess_image_quality(img)

        if onnx_session is not None:
            # Real ONNX inference
            input_name = onnx_session.get_inputs()[0].name
            input_arr = preprocess_image(img)
            outputs = onnx_session.run(None, {input_name: input_arr})
            raw_scores = outputs[0][0]

            # Softmax
            exp_scores = np.exp(raw_scores - raw_scores.max())
            probs = exp_scores / exp_scores.sum()

            top_k = 3
            top_idx = probs.argsort()[::-1][:top_k]
            conditions = [CONDITION_LABELS[i] for i in top_idx]
            confidences = [round(float(probs[i]), 4) for i in top_idx]
        else:
            # Demo mode: simulate plausible results based on image quality
            logger.info("Demo mode — returning simulated AI results")
            if quality_score < 0.2:
                conditions = ["Image Quality Insufficient"]
                confidences = [0.91]
            else:
                conditions = [
                    "Normal / No significant finding",
                    "Diabetic Retinopathy (Mild)",
                    "Glaucoma Suspect",
                ]
                confidences = [0.72, 0.18, 0.10]

        logger.info(
            "Analyze: type=%s quality=%.3f top=%s conf=%.2f",
            image_type, quality_score, conditions[0], confidences[0]
        )

        return jsonify({
            "condition_suggestions": conditions,
            "confidence": confidences,
            "image_quality_score": quality_score,
            "model_version": MODEL_VERSION,
            "disclaimer": AI_DISCLAIMER,
            "image_type": image_type,
        })

    except Exception as e:
        logger.error("Analyze error: %s", str(e), exc_info=True)
        return jsonify({"error": str(e)}), 500


# ── /feedback ────────────────────────────────────────────────────────────────
@app.route("/feedback", methods=["POST"])
def feedback():
    """
    Accepts: JSON { "image_id": str, "image_base64": str, "correct_label": str }
    Returns: { "status": str, "model_updated": bool }
    """
    body = request.get_json()
    if not body:
        return jsonify({"error": "JSON body required"}), 400

    image_id = body.get("image_id", "unknown")
    image_base64 = body.get("image_base64", "")
    correct_label = body.get("correct_label", "")

    if not image_base64 or not correct_label:
        return jsonify({"error": "Missing image_base64 or correct_label"}), 400

    if correct_label not in CONDITION_LABELS:
        return jsonify({"error": f"Invalid label. Must be one of: {CONDITION_LABELS}"}), 400

    try:
        # 1. Save image to dataset
        import base64
        image_data = base64.b64decode(image_base64)
        
        # Determine dataset path (swap slashes for safe Windows/Linux directory names)
        safe_label = correct_label.replace("/", "_")
        dataset_dir = Path(__file__).parent / "dataset" / "train" / safe_label
        dataset_dir.mkdir(parents=True, exist_ok=True)
        
        image_path = dataset_dir / f"{image_id}.jpg"
        with open(image_path, "wb") as f:
            f.write(image_data)
        
        logger.info(f"Saved feedback image for label '{correct_label}' to {image_path}")

        # 2. Defer retraining to off-hours ETL pipeline
        logger.info("Feedback saved to dataset. Fine-tuning queued for off-hours ETL processing.")
        return jsonify({"status": "Correction queued for overnight training.", "model_updated": False})

    except Exception as e:
        logger.error("Feedback error: %s", str(e), exc_info=True)
        return jsonify({"error": str(e)}), 500


# ── /ocr ─────────────────────────────────────────────────────────────────────
@app.route("/ocr", methods=["POST"])
def ocr():
    """
    Accepts: multipart/form-data with 'image' file
    Returns: { "text": str, "confidence": float }
    """
    if "image" not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    file = request.files["image"]
    try:
        img = Image.open(io.BytesIO(file.read()))

        # Tesseract OCR
        text = pytesseract.image_to_string(img, lang="eng+hin")
        data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

        # Average confidence (filter -1 values)
        confs = [int(c) for c in data["conf"] if c != "-1" and int(c) >= 0]
        avg_conf = round(sum(confs) / len(confs) / 100.0, 4) if confs else 0.0

        logger.info("OCR: extracted %d chars, conf=%.2f", len(text), avg_conf)
        return jsonify({"text": text.strip(), "confidence": avg_conf})

    except Exception as e:
        logger.error("OCR error: %s", str(e), exc_info=True)
        return jsonify({"error": str(e)}), 500


# ── /rx-assist ────────────────────────────────────────────────────────────────
@app.route("/rx-assist", methods=["POST"])
def rx_assist():
    """
    Accepts: JSON { "doctor_notes": str, "exam_context": str }
    Returns: { "suggestion": str, "disclaimer": str }
    Calls Ollama LLM locally; falls back to rule-based if Ollama unavailable.
    """
    body = request.get_json()
    if not body:
        return jsonify({"error": "JSON body required"}), 400

    doctor_notes = body.get("doctor_notes", "")
    exam_context = body.get("exam_context", "")

    prompt = f"""You are an optometry clinical decision support assistant.
A clinician has provided the following notes and exam context.
Suggest relevant prescription medications, dosage instructions, and follow-up actions.
Always include safety warnings. Never present suggestions as definitive — they require clinician review.

Doctor's Notes: {doctor_notes}
Exam Context: {exam_context}

Provide a structured, concise clinical suggestion:"""

    # Try Ollama
    suggestion = None
    try:
        import urllib.request
        payload = json.dumps({
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.3, "num_predict": 400}
        }).encode()

        req = urllib.request.Request(
            f"{OLLAMA_URL}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read())
            suggestion = result.get("response", "").strip()
            logger.info("Rx-assist via Ollama (%s): %d chars", OLLAMA_MODEL, len(suggestion))
    except Exception as e:
        logger.warning("Ollama unavailable (%s) — using rule-based fallback", str(e))

    # Rule-based fallback
    if not suggestion:
        suggestion = generate_rule_based_suggestion(doctor_notes)

    return jsonify({
        "suggestion": suggestion,
        "disclaimer": AI_DISCLAIMER,
        "source": "ollama" if suggestion and "Ollama" not in suggestion else "rule_based"
    })


def generate_rule_based_suggestion(notes: str) -> str:
    """Simple keyword-based Rx suggestion fallback."""
    notes_lower = notes.lower()
    parts = []

    if "dry eye" in notes_lower or "dry" in notes_lower:
        parts.append("• Lubricating Eye Drops (e.g., Carboxymethylcellulose 0.5%) — 1-2 drops TID PRN")

    if "infection" in notes_lower or "conjunctivitis" in notes_lower or "pink eye" in notes_lower:
        parts.append("• Antibiotic Eye Drops (e.g., Moxifloxacin 0.5%) — 1 drop QID × 5 days")
        parts.append("• Maintain eyelid hygiene; avoid touching eyes")

    if "glaucoma" in notes_lower or "iop" in notes_lower or "pressure" in notes_lower:
        parts.append("• IOP-lowering drops (e.g., Timolol 0.5% or Latanoprost 0.005%) — 1 drop at bedtime")
        parts.append("• Follow-up in 4 weeks to reassess IOP")

    if "allerg" in notes_lower or "itch" in notes_lower:
        parts.append("• Antihistamine drops (e.g., Olopatadine 0.1%) — 1 drop BID")

    if not parts:
        parts.append("• Clinical notes reviewed. No specific medication triggers identified.")
        parts.append("• Recommend full examination and specialist review.")

    parts.append("\n⚠ DECISION SUPPORT ONLY — Clinician review mandatory before prescribing.")
    return "\n".join(parts)


# ── /chatbot ──────────────────────────────────────────────────────────────────
@app.route("/chatbot", methods=["POST"])
def chatbot():
    data = request.json or {}
    message = (data.get("message") or "").strip().lower()
    
    if not message:
        return jsonify({"reply": "Hello! How can I assist you with your booking or eye care today?"}), 400
        
    reply = "I understand you need assistance. To confirm, would you like me to reserve an optometry review?"
    
    # Simple rule-based intent parsing
    if any(kw in message for kw in ["book", "schedule", "appoint", "reserve"]):
        reply = "Certainly! I've flagged a provisional calendar hold. Please confirm if a morning or afternoon slot works best."
    elif any(kw in message for kw in ["cancel", "reschedule", "change"]):
        reply = "I can modify that appointment. Please provide your patient file identifier so I may verify the calendar records."
    elif any(kw in message for kw in ["blur", "pain", "itch", "red"]):
        reply = "That sounds uncomfortable. I recommend prioritizing an urgent visual evaluation. Should I fit you in tomorrow?"
    elif any(kw in message for kw in ["frame", "lens", "glass"]):
        reply = "Our optical shop has multiple designer configurations! Drop by any time to sample prescription optics."
        
    return jsonify({"reply": reply})


# ── /health ───────────────────────────────────────────────────────────────────
@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "service": "MauEyeCare AI Microservice",
        "model_version": MODEL_VERSION,
        "onnx_loaded": onnx_session is not None,
        "timestamp": time.time()
    })


# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5050))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    logger.info("Starting MauEyeCare AI service on port %d", port)
    app.run(host="0.0.0.0", port=port, debug=debug)
