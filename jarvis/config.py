import os
import cv2

class Config:
    """
    Central configuration for JARVIS Mark-II Premium.
    """
    # ===================== SYSTEM INFO =====================
    APP_NAME = "JARVIS MARK-II"
    VERSION = "2.6.0 (Premium)"
    WIDTH = 1280
    HEIGHT = 720
    FPS_LIMIT = 60
    
    # ===================== DYNAMIC PATHS =====================
    _CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    ROOT_DIR = os.path.dirname(_CURRENT_DIR)
    
    DATA_DIR = os.path.join(ROOT_DIR, "data")
    ASSETS_DIR = os.path.join(ROOT_DIR, "assets")
    DOCS_DIR = os.path.join(ROOT_DIR, "docs")
    
    LOGS_DIR = os.path.join(DATA_DIR, "logs")
    SCREENSHOT_DIR = os.path.join(DATA_DIR, "screenshots")
    FACES_DIR = os.path.join(ASSETS_DIR, "faces")
    
    DB_FILE = os.path.join(DATA_DIR, "face_db.json")
    LOG_FILE = os.path.join(LOGS_DIR, "jarvis.log")
    
    # ===================== COLORS (BGR) =====================
    CYAN_HOLO = (255, 255, 0)       
    CYAN_DIM = (100, 100, 0)        
    BLUE_DEEP = (50, 20, 0)         
    ORANGE_WARN = (0, 165, 255)     
    RED_ALERT = (0, 0, 255)         
    GREEN_OK = (0, 255, 0)          
    WHITE = (255, 255, 255)         
    GOLD = (0, 215, 255)            
    
    # ===================== UI SETTINGS =====================
    FONT = cv2.FONT_HERSHEY_SIMPLEX
    UI_ALPHA = 0.7
    GLOW_STRENGTH = 15
    MATRIX_SPEED = 1
    MATRIX_OPACITY = 0.15 
    CINEMATIC_MODE = True
    
    # ===================== MOUSE CONTROL =====================
    MOUSE_SMOOTHING = 5         
    FRAME_REDUCTION = 120       
    CLICK_THRESHOLD = 30        
    CLICK_COOLDOWN = 0.6
    GESTURE_HAND = "RIGHT" # "RIGHT", "LEFT", "BOTH"
    
    # ===================== SECURITY =====================
    FACE_MATCH_THRESHOLD = 0.85 
    REGISTRATION_FRAMES = 15    
    FACE_STABILITY_CHECK = 10   
    MAX_SAMPLES_PER_USER = 5    
    ADMIN_USER = "Admin" # Default admin name
    LOCK_ON_UNKNOWN = True
    
    # ===================== VOICE =====================
    WAKE_WORD = "jarvis"
    VOICE_RATE = 145 # Slower, deeper
    VOICE_VOLUME = 1.0
    VOICE_PITCH = 0.8 # Lower pitch (simulated)
    MIC_ENERGY_THRESHOLD = 300
    MIC_DYNAMIC_ENERGY = True
    ONE_SHOT_COMMAND = True     
    
    # ===================== VISION =====================
    YOLO_MODEL = "yolov8n.pt" 
    YOLO_CONF_THRESHOLD = 0.5
    
    @staticmethod
    def setup_directories():
        dirs = [
            Config.DATA_DIR, 
            Config.LOGS_DIR, 
            Config.SCREENSHOT_DIR, 
            Config.ASSETS_DIR, 
            Config.FACES_DIR
        ]
        for d in dirs:
            if not os.path.exists(d):
                os.makedirs(d)
