import json
import numpy as np
import os
from .config import Config

class FaceID:
    """
    Biometric System 2.6 (Premium)
    Adds Admin checks and Security Locking.
    """
    def __init__(self):
        self.db = {}
        self.load_db()
        
    def load_db(self):
        if os.path.exists(Config.DB_FILE):
            try:
                with open(Config.DB_FILE, 'r') as f:
                    self.db = json.load(f)
            except Exception as e:
                print(f"[FACE_ID] Error loading DB: {e}")
                self.db = {}
        else:
            self.db = {}
            
    def save_db(self):
        try:
            with open(Config.DB_FILE, 'w') as f:
                json.dump(self.db, f, indent=4)
        except Exception as e:
            print(f"[FACE_ID] Error saving DB: {e}")

    def get_embedding(self, landmarks):
        lms = np.array(landmarks)
        try:
            left_eye = lms[33]
            right_eye = lms[263]
            nose_tip = lms[1]
            mouth_left = lms[61]
            mouth_right = lms[291]
            chin = lms[152]
        except IndexError:
            return None 
            
        base_dist = np.linalg.norm(left_eye - right_eye)
        if base_dist < 1e-6: return None
        
        def dist_ratio(p1, p2):
            return np.linalg.norm(p1 - p2) / base_dist
            
        vector = [
            dist_ratio(left_eye, nose_tip),
            dist_ratio(right_eye, nose_tip),
            dist_ratio(left_eye, mouth_left),
            dist_ratio(right_eye, mouth_right),
            dist_ratio(nose_tip, chin),
            dist_ratio(mouth_left, mouth_right),
            dist_ratio(left_eye, chin),
            dist_ratio(right_eye, chin),
            dist_ratio(nose_tip, mouth_left),
            dist_ratio(nose_tip, mouth_right),
            dist_ratio(mouth_left, chin),
            dist_ratio(mouth_right, chin)
        ]
        return vector

    def register_face(self, name, landmarks_buffer):
        embeddings = []
        for lms in landmarks_buffer:
            emb = self.get_embedding(lms)
            if emb:
                embeddings.append(emb)
        
        if not embeddings:
            return False
            
        avg_embedding = np.mean(embeddings, axis=0).tolist()
        
        if name not in self.db:
            self.db[name] = []
            
        self.db[name].append(avg_embedding)
        
        if len(self.db[name]) > Config.MAX_SAMPLES_PER_USER:
            self.db[name].pop(0) 
            
        self.save_db()
        return True

    def identify(self, landmarks):
        """
        Identifies a face.
        Returns (Name, Confidence_Score)
        """
        if not self.db:
            return "UNKNOWN", 0.0
            
        current_vec = self.get_embedding(landmarks)
        if current_vec is None:
            return "UNKNOWN", 0.0
            
        current_vec = np.array(current_vec)
        norm_curr = np.linalg.norm(current_vec)
        
        best_match = "UNKNOWN"
        best_score = -1.0
        
        for name, samples in self.db.items():
            for stored_vec in samples:
                stored_vec = np.array(stored_vec)
                norm_stored = np.linalg.norm(stored_vec)
                
                dot_product = np.dot(current_vec, stored_vec)
                similarity = dot_product / (norm_curr * norm_stored)
                
                if similarity > best_score:
                    best_score = similarity
                    best_match = name
                
        if best_score > Config.FACE_MATCH_THRESHOLD:
            return best_match, best_score
            
        return "UNKNOWN", 0.0
        
    def is_admin(self, name):
        return name.lower() == Config.ADMIN_USER.lower()
