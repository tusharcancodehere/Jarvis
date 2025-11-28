import cv2
import numpy as np
from .config import Config

class GraphicsUtils:
    """
    Helper functions for drawing glowing text and glass panels.
    Premium Edition: Thicker glows, smoother alphas.
    """
    @staticmethod
    def draw_glow_text(img, text, pos, scale=0.5, color=Config.CYAN_HOLO, thickness=1, glow_intensity=3):
        """Draws text with a blurred glow outline."""
        x, y = pos
        # Glow (Thick line)
        cv2.putText(img, text, pos, Config.FONT, scale, color, thickness + glow_intensity)
        # Core (Thin line)
        cv2.putText(img, text, pos, Config.FONT, scale, Config.WHITE, thickness)

    @staticmethod
    def draw_glass_panel(img, rect, color=Config.BLUE_DEEP, alpha=Config.UI_ALPHA, title=None):
        x, y, w, h = rect
        sub = img[y:y+h, x:x+w]
        if sub.shape[0] == 0 or sub.shape[1] == 0: return
        
        # Fill
        fill = np.full(sub.shape, color, dtype=np.uint8)
        res = cv2.addWeighted(sub, 1-alpha, fill, alpha, 0)
        img[y:y+h, x:x+w] = res
        
        # Border
        cv2.rectangle(img, (x, y), (x+w, y+h), Config.CYAN_HOLO, 1)
        
        # Corner Accents (Cinematic Style)
        l = 15
        t = 2
        # Top Left
        cv2.line(img, (x, y), (x+l, y), Config.WHITE, t)
        cv2.line(img, (x, y), (x, y+l), Config.WHITE, t)
        # Top Right
        cv2.line(img, (x+w, y), (x+w-l, y), Config.WHITE, t)
        cv2.line(img, (x+w, y), (x+w, y+l), Config.WHITE, t)
        # Bottom Left
        cv2.line(img, (x, y+h), (x+l, y+h), Config.WHITE, t)
        cv2.line(img, (x, y+h), (x, y+h-l), Config.WHITE, t)
        # Bottom Right
        cv2.line(img, (x+w, y+h), (x+w-l, y+h), Config.WHITE, t)
        cv2.line(img, (x+w, y+h), (x+w, y+h-l), Config.WHITE, t)
        
        # Title
        if title:
            GraphicsUtils.draw_glow_text(img, title, (x+10, y+25), 0.6, Config.CYAN_HOLO, 1)
            
    @staticmethod
    def draw_cinematic_border(img):
        h, w = img.shape[:2]
        color = Config.CYAN_DIM
        t = 2
        l = 50
        
        # Corners
        cv2.line(img, (20, 20), (20+l, 20), color, t)
        cv2.line(img, (20, 20), (20, 20+l), color, t)
        
        cv2.line(img, (w-20, 20), (w-20-l, 20), color, t)
        cv2.line(img, (w-20, 20), (w-20, 20+l), color, t)
        
        cv2.line(img, (20, h-20), (20+l, h-20), color, t)
        cv2.line(img, (20, h-20), (20, h-20-l), color, t)
        
        cv2.line(img, (w-20, h-20), (w-20-l, h-20), color, t)
        cv2.line(img, (w-20, h-20), (w-20, h-20-l), color, t)
        
        # Center Crosshair
        cx, cy = w//2, h//2
        cv2.line(img, (cx-10, cy), (cx+10, cy), color, 1)
        cv2.line(img, (cx, cy-10), (cx, cy+10), color, 1)
