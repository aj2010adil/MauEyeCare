#!/usr/bin/env python
"""
Doctor User Guide - Complete feature overview and instructions
"""
import streamlit as st
import datetime

def create_doctor_user_guide():
    """Create comprehensive user guide for doctors"""
    
    st.title("👨‍⚕️ MauEyeCare - Doctor User Guide")
    st.markdown("*Complete feature overview and step-by-step instructions*")
    
    # Quick navigation
    guide_sections = [
        "🚀 Quick Start",
        "📋 Patient Management", 
        "👓 Spectacle Features",
        "🤖 AI Tools",
        "📄 Reports & PDFs",
        "💬 WhatsApp Integration",
        "🔧 System Settings"
    ]
    
    selected_section = st.selectbox("Jump to Section:", guide_sections)
    
    if selected_section == "🚀 Quick Start":
        show_quick_start_guide()
    elif selected_section == "📋 Patient Management":
        show_patient_management_guide()
    elif selected_section == "👓 Spectacle Features":
        show_spectacle_features_guide()
    elif selected_section == "🤖 AI Tools":
        show_ai_tools_guide()
    elif selected_section == "📄 Reports & PDFs":
        show_reports_guide()
    elif selected_section == "💬 WhatsApp Integration":
        show_whatsapp_guide()
    elif selected_section == "🔧 System Settings":
        show_system_settings_guide()

def show_quick_start_guide():
    """Quick start guide for new users"""
    
    st.header("🚀 Quick Start Guide")
    
    st.markdown("""
    ### Welcome to MauEyeCare! 
    Follow these steps to get started:
    """)
    
    with st.expander("Step 1: Add Your First Patient", expanded=True):
        st.markdown("""
        1. Go to **"📋 Patient & Prescription"** tab
        2. Fill in patient details:
           - First Name, Last Name
           - Age, Gender, Mobile Number
           - Patient Issue (dropdown)
           - Advice/Notes (dropdown)
        3. Click **"💾 Save Patient"**
        """)
    
    with st.expander("Step 2: Capture Patient Photo"):
        st.markdown("""
        1. Go to **"🤖 AI Camera Analysis"** tab
        2. Click **"📷 Start Camera"**
        3. Position patient's face in frame
        4. Click **"📸 Capture"**
        5. AI will analyze face shape automatically
        """)
    
    with st.expander("Step 3: Get Spectacle Recommendations"):
        st.markdown("""
        1. After photo capture, AI provides recommendations
        2. View recommended spectacles based on face shape
        3. Check pricing in **"📄 Analysis Report"** tab
        4. Use **"🎯 Interactive Try-On"** to show patient options
        """)
    
    with st.expander("Step 4: Create Prescription"):
        st.markdown("""
        1. Fill RX table (OD/OS) with prescription details
        2. Add medical test results if needed
        3. Select medicines from inventory
        4. Click **"Generate PDF"** to create prescription
        """)
    
    st.success("🎉 You're ready to use MauEyeCare!")

def show_patient_management_guide():
    """Patient management features guide"""
    
    st.header("📋 Patient Management Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ✅ Available Features")
        features = [
            "Patient registration with complete details",
            "Medical history tracking",
            "Prescription history with dates",
            "Payment tracking (given/pending)",
            "Mobile number search",
            "Patient photo storage",
            "Eye test results recording",
            "Automatic patient ID generation"
        ]
        
        for feature in features:
            st.markdown(f"• {feature}")
    
    with col2:
        st.markdown("### 📝 How to Use")
        
        with st.expander("Add New Patient"):
            st.markdown("""
            1. **Patient & Prescription** tab
            2. Fill all required fields
            3. Select issue from dropdown
            4. Choose appropriate advice
            5. Click **Save Patient**
            """)
        
        with st.expander("Search Existing Patient"):
            st.markdown("""
            1. **Patient History** tab
            2. Search by mobile number or name
            3. Click on patient to view history
            4. See all previous prescriptions
            """)
        
        with st.expander("Update Patient Info"):
            st.markdown("""
            1. Search and select patient
            2. Modify details in form
            3. Save changes
            4. History is automatically updated
            """)

