#!/usr/bin/env python
"""
Simple and reliable camera system for Streamlit
"""
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("Warning: OpenCV not available. Using fallback methods.")

import streamlit as st
import numpy as np
from PIL import Image
import time

def simple_camera_capture():
    """Simple camera capture that works reliably"""
    
    st.markdown("### 📷 Camera Capture")
    
    if not CV2_AVAILABLE:
        st.warning("⚠️ OpenCV not available. Using Streamlit's built-in camera.")
        return show_camera_with_preview()
    
    # Camera status
    camera_status = st.empty()
    camera_feed = st.empty()
    capture_button_placeholder = st.empty()
    
    # Initialize camera
    try:
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            st.error("❌ Camera not accessible. Please check:")
            st.info("• Camera permissions in browser")
            st.info("• Camera is not being used by another app")
            st.info("• Camera drivers are installed")
            return None
        
        # Set camera properties
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        camera_status.success("✅ Camera initialized successfully")
        
        # Show live preview
        st.markdown("**Live Camera Preview:**")
        
        # Create a button to capture
        if st.button("📸 Capture Photo", type="primary", key="simple_capture"):
            # Capture frame
            ret, frame = cap.read()
            
            if ret:
                # Convert BGR to RGB
                if CV2_AVAILABLE:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                else:
                    frame_rgb = frame
                
                # Show captured image
                st.image(frame_rgb, caption="📸 Captured Photo", width=500)
                
                # Release camera
                cap.release()
                if CV2_AVAILABLE:
                    cv2.destroyAllWindows()
                
                return frame_rgb
            else:
                st.error("❌ Failed to capture photo")
                cap.release()
                return None
        
        # Show current frame
        ret, frame = cap.read()
        if ret:
            if CV2_AVAILABLE:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            else:
                frame_rgb = frame
            camera_feed.image(frame_rgb, caption="Live Camera Feed", width=500)
        
        # Release camera if not capturing
        cap.release()
        if CV2_AVAILABLE:
            cv2.destroyAllWindows()
        
    except Exception as e:
        st.error(f"❌ Camera error: {str(e)}")
        st.info("💡 Try these solutions:")
        st.info("• Refresh the page")
        st.info("• Allow camera permissions")
        st.info("• Use photo upload instead")
        return None
    
    return None

def show_camera_with_preview():
    """Show camera with live preview using Streamlit's built-in camera"""
    
    st.markdown("### 📷 Camera Capture")
    
    # Auto-open camera with Streamlit's built-in camera input
    camera_photo = st.camera_input(
        "📸 Take a photo for AI analysis",
        help="Position your face in the center and ensure good lighting",
        key="auto_camera"
    )
    
    if camera_photo is not None:
        # Convert to PIL Image
        image = Image.open(camera_photo)
        image_array = np.array(image)
        
        st.success("✅ Photo captured successfully!")
        st.image(image_array, caption="Captured Photo", width=400)
        return image_array
    
    # Instructions for better photos
    st.info("💡 **Tips for best results:**")
    st.markdown("""
    • **Face the camera directly**
    • **Ensure good lighting**
    • **Remove existing glasses**
    • **Keep face centered**
    • **Maintain neutral expression**
    """)
    
    return None

