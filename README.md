# MauEyeCare - Professional Eye Care Clinic Management System

MauEyeCare is a comprehensive, production-grade clinic management system designed for ophthalmology and optometry practices. It runs entirely on a local Windows 11 machine, ensuring data privacy and fast performance, while being accessible from any device on the same network.

## 📋 Features

- **One-Click Windows Setup**: A simple PowerShell script installs all dependencies and configures the system.
- **Secure Local Data**: All patient and clinic data is stored securely in a local PostgreSQL database.
- **Patient & Visit Management**: Track patient history, manage multiple visits, and record detailed eye-care data.
- **Professional PDF Prescriptions**: Generate, save, and manage beautiful prescription PDFs, automatically organized by date.
- **Mobile-Friendly**: Doctors and staff can use the app on tablets or phones within the clinic's Wi-Fi network.
- **Role-Based Access**: Secure login for Admins, Doctors, and Staff with different permissions.
- **Dashboards & Insights**: Get a real-time view of clinic operations and marketing performance.
- **Inventory Tracking**: Manage spectacle frames and other inventory.

## 🔧 System Requirements

- Windows 11
- An active internet connection (for the initial setup only)
- Administrator access to run the setup script

## 🚀 Installation and First-Time Setup

Follow these steps to get MauEyeCare running on your computer. This only needs to be done once.

1.  **Download the Project**
    - Download the project files as a ZIP from the source repository and extract it to a known location (e.g., your Desktop).

2.  **Run the Setup Script**
    - Right-click the Windows Start button and select **Terminal (Admin)** or **Windows PowerShell (Admin)**.
    - In the terminal window, navigate to the project folder. For example, if it's on your Desktop, type:
      ```powershell
      cd $env:USERPROFILE\Desktop\MauEyeCare
      ```
    - Now, run the setup script. This will install all required software like Python, Node.js, and PostgreSQL automatically.
      ```powershell
      Set-ExecutionPolicy Bypass -Scope Process -Force; .\setup.ps1
      ```
    - The script will show its progress and may take 10-15 minutes to complete.

3.  **Setup is Complete!**
    - Once finished, the system is ready with a default **Doctor** user:
      - **Email**: `doctor@maueyecare.com`
      - **Password**: `MauEyeCareAdmin@2024`
    - Please change this password after your first login via the Settings page.

---

## ▶️ How to Run the Application

1.  Open a new PowerShell or Terminal window (it does not need to be Admin).
2.  Navigate to the project folder:
    ```powershell
    cd $env:USERPROFILE\Desktop\MauEyeCare
    ```
3.  Run the start script:
    ```powershell
    .\run.ps1
    ```
4.  The backend and frontend servers will start. Keep this window open while using the application.

---

## 💻 Accessing the Application

### From Your Laptop
Open your web browser (Chrome, Edge, Firefox) and go to:
**<http://localhost:5173>**

### From a Mobile or Tablet (on the same Wi-Fi)
To use the app on a mobile device, you need your laptop's Local Network (LAN) IP Address.

1.  **Find your Laptop's IP Address**:
    - The `run.ps1` script attempts to print this IP address for you when it starts.
    - Alternatively, on your laptop, open a new Terminal window, type `ipconfig`, and press Enter.
    - Look for the "Wireless LAN adapter Wi-Fi" section and find the `IPv4 Address`. It will look something like `192.168.1.15`.

2.  **Access from Mobile**:
    - On your mobile device's web browser, type `http://` followed by the IP address and the port `:5173`.
    - Example: **`http://192.168.1.15:5173`**

> **Note**: Your mobile device and laptop must be connected to the same Wi-Fi network. If you can't connect, ensure your Wi-Fi connection is set to "Private" in Windows network settings. The setup script adds a firewall rule for this profile automatically.

---

## 🩺 Troubleshooting

If you encounter any issues, use the built-in diagnostic script:

1.  Open a new **Terminal (Admin)**.
2.  Navigate to the project folder.
3.  Run the diagnose script:
    ```powershell
    .\scripts\diagnose.ps1
    ```
4.  To attempt automatic fixes for common problems:
    ```powershell
    .\scripts\diagnose.ps1 -FixCommon
    ```