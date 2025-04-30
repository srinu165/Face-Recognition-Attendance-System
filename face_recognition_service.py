import os
import cv2
import numpy as np
from PIL import Image
import pickle
import time
from config import MODELS_DIR, FACES_DIR

# Ensure directory exists
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(FACES_DIR, exist_ok=True)

# Path to the haar cascade file for face detection
HAAR_CASCADE_PATH = os.path.join(MODELS_DIR, "haarcascade_frontalface_default.xml")

# Download cascade file if it doesn't exist
if not os.path.exists(HAAR_CASCADE_PATH):
    import urllib.request
    print("Downloading haar cascade file...")
    urllib.request.urlretrieve(
        "https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml",
        HAAR_CASCADE_PATH
    )

# Global variables
face_cascade = None
face_recognizer = None
FACE_SIZE = (200, 200)  # Standard size for face images

def load_models():
    """Load haar cascade and initialize face recognizer"""
    global face_cascade, face_recognizer
    
    try:
        # Load haar cascade for face detection
        face_cascade = cv2.CascadeClassifier(HAAR_CASCADE_PATH)
        
        # Load or create face recognizer
        face_recognizer = cv2.face.LBPHFaceRecognizer_create()
        
        # Try to load existing model if available
        recognizer_path = os.path.join(MODELS_DIR, "face_recognizer.yml")
        if os.path.exists(recognizer_path):
            face_recognizer.read(recognizer_path)
            print("Face recognition model loaded successfully.")
        else:
            print("No face recognition model found. Will create one when training.")
        
        return True
    except Exception as e:
        print(f"Error loading models: {e}")
        return False

def detect_faces(frame):
    """Detect faces in a frame and return coordinates"""
    if face_cascade is None:
        load_models()
    
    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Detect faces
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.3,
        minNeighbors=5,
        minSize=(30, 30)
    )
    
    return faces, gray

