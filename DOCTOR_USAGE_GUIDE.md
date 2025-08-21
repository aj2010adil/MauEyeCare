# MauEyeCare - Doctor Usage Guide

## 🚀 Quick Start

### 1. Launch the Application
- **Double-click** `MauEyeCareLauncher.exe`
- The application will automatically:
  - Start the backend server (port 8001)
  - Start the frontend server (port 5173)
  - Open your browser to `http://localhost:5173`
  - Check and install any missing dependencies

### 2. Login
- Use your doctor credentials to log in
- The system will remember your session

---

## 📋 Daily Workflow

### **Patient Consultation Process**

#### Step 1: Create/Find Patient
1. Go to **Patients** section
2. Click **"Add New Patient"** or search existing patients
3. Fill in patient details:
   - Name, Phone, Age, Gender
   - Medical history (if any)

#### Step 2: Start Consultation
1. Select the patient
2. Click **"Start Consultation"**
3. Record patient symptoms and complaints
4. Perform eye examination
5. Document findings in the visit notes

#### Step 3: Write Prescription
1. Click **"Create Prescription"**
2. Fill in prescription details:
   - **RX Values**: Sphere, Cylinder, Axis, Add
   - **Spectacles**: Select from inventory or add new
   - **Medicines**: Choose from available medicines
3. Use **Auto-Suggest** features for faster entry
4. Review and save prescription

#### Step 4: Export Prescription
1. Click **"Export"** on the prescription
2. Choose format:
   - **HTML**: For email/web sharing
   - **PDF**: For printing
   - **DOCX**: For Word documents
3. Prescription includes:
   - Clinic branding
   - Patient details
   - Complete RX values
   - QR code for online access

---

## 🕶️ Spectacle Showcase & Sales

### **Browse Spectacles**
1. Go to **Showcase** section
2. Use filters to find spectacles:
   - Brand (Ray-Ban, Oakley, Titan, etc.)
   - Frame shape (Aviator, Round, Rectangle)
   - Price range
   - Gender/Age group
3. Switch between **Grid** and **List** views

### **Compare Spectacles**
1. Click **"Compare"** button on spectacles
2. Add up to 3 spectacles for side-by-side comparison
3. View detailed specifications
4. Compare prices and features

### **Virtual Try-On**
1. Click **"Try On"** button on any spectacle
2. Allow camera access when prompted
3. Position your face in the camera view
4. The spectacle will overlay on your face
5. Adjust zoom, rotation, and brightness
6. **Capture** the image for sharing
7. **Download** or **Share** the try-on image

### **Add to Cart & Checkout**
1. Click **"Add to Cart"** on selected spectacles
2. Review cart contents
3. Proceed to checkout
4. Complete payment process
5. Inventory automatically updates

---

## 📦 Inventory Management

### **Upload Inventory**
1. Click **"Upload Inventory"** button
2. Choose upload method:
   - **CSV File**: Bulk upload with template
   - **Individual Entry**: Add items one by one
3. Download template for CSV format
4. Upload file and review results

### **Add Products via Image**
1. Click **"Add via Image"** button
2. Choose method:
   - **Upload Image**: Select from computer
   - **Take Photo**: Use camera
3. System will auto-analyze image and suggest:
   - Product name and brand
   - Category and specifications
   - Estimated price
4. Review and edit suggestions
5. Save product to inventory

### **Manage Stock**
- View current stock levels
- Set low stock alerts
- Update quantities after sales
- Track product performance

---

## 🔧 Advanced Features

### **Auto-Suggest Input**
- **Patient Names**: Type to search existing patients
- **Diagnoses**: Common eye conditions with descriptions
- **Medicines**: Complete medicine database with dosages
- **Spectacle Brands**: Popular brands and models

### **QR Code Integration**
- Every prescription gets a unique QR code
- Patients can scan to view prescription online
- Share QR codes via WhatsApp or email
- Track prescription access

### **Image Analysis**
- Upload product photos for auto-tagging
- AI-powered brand and model recognition
- Automatic price suggestions
- Specification extraction

### **Keyboard Shortcuts**
- **H**: Open help
- **N**: New prescription
- **S**: Search
- **C**: Compare spectacles
- **T**: Try-on mode

---

## 📱 Mobile-Friendly Features

### **Responsive Design**
- Works on tablets and phones
- Touch-friendly interface
- Swipe gestures for navigation
- Optimized for different screen sizes

### **Camera Integration**
- Use phone camera for try-on
- Capture product images
- Photo-based patient records
- Document sharing

---

## 🛠️ Troubleshooting

### **Application Won't Start**
1. Check if Node.js is installed
2. Verify PostgreSQL is running
3. Check firewall settings
4. Run as administrator if needed

### **Camera Not Working**
1. Allow camera permissions in browser
2. Check if camera is in use by another app
3. Try refreshing the page
4. Check browser settings

### **Export Issues**
1. Ensure you have write permissions
2. Check available disk space
3. Try different export format
4. Restart application if needed

### **Database Connection**
1. Verify PostgreSQL is running
2. Check database credentials
3. Ensure network connectivity
4. Restart backend service

---

## 📞 Support

### **Technical Support**
- Check the logs in the `logs/` folder
- Review error messages in browser console
- Contact system administrator

### **Training**
- Watch tutorial videos
- Practice with sample data
- Use the help system (press H)

---

## 🎯 Best Practices

### **Data Entry**
- Always verify patient information
- Use auto-suggest for consistency
- Double-check prescription values
- Save work frequently

### **Patient Care**
- Maintain detailed visit notes
- Follow up on prescriptions
- Use try-on for better patient experience
- Keep inventory updated

### **System Maintenance**
- Regular backups
- Update software when available
- Monitor system performance
- Report issues promptly

---

## 🔄 Regular Tasks

### **Daily**
- Check patient appointments
- Review inventory levels
- Export prescriptions as needed
- Update patient records

### **Weekly**
- Review sales reports
- Update inventory
- Backup data
- Check system updates

### **Monthly**
- Generate reports
- Review system performance
- Update product catalog
- Staff training if needed

---

*This guide covers the essential features of MauEyeCare. For advanced features and customization, please contact your system administrator.*
