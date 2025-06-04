from flask import Flask, render_template, request
import os
import base64
import json
import re
import face_recognition
from datetime import datetime

app = Flask(__name__)

FACE_DIR = "static/faces"
USER_DB = "users.json"

os.makedirs(FACE_DIR, exist_ok=True)

def load_users():
    if not os.path.exists(USER_DB):
        return []
    with open(USER_DB, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(USER_DB, 'w') as f:
        json.dump(users, f, indent=2)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        data = request.get_json()
        name = data['name']
        mobile = data['mobile']
        img_data = data['image']

        # Decode base64 image
        img_str = re.search(r'base64,(.*)', img_data).group(1)
        img_bytes = base64.b64decode(img_str)

        filename = f"{name}_{mobile}.jpg"
        path = os.path.join(FACE_DIR, filename)
        with open(path, 'wb') as f:
            f.write(img_bytes)

        users = load_users()
        # Prevent duplicate signup (optional)
        for u in users:
            if u['mobile'] == mobile:
                return "Mobile number already registered!", 400

        users.append({
            "name": name,
            "mobile": mobile,
            "face_image": filename
        })
        save_users(users)
        return "Signup successful with face captured!"

    return render_template('signup.html')

@app.route('/attendance', methods=['GET', 'POST'])
def attendance():
    if request.method == 'POST':
        data = request.get_json()
        img_data = data['image']
        img_str = re.search(r'base64,(.*)', img_data).group(1)
        img_bytes = base64.b64decode(img_str)

        # Save temp image
        temp_img_path = os.path.join(FACE_DIR, "temp_attendance.jpg")
        with open(temp_img_path, 'wb') as f:
            f.write(img_bytes)

        unknown_img = face_recognition.load_image_file(temp_img_path)
        unknown_encodings = face_recognition.face_encodings(unknown_img)
        if len(unknown_encodings) == 0:
            return "No face detected in attendance photo.", 400
        unknown_encoding = unknown_encodings[0]

        users = load_users()
        for user in users:
            user_img_path = os.path.join(FACE_DIR, user["face_image"])
            known_img = face_recognition.load_image_file(user_img_path)
            known_encodings = face_recognition.face_encodings(known_img)
            if not known_encodings:
                continue
            known_encoding = known_encodings[0]
            matches = face_recognition.compare_faces([known_encoding], unknown_encoding)
            if matches[0]:
                return f"✅ Attendance marked for {user['name']} ({user['mobile']}) at {datetime.now()}"

        return "❌ Face not recognized. Please try again.", 400

    return render_template('attendance.html')

if __name__ == "__main__":
    app.run(debug=True)
