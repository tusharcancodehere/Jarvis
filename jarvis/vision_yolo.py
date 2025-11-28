import torch
from ultralytics import YOLO
from .config import Config
import math

class VisionSystem:
    """
    Manages YOLOv8 Object Detection with GPU acceleration and stability checks.
    """
    def __init__(self):
        self.model = None
        self.enabled = False
        self.device = 'cpu'
        
    def load_model(self):
        """
        Loads the YOLO model. Attempts CUDA first, falls back to CPU.
        """
        if self.model is not None:
            return True
            
        print("[VISION] Loading YOLO model...")
        try:
            if torch.cuda.is_available():
                try:
                    t = torch.zeros(1).cuda()
                    del t
                    self.device = 'cuda'
                    print("[VISION] CUDA Detected. Using GPU.")
                except Exception as e:
                    print(f"[VISION] GPU Error: {e}. Falling back to CPU.")
                    self.device = 'cpu'
            else:
                self.device = 'cpu'
                
            self.model = YOLO(Config.YOLO_MODEL)
            self.model.to(self.device)
            print(f"[VISION] Model loaded on {self.device}.")
            return True
            
        except Exception as e:
            print(f"[VISION] Critical Load Error: {e}")
            self.model = None
            return False

    def detect(self, frame):
        """
        Runs detection on the frame.
        Returns list of dicts: {'bbox': (x1,y1,x2,y2), 'label': str, 'conf': float}
        """
        if not self.enabled or self.model is None:
            return []
            
        try:
            results = self.model(frame, verbose=False, stream=False, conf=Config.YOLO_CONF_THRESHOLD)
            detections = []
            
            for r in results:
                boxes = r.boxes
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0]
                    conf = float(box.conf[0])
                    cls = int(box.cls[0])
                    label = self.model.names[cls]
                    
                    detections.append({
                        'bbox': (int(x1), int(y1), int(x2), int(y2)),
                        'conf': conf,
                        'label': label
                    })
            return detections
            
        except Exception as e:
            print(f"[VISION] Detection Error: {e}")
            return []
            
    def toggle(self, state=None):
        if state is None:
            self.enabled = not self.enabled
        else:
            self.enabled = state
            
        if self.enabled and self.model is None:
            self.load_model()
            
        return self.enabled
