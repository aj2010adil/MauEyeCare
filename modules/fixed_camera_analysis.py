#!/usr/bin/env python
"""
Fixed camera system with immediate AI analysis
"""
import cv2
import streamlit as st
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import datetime

def capture_and_analyze_immediately():
    """Capture photo and trigger immediate analysis"""
    
    # Initialize camera
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        return None, "Camera not accessible. Please check camera permissions."
    
    # Set camera properties
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    # Create placeholders for real-time feedback
    camera_placeholder = st.empty()
    status_placeholder = st.empty()
    
    # Face detection setup
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    captured_frame = None
    
    # Show live preview with capture button
    status_placeholder.info("📷 Camera is ready. Position your face and click capture when ready.")
    
    # Capture button
    if st.button("📸 Capture Photo Now", type="primary", key="immediate_capture"):
        ret, frame = cap.read()
        
        if ret:
            # Check face quality immediately
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            if len(faces) == 0:
                status_placeholder.error("❌ No face detected. Please position your face in the camera and try again.")
                cap.release()
                return None, "No face detected"
            
            if len(faces) > 1:
                status_placeholder.warning("⚠️ Multiple faces detected. Please ensure only one person is in frame.")
            
            # Get the best face
            face = max(faces, key=lambda x: x[2] * x[3])
            x, y, w, h = face
            
            # Check face size
            face_area = w * h
            frame_area = frame.shape[0] * frame.shape[1]
            
            if face_area < frame_area * 0.08:
                status_placeholder.warning("⚠️ Face is too small. Move closer to the camera.")
            elif face_area > frame_area * 0.7:
                status_placeholder.warning("⚠️ Face is too large. Move back from the camera.")
            else:
                status_placeholder.success("✅ Perfect! Face captured successfully.")
            
            captured_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Show captured image immediately
            camera_placeholder.image(captured_frame, caption="📸 Captured Photo", width=400)
        else:
            status_placeholder.error("❌ Failed to capture photo. Please try again.")
    
    cap.release()
    cv2.destroyAllWindows()
    
    if captured_frame is not None:
        return captured_frame, "Photo captured successfully"
    else:
        return None, "Photo capture cancelled"

def analyze_face_immediately(image_array, patient_name, age, gender):
    """Immediate face analysis with detailed results"""
    
    try:
        # Face detection
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        if len(faces) == 0:
            return {
                "status": "error",
                "message": "No face detected in the image",
                "recommendations": []
            }
        
        # Get face measurements
        face = max(faces, key=lambda x: x[2] * x[3])
        x, y, w, h = face
        face_ratio = w / h
        
        # Determine face shape with confidence
        if face_ratio > 1.2:
            face_shape = "Wide/Round"
            confidence = min(95, 70 + (face_ratio - 1.2) * 50)
            best_shapes = ["Rectangle", "Square", "Cat-Eye"]
            avoid_shapes = ["Round", "Oval"]
            reasoning = "Wide faces benefit from angular frames that add length and definition"
        elif face_ratio < 0.8:
            face_shape = "Long/Oval"
            confidence = min(95, 70 + (0.8 - face_ratio) * 50)
            best_shapes = ["Round", "Aviator", "Square"]
            avoid_shapes = ["Rectangle", "Cat-Eye"]
            reasoning = "Long faces look great with wider frames that add width and balance"
        else:
            face_shape = "Balanced/Square"
            confidence = min(95, 70 + (1.0 - abs(face_ratio - 1.0)) * 50)
            best_shapes = ["Round", "Oval", "Cat-Eye"]
            avoid_shapes = ["Square", "Rectangle"]
            reasoning = "Balanced faces can wear most frame styles, with round frames softening angular features"
        
        # Get spectacle recommendations based on analysis
        from modules.enhanced_spectacle_data import ENHANCED_SPECTACLE_DATA
        
        recommended_spectacles = []
        
        for spec_name, spec_data in ENHANCED_SPECTACLE_DATA.items():
            # Match by shape
            if spec_data['shape'] in best_shapes or spec_data['shape'] == "Any":
                # Age-based filtering
                if age < 25 and spec_data['category'] in ["Sunglasses", "Budget"]:
                    recommended_spectacles.append(spec_name)
                elif 25 <= age < 40 and spec_data['category'] in ["Prescription", "Sunglasses"]:
                    recommended_spectacles.append(spec_name)
                elif 40 <= age < 60 and spec_data['category'] in ["Prescription", "Progressive", "Luxury"]:
                    recommended_spectacles.append(spec_name)
                elif age >= 60 and spec_data['category'] in ["Progressive", "Prescription"]:
                    recommended_spectacles.append(spec_name)
        
        # Sort recommendations by suitability
        if age < 30:
            recommended_spectacles.sort(key=lambda x: ENHANCED_SPECTACLE_DATA[x]['price'])
        else:
            recommended_spectacles.sort(key=lambda x: -ENHANCED_SPECTACLE_DATA[x]['price'])
        
        return {
            "status": "success",
            "face_shape": face_shape,
            "face_coordinates": (x, y, w, h),
            "face_ratio": face_ratio,
            "confidence": confidence,
            "best_shapes": best_shapes,
            "avoid_shapes": avoid_shapes,
            "reasoning": reasoning,
            "recommended_spectacles": recommended_spectacles[:6],
            "analysis_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "patient_name": patient_name,
            "age": age,
            "gender": gender
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Analysis failed: {str(e)}",
            "recommendations": []
        }