def show_spectacle_features_guide():
    """Spectacle features comprehensive guide"""
    
    st.header("👓 Spectacle Features")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "🖼️ Gallery", "🎯 Virtual Try-On", "🛍️ Product Pages", "💰 Pricing"
    ])
    
    with tab1:
        st.markdown("### 📦 Spectacle Gallery Features")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Available Collections:**")
            st.markdown("""
            • **Luxury Brands**: Ray-Ban, Oakley, Gucci, Prada
            • **Indian Brands**: Lenskart, Titan Eye Plus, Coolwinks
            • **Budget Options**: Specsmakers, Zenni Optical
            • **Specialty**: Progressive, Kids, Safety, Reading
            • **50+ Models** with real images and pricing
            """)
        
        with col2:
            st.markdown("**Filter Options:**")
            st.markdown("""
            • Category (Luxury, Mid-Range, Indian, Budget)
            • Price Range (₹1,200 - ₹28,000)
            • Brand selection
            • Shape (Rectangle, Round, Aviator, Cat-Eye)
            • Material (Metal, Acetate, Plastic, TR90)
            """)
    
    with tab2:
        st.markdown("### 🎯 Interactive Virtual Try-On")
        
        st.markdown("**How to Use:**")
        st.markdown("""
        1. **Capture patient photo** in AI Camera Analysis
        2. Go to **"🎯 Interactive Try-On"** tab
        3. **Browse spectacle gallery** with filters
        4. **Click "👓 Try On"** on any spectacle
        5. **See real-time overlay** on patient's face
        6. **Compare multiple options** side by side
        7. **Direct shopping actions** available
        """)
        
        st.markdown("**Features:**")
        st.markdown("""
        • Smart face detection and positioning
        • Material-based frame styling
        • Brand watermarks on images
        • Price display with breakdown
        • Instant product page access
        • Share and save options
        """)
    
    with tab3:
        st.markdown("### 🛍️ Professional Product Pages")
        
        st.markdown("**Similar to Fashion Eyewear website:**")
        st.markdown("""
        • **Multiple product views** (Front, Side, Top, Details)
        • **Complete specifications** with measurements
        • **Size options** (Small, Medium, Large)
        • **Color variants** available
        • **Lens type selection** (Single Vision, Progressive, Bifocal)
        • **Customer reviews** with ratings
        • **Related products** suggestions
        • **Add to cart** functionality
        • **Virtual try-on integration**
        """)
    
    with tab4:
        st.markdown("### 💰 Pricing Information")
        
        st.markdown("**Price Ranges (₹):**")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Budget**")
            st.markdown("₹1,200 - ₹5,000")
            st.markdown("• Specsmakers")
            st.markdown("• Local brands")
            st.markdown("• Basic materials")
        
        with col2:
            st.markdown("**Mid-Range**")
            st.markdown("₹5,000 - ₹15,000")
            st.markdown("• Lenskart")
            st.markdown("• Titan Eye Plus")
            st.markdown("• Warby Parker")
        
        with col3:
            st.markdown("**Luxury**")
            st.markdown("₹15,000 - ₹28,000")
            st.markdown("• Ray-Ban")
            st.markdown("• Gucci, Prada")
            st.markdown("• Premium materials")

def show_ai_tools_guide():
    """AI tools and features guide"""
    
    st.header("🤖 AI Tools & Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔍 Face Analysis AI")
        
        with st.expander("How Face Analysis Works"):
            st.markdown("""
            1. **Capture patient photo** using camera
            2. **AI detects face shape** automatically
            3. **Analyzes facial features** and proportions
            4. **Determines best spectacle shapes**
            5. **Provides confidence score**
            6. **Explains reasoning** for recommendations
            """)
        
        st.markdown("**Detected Face Shapes:**")
        st.markdown("""
        • **Wide/Round**: Rectangle, Square, Cat-Eye recommended
        • **Long/Oval**: Round, Aviator, Square recommended  
        • **Balanced/Square**: Round, Oval, Cat-Eye recommended
        """)
    
    with col2:
        st.markdown("### 🧠 AI Doctor Tools")
        
        with st.expander("Symptom Analysis"):
            st.markdown("""
            • **AI-powered diagnosis** suggestions
            • **Treatment recommendations**
            • **When to seek immediate care**
            • **Based on age, gender, symptoms**
            """)
        
        with st.expander("Medication Suggestions"):
            st.markdown("""
            • **First-line medications** with dosages
            • **Alternative options** available
            • **Duration of treatment**
            • **Important precautions**
            """)
        
        with st.expander("Drug Interaction Check"):
            st.markdown("""
            • **Checks medication interactions**
            • **Timing recommendations**
            • **Safety precautions**
            • **Monitoring requirements**
            """)

