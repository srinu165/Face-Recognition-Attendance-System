import os

# College name
COLLEGE_NAME = "TEEGALA KRISHNA REDDY ENGINEERING COLLEGE"

# Directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODELS_DIR = os.path.join(DATA_DIR, "models")
FACES_DIR = os.path.join(DATA_DIR, "faces")
ATTENDANCE_DIR = os.path.join(DATA_DIR, "attendance")

# Create directories if they don't exist
for directory in [DATA_DIR, MODELS_DIR, FACES_DIR, ATTENDANCE_DIR]:
    os.makedirs(directory, exist_ok=True)

# Database settings
DB_PATH = os.path.join(DATA_DIR, "attendance.db")

# UI settings
THEME_COLOR = "#0d47a1"  # Primary color (dark blue)
ACCENT_COLOR = "#f44336"  # Accent color (red)
BACKGROUND_COLOR = "#f5f5f5"  # Background color (light gray)
SUCCESS_COLOR = "#4caf50"  # Success color (green)
WARNING_COLOR = "#ff9800"  # Warning color (orange)
ERROR_COLOR = "#f44336"  # Error color (red)

# Face recognition settings
FACE_CONFIDENCE_THRESHOLD = 70  # Confidence threshold for face recognition
MIN_FACE_SIZE = (30, 30)  # Minimum face size for detection
FACE_REGISTER_IMAGES = 20  # Number of images to take during registration