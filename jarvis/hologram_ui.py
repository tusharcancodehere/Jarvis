import cv2
import numpy as np
import datetime
import psutil
from collections import deque
from .config import Config
from .matrix_rain import MatrixRain
from .graphics_utils import GraphicsUtils

class HologramUI:
    """
    Manages the HUD rendering, including glow effects, menus, and notifications.
    Premium Edition: Cinematic visuals, FPS counter, Status Icons.
    """
    def __init__(self):
        self.matrix = MatrixRain()
        self.notifications = deque(maxlen=8)
        self.greeting_timer = 0
        self.greeting_text = ""
        
        self.menu_buttons = {
            "YOUTUBE": (Config.WIDTH - 160, 150, 140, 40),
            "GOOGLE": (Config.WIDTH - 160, 200, 140, 40),
            "MUSIC": (Config.WIDTH - 160, 250, 140, 40),
            "OBJECTS": (Config.WIDTH - 160, 300, 140, 40)
        }
        
    def add_notification(self, text):
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        self.notifications.append(f"[{ts}] {text}")
        
    def show_greeting(self, text):
        self.greeting_text = text
        self.greeting_timer = 120 
        
    def check_menu_click(self, cursor_pos):
        cx, cy = cursor_pos
        for name, rect in self.menu_buttons.items():
            x, y, w, h = rect
            if x < cx < x+w and y < cy < y+h:
                return name
        return None

    def update(self, img, detections, mouse_status, cursor_pos, fps, is_listening, is_locked):
        # 1. Matrix Background
        img = self.matrix.update(img)
        
        # 2. Cinematic Border
        GraphicsUtils.draw_cinematic_border(img)
        
        # 3. System Stats Panel (Top Left)
        GraphicsUtils.draw_glass_panel(img, (20, 20, 280, 160), title="SYSTEM STATUS")
        
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        batt = psutil.sensors_battery()
        pwr = batt.percent if batt else 100
        
        y = 60
        GraphicsUtils.draw_glow_text(img, f"CPU: {int(cpu)}%", (35, y), 0.5, Config.WHITE)
        cv2.rectangle(img, (130, y-8), (130 + int(cpu), y), Config.CYAN_HOLO, -1)
        
        y += 35
        GraphicsUtils.draw_glow_text(img, f"RAM: {int(ram)}%", (35, y), 0.5, Config.WHITE)
        cv2.rectangle(img, (130, y-8), (130 + int(ram), y), Config.ORANGE_WARN, -1)
        
        y += 35
        pwr_color = Config.GREEN_OK if pwr > 20 else Config.RED_ALERT
        GraphicsUtils.draw_glow_text(img, f"PWR: {int(pwr)}%", (35, y), 0.5, Config.WHITE)
        cv2.rectangle(img, (130, y-8), (130 + int(pwr), y), pwr_color, -1)
        
        # 4. FPS & GPU (Top Right)
        GraphicsUtils.draw_glow_text(img, f"FPS: {int(fps)}", (Config.WIDTH - 100, 40), 0.6, Config.GREEN_OK)
        gpu_status = "GPU: ON" if Config.CINEMATIC_MODE else "GPU: OFF" # Mock status or tied to YOLO
        GraphicsUtils.draw_glow_text(img, gpu_status, (Config.WIDTH - 100, 70), 0.5, Config.CYAN_HOLO)

        # 5. Voice Status (Bottom Center)
        if is_listening:
            cx = Config.WIDTH // 2
            cv2.circle(img, (cx, Config.HEIGHT - 40), 10, Config.CYAN_HOLO, -1)
            GraphicsUtils.draw_glow_text(img, "VOICE ACTIVE", (cx - 60, Config.HEIGHT - 60), 0.6, Config.CYAN_HOLO, glow_intensity=5)

        # 6. Security Lock Status
        if is_locked:
             GraphicsUtils.draw_glass_panel(img, (Config.WIDTH//2 - 150, 100, 300, 60), Config.RED_ALERT, 0.8)
             GraphicsUtils.draw_glow_text(img, "SECURITY LOCK ACTIVE", (Config.WIDTH//2 - 130, 140), 0.7, Config.WHITE, 2)

        # 7. Hologram Menu
        for name, rect in self.menu_buttons.items():
            x, y, w, h = rect
            is_hover = x < cursor_pos[0] < x+w and y < cursor_pos[1] < y+h
            
            bg_color = Config.BLUE_DEEP if not is_hover else Config.CYAN_DIM
            GraphicsUtils.draw_glass_panel(img, rect, bg_color, 0.6)
            
            color = Config.CYAN_HOLO if not is_hover else Config.WHITE
            GraphicsUtils.draw_glow_text(img, name, (x+10, y+25), 0.5, color)
            
        # 8. Notifications
        GraphicsUtils.draw_glass_panel(img, (Config.WIDTH - 350, Config.HEIGHT - 220, 330, 200), title="LOGS")
        y = Config.HEIGHT - 40
        for note in reversed(self.notifications):
            cv2.putText(img, note, (Config.WIDTH - 340, y), Config.FONT, 0.4, Config.CYAN_DIM, 1)
            y -= 25
            if y < Config.HEIGHT - 200: break
            
        # 9. Mouse Status
        status_color = Config.GREEN_OK if "ACTIVE" in mouse_status or "CLICK" in mouse_status else Config.ORANGE_WARN
        if "PAUSED" in mouse_status: status_color = Config.RED_ALERT
        GraphicsUtils.draw_glow_text(img, f"MOUSE: {mouse_status}", (20, Config.HEIGHT - 30), 0.6, status_color)
        
        # 10. Central Greeting
        if self.greeting_timer > 0:
            cx, cy = Config.WIDTH // 2, Config.HEIGHT // 2
            alpha = min(0.9, self.greeting_timer / 30.0)
            if alpha > 0.1:
                GraphicsUtils.draw_glass_panel(img, (cx - 200, cy - 60, 400, 120), Config.BLUE_DEEP, alpha)
                GraphicsUtils.draw_glow_text(img, self.greeting_text, (cx - 180, cy + 10), 1.0, Config.GOLD, 2)
            self.greeting_timer -= 1
            
        # 11. YOLO Detections
        for d in detections:
            x1, y1, x2, y2 = d['bbox']
            label = d['label'].upper()
            color = Config.RED_ALERT if label in ['person', 'knife', 'scissors'] else Config.CYAN_HOLO
            
            cv2.rectangle(img, (x1, y1), (x2, y2), color, 1)
            GraphicsUtils.draw_glow_text(img, f"{label} {int(d['conf']*100)}%", (x1, y1-10), 0.5, color)
            
        return img