def create_instant_analysis_display(analysis_result):
    """Create immediate visual display of analysis results"""
    
    if analysis_result["status"] == "success":
        # Success display
        st.success(f"✅ Analysis Complete!")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Face Shape", analysis_result["face_shape"])
        
        with col2:
            st.metric("Confidence", f"{analysis_result['confidence']:.1f}%")
        
        with col3:
            st.metric("Recommendations", len(analysis_result["recommended_spectacles"]))
        
        # Detailed results
        st.markdown("**🎯 Analysis Results:**")
        st.info(analysis_result["reasoning"])
        
        st.markdown(f"**✅ Best Frame Shapes:** {', '.join(analysis_result['best_shapes'])}")
        st.markdown(f"**❌ Avoid Frame Shapes:** {', '.join(analysis_result['avoid_shapes'])}")
        
        # Show recommended spectacles immediately
        if analysis_result["recommended_spectacles"]:
            st.markdown("**🔍 Top Spectacle Recommendations:**")
            
            from modules.enhanced_spectacle_data import ENHANCED_SPECTACLE_DATA
            
            for i, spec_name in enumerate(analysis_result["recommended_spectacles"][:3], 1):
                if spec_name in ENHANCED_SPECTACLE_DATA:
                    spec_data = ENHANCED_SPECTACLE_DATA[spec_name]
                    
                    with st.expander(f"{i}. {spec_data['brand']} {spec_data['model']} - ${spec_data['price']}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**Category:** {spec_data['category']}")
                            st.write(f"**Material:** {spec_data['material']}")
                            st.write(f"**Shape:** {spec_data['shape']}")
                        
                        with col2:
                            st.write(f"**Source:** {spec_data['source']}")
                            st.write(f"**Delivery:** {spec_data['delivery_days']} days")
                            st.write(f"**Lens Price:** ${spec_data['lens_price']}")
                        
                        total_price = spec_data['price'] + spec_data['lens_price']
                        st.markdown(f"**Total Price: ${total_price}**")
        
        return True
    
    else:
        # Error display
        st.error(f"❌ {analysis_result['message']}")
        st.info("💡 **Tips for better results:**")
        st.info("• Ensure good lighting")
        st.info("• Face the camera directly")
        st.info("• Remove existing glasses")
        st.info("• Keep face centered in frame")
        
        return False

def trigger_immediate_analysis_workflow(patient_name, age, gender):
    """Complete workflow: capture -> analyze -> display results"""
    
    st.markdown("### 📸 Instant Photo Capture & Analysis")
    
    # Step 1: Capture photo
    st.markdown("**Step 1: Capture Photo**")
    captured_image, message = capture_and_analyze_immediately()
    
    if captured_image is not None:
        # Store in session state
        st.session_state['instant_captured_photo'] = captured_image
        
        # Step 2: Immediate analysis
        st.markdown("**Step 2: AI Analysis**")
        
        with st.spinner("🤖 AI analyzing your face shape and matching spectacles..."):
            analysis_result = analyze_face_immediately(captured_image, patient_name, age, gender)
        
        # Store analysis results
        st.session_state['instant_analysis'] = analysis_result
        
        # Step 3: Display results
        st.markdown("**Step 3: Results**")
        success = create_instant_analysis_display(analysis_result)
        
        if success:
            # Step 4: Generate comprehensive report
            if st.button("📋 Generate Complete Report with Pricing", type="primary"):
                generate_comprehensive_report_with_pricing(analysis_result, captured_image)
        
        return True
    
    else:
        st.error(f"❌ {message}")
        return False

def generate_comprehensive_report_with_pricing(analysis_result, patient_photo):
    """Generate final comprehensive report with pricing table"""
    
    from modules.enhanced_spectacle_data import ENHANCED_SPECTACLE_DATA, generate_pricing_table_data
    
    st.markdown("### 📊 Comprehensive Analysis Report")
    
    # Generate pricing table
    pricing_table = generate_pricing_table_data(analysis_result["recommended_spectacles"], "Single Vision")
    
    if pricing_table:
        # Display pricing table
        st.markdown("**💰 Detailed Pricing Table:**")
        df_pricing = pd.DataFrame(pricing_table)
        st.dataframe(df_pricing, use_container_width=True)
        
        # Create combined image report
        from modules.enhanced_spectacle_data import create_comprehensive_report_image
        
        with st.spinner("🎨 Creating visual report..."):
            comprehensive_report = create_comprehensive_report_image(
                patient_photo,
                analysis_result,
                pricing_table
            )
        
        st.image(comprehensive_report, caption="📋 Complete Analysis Report", use_column_width=True)
        
        # Download options
        col1, col2 = st.columns(2)
        
        with col1:
            # Download image report
            img_buffer = BytesIO()
            comprehensive_report.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
            
            st.download_button(
                label="📄 Download Visual Report",
                data=img_buffer.getvalue(),
                file_name=f"Spectacle_Analysis_{analysis_result['patient_name'].replace(' ', '_')}_{timestamp}.png",
                mime="image/png"
            )
        
        with col2:
            # Download pricing table as CSV
            csv_buffer = StringIO()
            df_pricing.to_csv(csv_buffer, index=False)
            
            st.download_button(
                label="📊 Download Pricing Table",
                data=csv_buffer.getvalue(),
                file_name=f"Spectacle_Pricing_{analysis_result['patient_name'].replace(' ', '_')}_{timestamp}.csv",
                mime="text/csv"
            )
        
        st.balloons()
        st.success("✅ Complete analysis report generated successfully!")
    
    else:
        st.error("❌ Failed to generate pricing table")

# Import required for CSV export
from io import StringIO
import pandas as pd