def show_reports_guide():
    """Reports and PDF generation guide"""
    
    st.header("📄 Reports & PDF Generation")
    
    tab1, tab2, tab3 = st.tabs(["📋 Prescriptions", "📊 Analysis Reports", "📱 WhatsApp Sharing"])
    
    with tab1:
        st.markdown("### 📋 Prescription PDFs")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**What's Included:**")
            st.markdown("""
            • **Patient information** (name, age, contact)
            • **RX table** (OD/OS specifications)
            • **Medicine list** with quantities
            • **Dosage instructions**
            • **Doctor details** and signature
            • **Hospital branding**
            • **Date and prescription ID**
            """)
        
        with col2:
            st.markdown("**How to Generate:**")
            st.markdown("""
            1. Complete patient form
            2. Fill RX table details
            3. Select medicines from inventory
            4. Add dosage instructions
            5. Click **"Generate PDF"**
            6. Download or share via WhatsApp
            """)
    
    with tab2:
        st.markdown("### 📊 Analysis Reports")
        
        st.markdown("**Comprehensive Analysis Includes:**")
        st.markdown("""
        • **Face shape analysis** with confidence score
        • **Recommended spectacles** with images
        • **Pricing table** in ₹ with breakdown
        • **Virtual try-on images** showing patient wearing spectacles
        • **Detailed specifications** for each recommendation
        • **Delivery information** and availability
        """)
    
    with tab3:
        st.markdown("### 📱 WhatsApp Integration")
        
        st.markdown("**Available Actions:**")
        st.markdown("""
        • **Send prescription PDFs** directly to patients
        • **Share analysis reports** with images
        • **Send appointment reminders**
        • **Follow-up messages** with care instructions
        • **Automatic formatting** for Indian mobile numbers
        """)

def show_whatsapp_guide():
    """WhatsApp integration guide"""
    
    st.header("💬 WhatsApp Integration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📱 Features Available")
        
        st.markdown("**Send to Patients:**")
        st.markdown("""
        • **Prescription PDFs** with complete details
        • **Analysis reports** with spectacle recommendations
        • **Appointment confirmations**
        • **Follow-up care instructions**
        • **Medication reminders**
        """)
        
        st.markdown("**Automatic Features:**")
        st.markdown("""
        • **Phone number formatting** (adds +91 for India)
        • **Professional message templates**
        • **Delivery confirmations**
        • **Error handling** and retry logic
        """)
    
    with col2:
        st.markdown("### ⚙️ Setup Requirements")
        
        with st.expander("WhatsApp Business API Setup"):
            st.markdown("""
            **Required Configuration:**
            • WhatsApp Business Account
            • Meta Developer Account
            • Access Token
            • Phone Number ID
            • Webhook Configuration
            
            **Contact admin for setup assistance**
            """)
        
        st.markdown("**Usage:**")
        st.markdown("""
        1. Generate prescription PDF
        2. Click **"📱 Send via WhatsApp"**
        3. Enter patient mobile number
        4. Message sent automatically
        5. Delivery confirmation received
        """)

def show_system_settings_guide():
    """System settings and configuration guide"""
    
    st.header("🔧 System Settings & Configuration")
    
    tab1, tab2, tab3, tab4 = st.tabs(["🗄️ Database", "📦 Inventory", "🌐 Updates", "🚀 Future Enhancements"])
    
    with tab1:
        st.markdown("### 🗄️ Database Management")
        
        st.markdown("**Current Database Stats:**")
        
        # Show actual stats if available
        try:
            from modules.comprehensive_spectacle_database import COMPREHENSIVE_SPECTACLE_DATABASE
            total_specs = len(COMPREHENSIVE_SPECTACLE_DATABASE)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Spectacles", total_specs)
            
            with col2:
                budget_count = len([s for s in COMPREHENSIVE_SPECTACLE_DATABASE.values() if s['price'] <= 5000])
                st.metric("Budget Options", budget_count)
            
            with col3:
                luxury_count = len([s for s in COMPREHENSIVE_SPECTACLE_DATABASE.values() if s['price'] > 15000])
                st.metric("Luxury Options", luxury_count)
        
        except:
            st.info("Database stats will appear when system is running")
        
        st.markdown("**Maintenance:**")
        st.markdown("""
        • **Automatic backups** daily
        • **Patient data encryption**
        • **HIPAA compliance** features
        • **Data export** options available
        """)
    
    with tab2:
        st.markdown("### 📦 Inventory Management")
        
        st.markdown("**Features:**")
        st.markdown("""
        • **Real-time stock tracking**
        • **Low stock alerts** (< 10 items)
        • **Automatic reorder suggestions**
        • **Market price updates**
        • **Supplier information**
        """)
        
        st.markdown("**How to Update:**")
        st.markdown("""
        1. Go to **Spectacle Gallery** tab
        2. Click **"🔄 Load Complete Database"**
        3. Or click **"🌐 Update from Web"**
        4. System fetches latest prices
        5. Inventory updated automatically
        """)
    
    with tab3:
        st.markdown("### 🌐 System Updates")
        
        st.markdown("**Available Updates:**")
        st.markdown("""
        • **Web scraping** from eyewear websites
        • **Price synchronization** with market rates
        • **New product additions** from suppliers
        • **Feature updates** and improvements
        """)
        
        st.markdown("**Update Schedule:**")
        st.markdown("""
        • **Daily**: Price updates from web sources
        • **Weekly**: New product additions
        • **Monthly**: Feature updates and improvements
        • **Quarterly**: Major system upgrades
        """)
    
    with tab4:
        show_future_enhancements_guide()