def analyze_captured_photo(image_array, patient_name, age, gender):
    """Analyze the captured photo immediately"""
    
    try:
        from modules.comprehensive_spectacle_database import COMPREHENSIVE_SPECTACLE_DATABASE
    except:
        from modules.enhanced_spectacle_data import ENHANCED_SPECTACLE_DATA as COMPREHENSIVE_SPECTACLE_DATABASE
    
    import datetime
    
    try:
        if CV2_AVAILABLE:
            # Face detection with OpenCV
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        else:
            # Fallback: assume face is in center of image
            h, w = image_array.shape[:2]
            face_w, face_h = w // 3, h // 3
            x, y = (w - face_w) // 2, (h - face_h) // 2
            faces = [(x, y, face_w, face_h)]
        
        if len(faces) == 0:
            return {
                "status": "error",
                "message": "No face detected. Please ensure your face is clearly visible in the photo.",
                "recommendations": []
            }
        
        # Get the largest face
        face = max(faces, key=lambda x: x[2] * x[3])
        x, y, w, h = face
        
        # Calculate face measurements
        face_ratio = w / h
        face_area = w * h
        image_area = image_array.shape[0] * image_array.shape[1]
        
        # Determine face shape
        if face_ratio > 1.2:
            face_shape = "Wide/Round"
            confidence = min(95, 70 + (face_ratio - 1.2) * 50)
            best_shapes = ["Rectangle", "Square", "Cat-Eye"]
            avoid_shapes = ["Round", "Oval"]
            reasoning = "Wide faces look great with angular frames that add length and definition"
        elif face_ratio < 0.8:
            face_shape = "Long/Oval"
            confidence = min(95, 70 + (0.8 - face_ratio) * 50)
            best_shapes = ["Round", "Aviator", "Square"]
            avoid_shapes = ["Rectangle", "Cat-Eye"]
            reasoning = "Long faces benefit from wider frames that add balance and width"
        else:
            face_shape = "Balanced/Square"
            confidence = min(95, 70 + (1.0 - abs(face_ratio - 1.0)) * 50)
            best_shapes = ["Round", "Oval", "Cat-Eye"]
            avoid_shapes = ["Square", "Rectangle"]
            reasoning = "Balanced faces can wear most styles, with round frames softening angular features"
        
        # Find matching spectacles
        recommended_spectacles = []
        
        for spec_name, spec_data in COMPREHENSIVE_SPECTACLE_DATABASE.items():
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
        
        # Sort by price (budget-friendly for younger, premium for older)
        if age < 30:
            recommended_spectacles.sort(key=lambda x: COMPREHENSIVE_SPECTACLE_DATABASE[x]['price'])
        else:
            recommended_spectacles.sort(key=lambda x: -COMPREHENSIVE_SPECTACLE_DATABASE[x]['price'])
        
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
            "gender": gender,
            "face_area_percentage": (face_area / image_area) * 100
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Analysis failed: {str(e)}",
            "recommendations": []
        }

def display_analysis_results(analysis_result):
    """Display analysis results in a user-friendly format"""
    
    if analysis_result["status"] == "success":
        st.success("🎉 Face Analysis Complete!")
        
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Face Shape", analysis_result["face_shape"])
        
        with col2:
            st.metric("Confidence", f"{analysis_result['confidence']:.1f}%")
        
        with col3:
            st.metric("Recommendations", len(analysis_result["recommended_spectacles"]))
        
        with col4:
            st.metric("Face Coverage", f"{analysis_result['face_area_percentage']:.1f}%")
        
        # Analysis explanation
        st.info(f"💡 **Analysis:** {analysis_result['reasoning']}")
        
        # Frame recommendations
        st.markdown("**✅ Best Frame Shapes for You:**")
        for shape in analysis_result['best_shapes']:
            st.success(f"• {shape}")
        
        st.markdown("**❌ Frame Shapes to Avoid:**")
        for shape in analysis_result['avoid_shapes']:
            st.warning(f"• {shape}")
        
        # Spectacle recommendations
        if analysis_result["recommended_spectacles"]:
            st.markdown("---")
            st.markdown("**🔍 Top Spectacle Recommendations:**")
            
            try:
                from modules.comprehensive_spectacle_database import COMPREHENSIVE_SPECTACLE_DATABASE
            except:
                from modules.enhanced_spectacle_data import ENHANCED_SPECTACLE_DATA as COMPREHENSIVE_SPECTACLE_DATABASE
            
            for i, spec_name in enumerate(analysis_result["recommended_spectacles"][:4], 1):
                if spec_name in COMPREHENSIVE_SPECTACLE_DATABASE:
                    spec_data = COMPREHENSIVE_SPECTACLE_DATABASE[spec_name]
                    
                    with st.expander(f"{i}. {spec_data['brand']} {spec_data['model']} - ${spec_data['price']}", expanded=(i==1)):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.write(f"**Frame Price:** ${spec_data['price']}")
                            st.write(f"**Lens Price:** ${spec_data['lens_price']}")
                            total_price = spec_data['price'] + spec_data['lens_price']
                            st.write(f"**Total Price:** ${total_price}")
                        
                        with col2:
                            st.write(f"**Material:** {spec_data['material']}")
                            st.write(f"**Shape:** {spec_data['shape']}")
                            st.write(f"**Category:** {spec_data['category']}")
                        
                        with col3:
                            st.write(f"**Source:** {spec_data['source']}")
                            st.write(f"**Delivery:** {spec_data['delivery_days']} days")
                            st.write(f"**Status:** {spec_data['availability']}")
                        
                        st.write(f"**Description:** {spec_data['description']}")
        
        return True
    
    else:
        st.error(f"❌ Analysis Failed: {analysis_result['message']}")
        
        st.markdown("**💡 Tips for Better Results:**")
        st.info("• Ensure good lighting")
        st.info("• Face the camera directly")
        st.info("• Remove existing glasses")
        st.info("• Keep face centered and clearly visible")
        st.info("• Try taking another photo")
        
        return False

