import streamlit as st
import cv2
import numpy as np
import pytesseract
import re
from datetime import datetime, timedelta

# Tesseract path
pytesseract.pytesseract.tesseract_cmd = r"C:\\Users\\PMLS\\Desktop\\Tesseract-OCR\\tesseract.exe"

# Dummy license DB
LICENSE_DB = {
    "34501-4814449-1": {"name": "Samar Abbas", "status": "Valid", "expiry": "2027-05-30"},
    "35201-1234567-8": {"name": "Ali Raza", "status": "Expired", "expiry": "2022-12-12"},
    "34602-6997069-9": {"name": "Abdul Rehman", "status": "Valid", "expiry": "2027-06-30"},
    "34501-4814449-2": {"name": "Awais Ali", "status": "Valid", "expiry": "2027-05-30"},
    "34501-4814449-3": {"name": "Afsar", "status": "Expired", "expiry": "2027-05-30"},
}

# Session state
if "scan_history" not in st.session_state:
    st.session_state.scan_history = []

# Config
st.set_page_config(page_title="Smart License Verifier", layout="centered", page_icon="🚦")

# --- Styles ---
st.markdown("""
<style>
body {
    background-color: #0f1117;
    font-family: 'Segoe UI', sans-serif;
}

.sidebar-box {
    background: rgba(0, 255, 255, 0.1);
    border: 2px solid #00ffe7;
    border-radius: 15px;
    box-shadow: 0 0 20px #00ffe7;
    padding: 20px;
    max-width: 100%;
}

.neon-badge {
    display: inline-block;
    background: linear-gradient(90deg, #00ffe7, #6a5acd);
    color: black;
    padding: 4px 10px;
    border-radius: 20px;
    font-weight: bold;
}

.feature-box {
    background: #111827;
    border-left: 4px solid #00ffe7;
    padding: 10px 15px;
    margin-top: 10px;
    border-radius: 8px;
    animation: glow 2s infinite;
}

@keyframes glow {
    0% { box-shadow: 0 0 5px #00ffe7; }
    50% { box-shadow: 0 0 15px #00ffe7; }
    100% { box-shadow: 0 0 5px #00ffe7; }
}

.title-container {
    text-align: center;
    padding-top: 10px;
}

.title-text {
    color: #00ffe7;
    font-size: 36px;
    font-weight: bold;
    line-height: 1.2;
    margin: 0;
}

.align-block {
    display: inline-block;
    text-align: left;
}

.verification-line {
    padding-left: 75px;
}

.subtitle-text {
    font-size: 18px;
    color: #cccccc;
    margin-top: 10px;
    margin-bottom: 50px;
    padding-left: 35px;
}

@media only screen and (max-width: 600px) {
    .title-text {
        font-size: 26px;
        line-height: 1.3;
    }
    .verification-line {
        padding-left: 30px;
    }
    .subtitle-text {
        font-size: 14px;
        padding-left: 15px;
        margin-bottom: 40px;
    }
    .sidebar-box, .feature-box {
        font-size: 14px;
    }
}
</style>
""", unsafe_allow_html=True)

# --- Sidebar ---
st.sidebar.markdown("""
<div class='sidebar-box'>
    <h3>📘 About the App</h3>
    <p>This futuristic system enables real-time license verification by scanning the citizen's CNIC using a webcam.</p>
    <ul>
        <li>🔍 OCR Extraction</li>
        <li>🕒 7-Day Grace Period</li>
        <li>📷 Live Scan + Manual Entry</li>
        <li>📄 Scan History</li>
        <li>✨ Futuristic UI</li>
    </ul>
    <br>
    <b>👨‍💻 Developer:</b> Samar Abbas<br>
    <b>🎓 University:</b> University of Narowal
</div>
""", unsafe_allow_html=True)

# --- Title ---
st.markdown("""
<div class="title-container">
    <div class="align-block">
        <div class="title-text">🚦 Smart Traffic License</div>
        <div class="title-text verification-line">Verification System</div>
    </div>
</div>
<div class="title-container">
    <p class="subtitle-text">Verify license via CNIC — with grace period logic and real-time detection.</p>
</div>
""", unsafe_allow_html=True)

# --- Webcam capture ---
def capture_image():
    cap = cv2.VideoCapture(0)
    st.info("📸 Press 's' to snap. Press 'q' to quit.")
    while True:
        ret, frame = cap.read()
        cv2.imshow("Webcam View", frame)
        key = cv2.waitKey(1)
        if key & 0xFF == ord('s'):
            cv2.imwrite("captured_cnic.jpg", frame)
            cap.release()
            cv2.destroyAllWindows()
            return "captured_cnic.jpg"
        elif key & 0xFF == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            return None

# --- OCR ---
def extract_cnic(image_path):
    image = cv2.imread(image_path)
    image = cv2.resize(image, None, fx=1.5, fy=1.5)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789-'
    text = pytesseract.image_to_string(thresh, config=config)
    match = re.search(r'\d{5}-\d{7}-\d', text)
    return match.group() if match else None

# --- Grace period calculator ---
def grace_expiry():
    return (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

# --- CNIC Scan via webcam ---
st.subheader("📸 CNIC Scanning via Webcam")
if st.button("📷 Start Live Scan"):
    path = capture_image()
    if path:
        cnic = extract_cnic(path)
        if cnic:
            st.success(f"✅ CNIC Detected: `{cnic}`")
        else:
            st.error("❌ Failed to detect CNIC.")
    else:
        st.info("❗ Scan canceled.")

# Space between sections
st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)

# --- Manual Entry ---
st.subheader("✏️ Or Enter CNIC Manually")
manual_cnic = st.text_input("Enter CNIC Number (xxxxx-xxxxxxx-x)")

# --- License Lookup ---
if st.button("🔍 Verify CNIC"):
    cnic_number = manual_cnic.strip()
    st.session_state.scan_history.append((cnic_number, datetime.now().strftime("%Y-%m-%d %H:%M")))

    if cnic_number in LICENSE_DB:
        info = LICENSE_DB[cnic_number]
        badge = "🟢 Valid" if info["status"] == "Valid" else "🔴 Expired"
        st.markdown(f"### 👤 Name: `{info['name']}`")
        st.markdown(f"### 🧾 Status: <span class='neon-badge'>{badge}</span>", unsafe_allow_html=True)
        st.markdown(f"### 📅 Expiry Date: `{info['expiry']}`")
        if info["status"] != "Valid":
            st.warning(f"⚠️ License expired. Grace Period Active till **{grace_expiry()}**.")
    else:
        st.error("❌ No license found. Grace period initiated.")
        st.markdown(f"📅 **Grace Valid Until:** `{grace_expiry()}`")

# --- History ---
if st.session_state.scan_history:
    st.markdown("### 🧾 CNIC Scan History")
    for i, (val, dt) in enumerate(reversed(st.session_state.scan_history[-5:]), 1):
        st.markdown(f"<div class='feature-box'>🔹 <b>{val}</b> — {dt}</div>", unsafe_allow_html=True)

# --- Footer ---
st.markdown("---")
st.caption("💡 Created by Samar Abbas | Powered by Streamlit, OpenCV & Tesseract OCR")