def create_feature_overview_page():
    """Create complete feature overview page"""
    
    st.title("🏥 MauEyeCare - Complete Feature Overview")
    st.markdown("*All-in-one AI-powered optical center management system*")
    
    # Feature categories
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 👥 Patient Management")
        st.markdown("""
        ✅ Patient registration & history
        ✅ Medical test tracking
        ✅ Prescription management
        ✅ Payment tracking
        ✅ Mobile search functionality
        """)
    
    with col2:
        st.markdown("### 👓 Spectacle Features")
        st.markdown("""
        ✅ 50+ spectacle models
        ✅ Real product images
        ✅ Professional product pages
        ✅ Interactive virtual try-on
        ✅ Price comparison (₹1,200-₹28,000)
        """)
    
    with col3:
        st.markdown("### 🤖 AI Integration")
        st.markdown("""
        ✅ Face shape analysis
        ✅ Smart recommendations
        ✅ Symptom analysis
        ✅ Drug interaction checks
        ✅ Automated PDF generation
        """)
    
    # Technical specifications
    st.markdown("---")
    st.markdown("### 🔧 Technical Specifications")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**System Requirements:**")
        st.markdown("""
        • Python 3.11+
        • Streamlit framework
        • OpenCV for image processing
        • SQLite database
        • Internet connection for updates
        """)
    
    with col2:
        st.markdown("**Supported Features:**")
        st.markdown("""
        • Multi-language PDF support
        • WhatsApp Business API integration
        • Real-time web scraping
        • Cloud deployment ready
        • Mobile-responsive interface
        """)
    
    # Contact information
    st.markdown("---")
    st.markdown("### 📞 Support & Contact")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Technical Support**")
        st.markdown("📧 tech@maueyecare.com")
        st.markdown("📞 +91 92356-47410")
    
    with col2:
        st.markdown("**Training & Setup**")
        st.markdown("📧 training@maueyecare.com")
        st.markdown("🕒 Mon-Fri 9AM-6PM")
    
    with col3:
        st.markdown("**Emergency Support**")
        st.markdown("📞 +91 92356-47410")
        st.markdown("🚨 24/7 Available")
    
    # Version information
    st.markdown("---")
    st.info(f"**Version:** 2.0.0 | **Last Updated:** {datetime.datetime.now().strftime('%B %Y')} | **Build:** Production")

