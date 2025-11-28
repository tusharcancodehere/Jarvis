import pyautogui
import numpy as np
import time
import math
from collections import deque
from .config import Config

class MouseController:
    """
    Handles Hand-to-Mouse interaction with advanced smoothing and safety checks.
    """
    def __init__(self):
        self.screen_w, self.screen_h = pyautogui.size()
        self.x_history = deque(maxlen=Config.MOUSE_SMOOTHING)
        self.y_history = deque(maxlen=Config.MOUSE_SMOOTHING)
        
        self.active = False
        self.last_click_time = 0
        self.cursor_pos = (0, 0)
        self.paused_by_keyboard = False
        self.debug_info = {}
        
    def check_permissions(self):
        """
        Checks if pyautogui has screen access.
        """
        try:
            # Attempt a safe read operation
            pyautogui.position()
            return True
        except Exception:
            return False

    def update(self, landmarks, frame_shape):
        """
        Updates mouse position based on hand landmarks.
        frame_shape: (width, height)
        Returns status string.
        """
        if self.paused_by_keyboard:
            return "KEY-PAUSED"
            
        w, h = frame_shape # Corrected geometry
        
        index_tip = landmarks[8]
        thumb_tip = landmarks[4]
        middle_tip = landmarks[12]
        ring_tip = landmarks[16]
        pinky_tip = landmarks[20]
        
        # Safety: Check if fist (All fingertips below PIP joints)
        # 0=Wrist, 1-4=Thumb, 5-8=Index, 9-12=Middle, 13-16=Ring, 17-20=Pinky
        # PIP joints are 6, 10, 14, 18
        fingers_open = 0
        if index_tip.y < landmarks[6].y: fingers_open += 1
        if middle_tip.y < landmarks[10].y: fingers_open += 1
        if ring_tip.y < landmarks[14].y: fingers_open += 1
        if pinky_tip.y < landmarks[18].y: fingers_open += 1
        
        if fingers_open == 0: # Strict fist check
            self.active = False
            return "PAUSED (FIST)"
            
        self.active = True
        
        # Movement
        x1 = index_tip.x * w
        y1 = index_tip.y * h
        
        r = Config.FRAME_REDUCTION
        x_clamped = np.clip(x1, r, w - r)
        y_clamped = np.clip(y1, r, h - r)
        
        screen_x = np.interp(x_clamped, (r, w - r), (0, self.screen_w))
        screen_y = np.interp(y_clamped, (r, h - r), (0, self.screen_h))
        
        self.x_history.append(screen_x)
        self.y_history.append(screen_y)
        
        avg_x = sum(self.x_history) / len(self.x_history)
        avg_y = sum(self.y_history) / len(self.y_history)
        
        self.cursor_pos = (int(avg_x), int(avg_y))
        
        try:
            pyautogui.moveTo(avg_x, avg_y, _pause=False)
        except pyautogui.FailSafeException:
            pass 
        
        # Clicks
        dist_left = math.hypot(x1 - thumb_tip.x * w, y1 - thumb_tip.y * h)
        dist_right = math.hypot((middle_tip.x * w) - (thumb_tip.x * w), (middle_tip.y * h) - (thumb_tip.y * h))
        
        # Dynamic Threshold based on hand distance (Palm size approximation)
        # Distance between Wrist (0) and Middle MCP (9)
        wrist = landmarks[0]
        middle_mcp = landmarks[9]
        palm_size = math.hypot((wrist.x - middle_mcp.x)*w, (wrist.y - middle_mcp.y)*h)
        
        # Normalize palm size (approx 100-200px usually)
        # If palm is large (close), threshold should be larger
        # If palm is small (far), threshold should be smaller
        
        dynamic_threshold = Config.CLICK_THRESHOLD * (palm_size / 80.0) 
        dynamic_threshold = max(15, min(dynamic_threshold, 70))
        
        self.debug_info = {
            "palm_size": int(palm_size),
            "threshold": int(dynamic_threshold),
            "dist_left": int(dist_left),
            "dist_right": int(dist_right)
        }
        
        curr_time = time.time()
        if curr_time - self.last_click_time > Config.CLICK_COOLDOWN:
            if dist_left < dynamic_threshold:
                pyautogui.click()
                self.last_click_time = curr_time
                return "L-CLICK"
            elif dist_right < dynamic_threshold:
                pyautogui.rightClick()
                self.last_click_time = curr_time
                return "R-CLICK"
                
        return "ACTIVE"
