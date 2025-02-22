import cv2
import numpy as np
from ultralytics import YOLO
from flask import Flask, request
import requests
import base64
from io import BytesIO

# Flask app initialization
app = Flask(__name__)

# Configuration
CAMERA_ID = "cam1"  # Change this for different cameras
DETECTION_SERVER_URL = "http://localhost:3000/api/detection"

def encode_frame_to_base64(frame):
    """Convert frame to base64 string"""
    _, buffer = cv2.imencode('.jpg', frame)
    return base64.b64encode(buffer).decode('utf-8')

def send_detection(frame, camera_id):
    """Send POST request with detection data"""
    try:
        payload = {
            "cip": camera_id,
            "image": encode_frame_to_base64(frame),
            "isimp": False
        }
        response = requests.post(DETECTION_SERVER_URL, json=payload)
        return response.status_code == 200
    except Exception as e:
        print(f"Error sending detection: {e}")
        return False

def get_dark_channel(img, size=15):
    """Get dark channel prior"""
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (size, size))
    dark = cv2.erode(np.min(img, axis=2), kernel)
    return dark

def estimate_atmospheric_light(img, dark_channel):
    """Estimate atmospheric light"""
    h, w = dark_channel.shape
    n_pixels = h * w
    n_search = int(max(n_pixels * 0.001, 1))
    
    dark_vec = dark_channel.reshape(n_pixels)
    img_vec = img.reshape(n_pixels, 3)
    
    indices = dark_vec.argsort()[-n_search:]
    return np.max(img_vec[indices], axis=0)

def estimate_transmission(img, A, size=15, omega=0.95):
    """Estimate transmission map"""
    normalized = img / A
    transmission = 1 - omega * get_dark_channel(normalized, size)
    return transmission

def guided_filter(img, p, r, eps):
    """Edge-preserving guided filter"""
    mean_I = cv2.boxFilter(img, -1, (r, r))
    mean_p = cv2.boxFilter(p, -1, (r, r))
    mean_Ip = cv2.boxFilter(img * p, -1, (r, r))
    cov_Ip = mean_Ip - mean_I * mean_p
    
    mean_II = cv2.boxFilter(img * img, -1, (r, r))
    var_I = mean_II - mean_I * mean_I
    
    a = cov_Ip / (var_I + eps)
    b = mean_p - a * mean_I
    
    mean_a = cv2.boxFilter(a, -1, (r, r))
    mean_b = cv2.boxFilter(b, -1, (r, r))
    
    return mean_a * img + mean_b

def dehaze(img):
    """Dehaze image using Dark Channel Prior"""
    # Normalize image
    normalized = img.astype('float32') / 255.0
    
    # Get dark channel prior
    dark_channel = get_dark_channel(normalized)
    
    # Estimate atmospheric light
    A = estimate_atmospheric_light(normalized, dark_channel)
    
    # Estimate transmission map
    transmission = estimate_transmission(normalized, A)
    
    # Refine transmission map
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype('float32') / 255.0
    refined_transmission = guided_filter(gray, transmission, r=40, eps=1e-3)
    
    # Ensure minimum transmission for stability
    transmission = cv2.max(refined_transmission, 0.1)
    
    # Recover scene radiance
    result = np.empty_like(normalized)
    for i in range(3):
        result[:, :, i] = (normalized[:, :, i] - A[i]) / transmission + A[i]
    
    # Clip and convert back to uint8
    return np.clip(result * 255, 0, 255).astype('uint8')

def enhance_image(img):
    """Enhance image using dehazing and CLAHE"""
    # Dehaze
    dehazed = dehaze(img)
    
    # Apply CLAHE
    lab = cv2.cvtColor(dehazed, cv2.COLOR_BGR2LAB)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    lab[:,:,0] = clahe.apply(lab[:,:,0])
    enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    
    return enhanced

# Load YOLO model
model = YOLO("yolo12n.pt")

url = "http://192.168.137.71:8080/video"

# For webcam feed
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Process frame
    processed_frame = enhance_image(frame)
    
    # Run YOLO detection
    results = model(processed_frame, stream=True)
    
    person_detected = False
    # Draw results
    for r in results:
        boxes = r.boxes
        for box in boxes:
            # Check if detection is person (class 0 in COCO dataset)
            if box.cls[0] == 0:  # person class
                person_detected = True
                # Get the region of the detected person
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                person_frame = processed_frame[y1:y2, x1:x2]
                if person_frame.size > 0:  # Check if crop is valid
                    send_detection(person_frame, CAMERA_ID)
        
        annotated_frame = r.plot()
        cv2.imshow('Enhanced Detection', annotated_frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()