def show_future_enhancements_guide():
    """Show future enhancements and roadmap"""
    
    st.markdown("### 🚀 Future Enhancements & Roadmap")
    st.markdown("*Planned features and improvements for MauEyeCare system*")
    
    # Development phases
    phase1, phase2, phase3 = st.tabs(["📱 Phase 1: Core", "🔗 Phase 2: Integration", "🤖 Phase 3: Advanced"])
    
    with phase1:
        st.markdown("### 📱 Phase 1: Core Enhancements (1-2 weeks)")
        
        enhancements = [
            {"feature": "📧 Email Integration", "description": "Send prescriptions via email to patients", "priority": "High"},
            {"feature": "📅 Appointment System", "description": "Basic scheduling and calendar functionality", "priority": "High"},
            {"feature": "🔔 SMS Notifications", "description": "Automated reminders and follow-ups", "priority": "Medium"},
            {"feature": "📈 Basic Reports", "description": "Daily/monthly clinic summaries", "priority": "Medium"},
            {"feature": "🖼️ Real Medicine Images", "description": "Add actual product images to medicine database", "priority": "Low"}
        ]
        
        for item in enhancements:
            priority_color = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}[item["priority"]]
            st.markdown(f"**{item['feature']}** {priority_color}")
            st.markdown(f"*{item['description']}*")
            st.markdown("")
    
    with phase2:
        st.markdown("### 🔗 Phase 2: Integration (2-3 weeks)")
        
        integrations = [
            {"feature": "🏪 Pharmacy API Integration", "description": "Real-time pricing from 1mg, Netmeds, PharmEasy", "benefit": "Live price updates"},
            {"feature": "💳 Payment Gateway", "description": "Razorpay/Paytm integration for online payments", "benefit": "Digital transactions"},
            {"feature": "🏦 Insurance Processing", "description": "Direct insurance claim submissions", "benefit": "Streamlined billing"},
            {"feature": "☁️ Cloud Deployment", "description": "AWS/Azure hosting with auto-scaling", "benefit": "Better performance"},
            {"feature": "🔐 Enhanced Security", "description": "2FA, encryption, audit trails", "benefit": "Data protection"}
        ]
        
        for item in integrations:
            st.markdown(f"**{item['feature']}**")
            st.markdown(f"*{item['description']}*")
            st.success(f"✅ Benefit: {item['benefit']}")
            st.markdown("")
    
    with phase3:
        st.markdown("### 🤖 Phase 3: Advanced Features (3-4 weeks)")
        
        advanced_features = [
            {"feature": "📱 Mobile App", "description": "React Native app for patients with virtual try-on", "impact": "High"},
            {"feature": "📊 Analytics Dashboard", "description": "Business intelligence and performance metrics", "impact": "High"},
            {"feature": "🏥 Multi-clinic Support", "description": "Manage multiple clinic locations", "impact": "Medium"},
            {"feature": "🤖 AI Chatbot", "description": "Automated patient query handling", "impact": "Medium"},
            {"feature": "📄 OCR Integration", "description": "Scan and digitize paper prescriptions", "impact": "Low"}
        ]
        
        for item in advanced_features:
            impact_color = {"High": "🚀", "Medium": "⚡", "Low": "💡"}[item["impact"]]
            st.markdown(f"**{item['feature']}** {impact_color}")
            st.markdown(f"*{item['description']}*")
            st.markdown("")
    
    # Quick wins section
    st.markdown("---")
    st.markdown("### 💡 Quick Wins (Immediate Implementation)")
    
    quick_wins = [
        "📧 **Email Prescriptions**: Send PDFs directly to patient email",
        "📅 **Basic Scheduling**: Simple appointment booking system",
        "🔍 **Global Search**: Search across patients, medicines, spectacles",
        "📱 **QR Codes**: Generate QR codes for prescriptions",
        "📊 **Export Data**: CSV/Excel export for reports"
    ]
    
    for win in quick_wins:
        st.markdown(f"• {win}")
    
    # Implementation timeline
    st.markdown("---")
    st.markdown("### 📅 Implementation Timeline")
    
    timeline_data = {
        "Week 1-2": "Email integration, Appointment system, SMS notifications",
        "Week 3-4": "Pharmacy APIs, Payment gateway, Basic reports",
        "Week 5-6": "Cloud deployment, Security enhancements, Mobile app start",
        "Week 7-8": "Analytics dashboard, Multi-clinic support",
        "Week 9-10": "AI features, OCR integration, Advanced analytics",
        "Week 11-12": "Testing, optimization, production deployment"
    }
    
    for week, tasks in timeline_data.items():
        st.markdown(f"**{week}**: {tasks}")
    
    # Priority voting
    st.markdown("---")
    st.markdown("### 🗳️ Feature Priority Voting")
    st.markdown("*Help us prioritize which features to implement first*")
    
    priority_features = [
        "📧 Email Integration",
        "📅 Appointment System", 
        "💳 Payment Gateway",
        "📱 Mobile App",
        "📊 Analytics Dashboard",
        "🏪 Pharmacy API Integration"
    ]
    
    selected_priority = st.selectbox("Which feature would benefit your clinic most?", priority_features)
    
    if st.button("🗳️ Submit Vote"):
        st.success(f"Thank you! Your vote for '{selected_priority}' has been recorded.")
        st.info("We'll prioritize development based on doctor feedback.")