def complete_camera_analysis_workflow(patient_name, age, gender):
    """Complete workflow: camera -> capture -> analyze -> results"""
    
    st.markdown("## 📸 Complete Camera Analysis Workflow")
    
    # Step 1: Camera capture
    st.markdown("### Step 1: Capture Photo")
    captured_image = show_camera_with_preview()
    
    if captured_image is not None:
        # Store in session state
        st.session_state['workflow_captured_image'] = captured_image
        
        # Step 2: Analysis
        st.markdown("### Step 2: AI Face Analysis")
        
        with st.spinner("🤖 Analyzing your face shape and matching spectacles..."):
            analysis_result = analyze_captured_photo(captured_image, patient_name, age, gender)
        
        # Store analysis
        st.session_state['workflow_analysis'] = analysis_result
        
        # Step 3: Results
        st.markdown("### Step 3: Analysis Results")
        success = display_analysis_results(analysis_result)
        
        if success:
            # Step 4: Generate report
            st.markdown("### Step 4: Generate Complete Report")
            
            if st.button("📋 Generate Comprehensive Report", type="primary"):
                generate_final_report(analysis_result, captured_image)
        
        return True
    
    return False

def generate_final_report(analysis_result, patient_photo):
    """Generate final comprehensive report with pricing and downloads"""
    
    from modules.enhanced_spectacle_data import generate_pricing_table_data, create_comprehensive_report_image
    import pandas as pd
    from io import BytesIO, StringIO
    import datetime
    
    st.markdown("## 📊 Comprehensive Analysis Report")
    
    # Generate pricing table
    pricing_table = generate_pricing_table_data(analysis_result["recommended_spectacles"], "Single Vision")
    
    if pricing_table:
        # Display pricing table
        st.markdown("**💰 Detailed Pricing Table:**")
        df_pricing = pd.DataFrame(pricing_table)
        st.dataframe(df_pricing, use_container_width=True)
        
        # Create visual report
        with st.spinner("🎨 Creating visual report..."):
            comprehensive_report = create_comprehensive_report_image(
                patient_photo,
                analysis_result,
                pricing_table
            )
        
        st.image(comprehensive_report, caption="📋 Complete Analysis Report", use_column_width=True)
        
        # Download options
        st.markdown("**📥 Download Options:**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Download visual report
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
            # Download pricing CSV
            csv_buffer = StringIO()
            df_pricing.to_csv(csv_buffer, index=False)
            
            st.download_button(
                label="📊 Download Pricing CSV",
                data=csv_buffer.getvalue(),
                file_name=f"Spectacle_Pricing_{analysis_result['patient_name'].replace(' ', '_')}_{timestamp}.csv",
                mime="text/csv"
            )
        
        with col3:
            # Add to inventory
            if st.button("🛒 Add All to Inventory"):
                from modules.inventory_utils import add_or_update_inventory
                
                added_count = 0
                for spec_name in analysis_result["recommended_spectacles"]:
                    add_or_update_inventory(spec_name, 5)
                    added_count += 1
                
                st.success(f"✅ Added {added_count} spectacles to inventory!")
        
        st.balloons()
        st.success("🎉 Complete analysis report generated successfully!")
    
    else:
        st.error("❌ Failed to generate pricing table")