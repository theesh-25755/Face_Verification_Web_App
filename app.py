from flask import Flask, render_template, Response, request, redirect, url_for, flash
import cv2
import face_recognition
import numpy as np
import os
from datetime import datetime
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = "supersecretkey"  #  for login sessions

# configuration
IMAGE_FOLDER = 'images'
ADMIN_EMAIL = "admin@kdu.ac.lk"
ADMIN_PASSWORD = "123"  # Simple hardcoded password for now

# mongodb connection
client = MongoClient("mongodb://localhost:27017/")
db = client['attendance_db']  # Create a database named 'attendance_db'
attendance_collection = db['logs']  # Collection for logs

# global variables
camera = None
known_face_encodings = []
known_face_names = []

# load faces function
def load_known_faces():
    global known_face_encodings, known_face_names
    known_face_encodings = []
    known_face_names = []
    
    if not os.path.exists(IMAGE_FOLDER):
        os.makedirs(IMAGE_FOLDER)
        
    print("[INFO] Loading faces from disk...")
    for filename in os.listdir(IMAGE_FOLDER):
        if filename.startswith('.'): continue
        
        filepath = os.path.join(IMAGE_FOLDER, filename)
        img = cv2.imread(filepath)
        if img is None: continue
        
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        try:
            encoding = face_recognition.face_encodings(img)[0]
            known_face_encodings.append(encoding)
            # Filename changes
            known_face_names.append(os.path.splitext(filename)[0])
        except IndexError:
            print(f"[WARN] No face found in {filename}")
            
load_known_faces()

# camera generator
def gen_frames(is_registering=False, new_name=""):
    global camera
    camera = cv2.VideoCapture(0)
    
    while True:
        success, frame = camera.read()
        if not success:
            break
            
        if not is_registering:
            # verification
            # Resize for speed
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            
            # Find faces
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
            
            for face_encoding, face_location in zip(face_encodings, face_locations):
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.50)
                name = "Unknown"
                color = (0, 0, 255) # Red for unknown

                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                if len(face_distances) > 0:
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = known_face_names[best_match_index].upper()
                        color = (0, 255, 0) # Green for match
                        
                        # mongodb logging
                       
                        log_entry = {
                            "name": name,
                            "timestamp": datetime.now()
                        }
                        # Only insert if not logged in the last 60 seconds 
                        last_log = attendance_collection.find_one(
                            {"name": name}, 
                            sort=[("timestamp", -1)]
                        )
                        
                        should_log = True
                        if last_log:
                            time_diff = (datetime.now() - last_log['timestamp']).total_seconds()
                            if time_diff < 60: # 60 seconds debounce
                                should_log = False
                        
                        if should_log:
                            attendance_collection.insert_one(log_entry)
                            print(f"[DB] Logged {name} to MongoDB")

                # Draw Box
                top, right, bottom, left = face_location
                top, right, bottom, left = top*4, right*4, bottom*4, left*4
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)

        else:
            # registration mode
            # Just show the raw camera so the user can position themselves
            cv2.putText(frame, "Position Face & Click Capture", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

        # Encode frame to JPG for browser streaming
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

# routes

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/verify_feed')
def verify_feed():
    return Response(gen_frames(is_registering=False), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/verify')
def verify():
    return render_template('verify.html') 

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            return redirect(url_for('register_page'))
        else:
            return "<h3>Incorrect Password! <a href='/login'>Try Again</a></h3>"
    return render_template('login.html')

@app.route('/register_page')
def register_page():
    return render_template('register.html')

@app.route('/register_feed')
def register_feed():
    return Response(gen_frames(is_registering=True), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/capture_face', methods=['POST'])
def capture_face():
    # This captures the current frame from the camera
    name = request.form['student_name']
    s_id = request.form['student_id']
    
    if camera and camera.isOpened():
        ret, frame = camera.read()
        if ret:
            filename = f"{name}_{s_id}.jpg"
            path = os.path.join(IMAGE_FOLDER, filename)
            cv2.imwrite(path, frame)
            
            # Reload the database of faces
            load_known_faces()
            return f"<h3>Success! Saved {name}. <a href='/'>Go Home</a></h3>"
            
    return "Failed to capture."

@app.route('/dashboard')
def dashboard():
    #  Fetch all logs from MongoDB, sorted by newest first
    logs = attendance_collection.find().sort("timestamp", -1)
    
    # Send them to the HTML page
    return render_template('dashboard.html', logs=logs)

if __name__ == '__main__':
    app.run(debug=True, port=5001)