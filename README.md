
# Face Verification Attendance System 

A full-stack biometric attendance system developed for the **Digital Image Processing (CS31092)** module. This application uses **Computer Vision** to verify student identities in real-time and logs attendance to a local **MongoDB** database.

## 🚀 Features
* **Web Interface:** User-friendly Dashboard built with **Flask** (Python) and modern CSS.
* **Real-Time Verification:** Uses **OpenCV** & **Face Recognition** (HOG/CNN) to detect and verify faces via webcam.
* **Image Processing:** Applies **Histogram Equalization** to normalize lighting conditions before detection.
* **Database Integration:** Automates logging of Student Name, Date, and Time into **MongoDB** (NoSQL).
* **Admin Panel:** Secure login (`admin@kdu.ac.lk`) for administrators to register new students.
* **Session Logic:** Intelligent logging that prevents duplicate attendance entries within a 60-second window.
* **Live Dashboard:** View real-time attendance logs directly on the web interface.

## 🛠️ Tech Stack
* **Language:** Python 3.13
* **Backend:** Flask (Web Framework)
* **Computer Vision:** OpenCV, Dlib, Face_Recognition
* **Database:** MongoDB Community Edition (NoSQL)
* **Frontend:** HTML5, CSS3 (Card UI Design)
* **Hardware Support:** Optimized for Apple Silicon (M1/M2) using AVFoundation.

## ⚙️ Installation & Setup

### 1. Prerequisites
* Python 3.10 or higher
* MongoDB installed and running locally
* CMake (required for dlib)

### 2. Install Dependencies
Run the following command to install required libraries:
```bash
pip install flask pymongo opencv-python face-recognition numpy

```

### 3. Database Setup

Ensure your local MongoDB service is running on your Mac:

```bash
brew services start mongodb-community@7.0

```

### 4. Run the Application

Start the Flask server:

```bash
python3 app.py

```

Access the application in your browser at: `http://127.0.0.1:5001`

## 📖 Usage Guide

1. **Home Page:** Choose between "Mark Attendance", "Admin Login", or "View Logs".
2. **Registration:**
* Log in as Admin (Email: `admin@kdu.ac.lk`, Password: `123`).
* Enter the student's Name and ID.
* Align the student's face with the camera and click **Capture**.


3. **Verification:**
* Go to the **Verify** page.
* Look at the camera. A **Green Box** indicates a successful match and attendance is logged.
* A **Red Box** indicates an "Unknown" user.


4. **View Logs:**
* Click "View Logs" to see the real-time table of all students who have attended today.



## 📂 Project Structure

```
Face_Verification_Web_App/
├── app.py              # Main Flask Application (Backend Logic)
├── images/             # Folder storing known face images (Training Data)
├── templates/          # HTML Interface Files
│   ├── index.html      # Home Landing Page
│   ├── verify.html     # Camera Verification Interface
│   ├── register.html   # Admin Registration Interface
│   ├── login.html      # Admin Login Page
│   └── dashboard.html  # Attendance Log Table
└── static/
    └── style.css       # CSS Styling (Modern UI)