def take_face_images(student_id, student_name, num_images=20):
    """Capture multiple face images for a student"""
    if face_cascade is None:
        load_models()
    
    # Create directory for this student
    student_dir = os.path.join(FACES_DIR, f"{student_id}_{student_name}")
    os.makedirs(student_dir, exist_ok=True)
    
    # Initialize camera
    cap = cv2.VideoCapture(0)
    
    # Counter for number of images
    count = 0
    
    print(f"Taking {num_images} pictures. Please look at the camera...")
    
    while count < num_images:
        ret, frame = cap.read()
        if not ret:
            print("Error capturing image")
            break
        
        # Detect faces
        faces, gray = detect_faces(frame)
        
        for (x, y, w, h) in faces:
            # Draw rectangle around face
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            # Crop and save face
            face_img = gray[y:y+h, x:x+w]
            face_img_resized = cv2.resize(face_img, FACE_SIZE)
            
            # Save image
            img_path = os.path.join(student_dir, f"{count}.jpg")
            cv2.imwrite(img_path, face_img_resized)
            count += 1
            
            # Show progress
            cv2.putText(
                frame, 
                f"Captured: {count}/{num_images}", 
                (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                1, 
                (0, 255, 0), 
                2
            )
        
        # Display frame
        cv2.imshow('Face Registration', frame)
        
        # Break loop if ESC pressed
        if cv2.waitKey(100) & 0xFF == 27:
            break
        
        # Slight delay to not take images too quickly
        time.sleep(0.2)
    
    # Release camera and close windows
    cap.release()
    cv2.destroyAllWindows()
    
    return count

def train_model():
    """Train face recognition model with all registered faces"""
    if face_recognizer is None:
        load_models()
    
    # Lists for training data
    faces = []
    labels = []
    label_map = {}
    
    # Counter for assigning numeric labels
    label_counter = 0
    
    # Go through all student directories
    for student_dir in os.listdir(FACES_DIR):
        if os.path.isdir(os.path.join(FACES_DIR, student_dir)):
            # Extract student ID from directory name
            student_id = student_dir.split('_')[0]
            
            # Assign a numeric label for this student
            if student_id not in label_map:
                label_map[student_id] = label_counter
                label_counter += 1
            
            # Process all images for this student
            student_path = os.path.join(FACES_DIR, student_dir)
            for img_file in os.listdir(student_path):
                if img_file.endswith('.jpg'):
                    img_path = os.path.join(student_path, img_file)
                    face_img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                    
                    if face_img is not None:
                        # Add face and label to training data
                        faces.append(face_img)
                        labels.append(label_map[student_id])
    
    if not faces:
        print("No training data found.")
        return False
    
    # Convert lists to numpy arrays
    faces = np.array(faces)
    labels = np.array(labels)
    
    # Train the model
    face_recognizer.train(faces, labels)
    
    # Save the model
    face_recognizer.save(os.path.join(MODELS_DIR, "face_recognizer.yml"))
    
    # Save the label mapping
    with open(os.path.join(MODELS_DIR, "label_map.pkl"), 'wb') as f:
        pickle.dump(label_map, f)
    
    print(f"Face recognition model trained with {len(faces)} images for {label_counter} students.")
    return True

def recognize_face(frame):
    """Recognize a face in the frame and return student ID"""
    if face_recognizer is None:
        load_models()
    
    # Check if model and label map exist
    model_path = os.path.join(MODELS_DIR, "face_recognizer.yml")
    label_map_path = os.path.join(MODELS_DIR, "label_map.pkl")
    
    if not (os.path.exists(model_path) and os.path.exists(label_map_path)):
        print("Face recognition model or label map not found.")
        return None
    
    # Load label map
    with open(label_map_path, 'rb') as f:
        label_map = pickle.load(f)
    
    # Reverse the label map (numeric label -> student ID)
    reverse_map = {v: k for k, v in label_map.items()}
    
    # Detect faces
    faces, gray = detect_faces(frame)
    
    for (x, y, w, h) in faces:
        # Extract and resize face
        face_img = gray[y:y+h, x:x+w]
        face_img = cv2.resize(face_img, FACE_SIZE)
        
        # Predict
        label, confidence = face_recognizer.predict(face_img)
        
        # Check if confidence is good enough (lower is better in LBPH)
        if confidence < 70:  # Threshold can be adjusted
            student_id = reverse_map.get(label)
            return student_id, confidence, (x, y, w, h)
    
    return None, None, None

def verify_student_face(student_id, confidence_threshold=70):
    """Verify a student's face for login"""
    if face_recognizer is None:
        load_models()
    
    # Load label map
    label_map_path = os.path.join(MODELS_DIR, "label_map.pkl")
    if not os.path.exists(label_map_path):
        print("Label map not found.")
        return False
    
    with open(label_map_path, 'rb') as f:
        label_map = pickle.load(f)
    
    # Get the numeric label for this student ID
    if student_id not in label_map:
        print(f"Student ID {student_id} not registered for face recognition.")
        return False
    
    student_label = label_map[student_id]
    
    # Initialize camera
    cap = cv2.VideoCapture(0)
    
    # Set a timeout (10 seconds)
    start_time = time.time()
    timeout = 10
    
    while time.time() - start_time < timeout:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Detect faces
        faces, gray = detect_faces(frame)
        
        for (x, y, w, h) in faces:
            # Draw rectangle around face
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            # Extract and resize face
            face_img = gray[y:y+h, x:x+w]
            face_img = cv2.resize(face_img, FACE_SIZE)
            
            # Predict
            label, confidence = face_recognizer.predict(face_img)
            
            # Display result on frame
            cv2.putText(
                frame,
                f"Matching: {'Yes' if label == student_label else 'No'}",
                (x, y-30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0) if label == student_label else (0, 0, 255),
                2
            )
            
            cv2.putText(
                frame,
                f"Confidence: {confidence:.2f}",
                (x, y-10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0) if confidence < confidence_threshold else (0, 0, 255),
                2
            )
            
            # Check if this is the correct student
            if label == student_label and confidence < confidence_threshold:
                # Release camera and close windows
                cap.release()
                cv2.destroyAllWindows()
                return True
        
        # Display frame
        cv2.imshow('Face Verification', frame)
        
        # Break loop if ESC pressed
        if cv2.waitKey(100) & 0xFF == 27:
            break
    
    # Release camera and close windows
    cap.release()
    cv2.destroyAllWindows()
    
    return False