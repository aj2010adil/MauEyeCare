"""
MauEyeCare AI — Fundus Image Classification Training Pipeline
=============================================================
This script demonstrates how to train a PyTorch model for optometry 
image triage and export it to ONNX for use in the Flask microservice.

Prerequisites:
    pip install -r requirements-ml.txt

Usage:
    python train_model.py --data_dir ./dataset --epochs 10
"""

import os
import argparse
import logging
from pathlib import Path

import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import models, transforms, datasets
from torch.utils.data import DataLoader

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

# Must match CONDITION_LABELS in app.py
NUM_CLASSES = 10
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

def build_model(num_classes: int) -> nn.Module:
    """Load a pretrained ResNet18 and replace the final classification head."""
    logging.info("Loading pretrained ResNet18 model...")
    # Use weights parameter instead of pretrained=True for modern torchvision
    try:
        model = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
    except AttributeError:
        # Fallback for older torchvision
        model = models.resnet18(pretrained=True)

    # Freeze base layers for fine-tuning
    for param in model.parameters():
        param.requires_grad = False

    # Replace the final fully connected layer
    num_ftrs = model.fc.in_features
    model.fc = nn.Linear(num_ftrs, num_classes)
    return model

def get_transforms():
    """Standard ImageNet transforms."""
    train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(15),
        transforms.ColorJitter(brightness=0.2, contrast=0.2),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    
    val_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    return train_transform, val_transform

def train(args):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logging.info(f"Using device: {device}")

    model = build_model(NUM_CLASSES).to(device)

    # If dataset exists, run real training loop. Otherwise, just export the untrained head.
    data_path = Path(args.data_dir)
    if data_path.exists() and any(data_path.iterdir()):
        logging.info(f"Dataset found at {data_path}. Starting training loop...")
        train_transform, val_transform = get_transforms()
        
        # Expects: dataset/train/Class1, dataset/train/Class2, etc.
        train_dataset = datasets.ImageFolder(os.path.join(data_path, 'train'), train_transform)
        train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True)
        
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(model.fc.parameters(), lr=args.lr)

        for epoch in range(args.epochs):
            model.train()
            running_loss = 0.0
            for inputs, labels in train_loader:
                inputs, labels = inputs.to(device), labels.to(device)

                optimizer.zero_grad()
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                loss.backward()
                optimizer.step()

                running_loss += loss.item() * inputs.size(0)

            epoch_loss = running_loss / len(train_dataset)
            logging.info(f"Epoch {epoch+1}/{args.epochs} - Loss: {epoch_loss:.4f}")
    else:
        logging.warning(f"No dataset found at '{data_path}'.")
        logging.warning("Skipping training loop. Exporting initialized model directly (Demo purpose).")

    export_onnx(model, args.output)

def export_onnx(model: nn.Module, output_path: str):
    """Exports the PyTorch model to ONNX format."""
    model.eval()
    
    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Create a dummy input matching the expected input shape (Batch, Channels, Height, Width)
    dummy_input = torch.randn(1, 3, 224, 224, device=next(model.parameters()).device)
    
    logging.info(f"Exporting model to ONNX format at {output_path}...")
    torch.onnx.export(
        model, 
        dummy_input, 
        output_path,
        export_params=True,
        opset_version=14,
        do_constant_folding=True,
        input_names=['input'],
        output_names=['output'],
        dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}}
    )
    logging.info("Export complete. The model is ready for the Flask microservice.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MauEyeCare Fundus Image Training")
    parser.add_argument("--data_dir", type=str, default="./dataset", help="Path to training images")
    parser.add_argument("--output", type=str, default="./models/eye_triage.onnx", help="Output ONNX path")
    parser.add_argument("--epochs", type=int, default=5, help="Number of training epochs")
    parser.add_argument("--batch_size", type=int, default=32, help="Batch size")
    parser.add_argument("--lr", type=float, default=0.001, help="Learning rate")
    args = parser.parse_args()

    train(args)
