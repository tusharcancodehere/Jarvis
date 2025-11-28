import cv2
import numpy as np
import random
from .config import Config

class MatrixRain:
    """
    Optimized Matrix Rain effect using numpy operations where possible.
    """
    def __init__(self):
        self.width = Config.WIDTH
        self.height = Config.HEIGHT
        self.drops = np.random.randint(0, self.height // 20, size=(self.width // 20))
        self.chars = list("0123456789ABCDEF")
        
    def update(self, img):
        """
        Updates the matrix rain effect on the provided image.
        """
        # Create a separate layer for the rain to allow alpha blending
        overlay = img.copy()
        
        # Loop through drops
        for i in range(len(self.drops)):
            # Random character
            char = random.choice(self.chars)
            x = i * 20
            y = self.drops[i] * 20
            
            # Draw character
            # Only draw if on screen
            if y < self.height + 20:
                # Color variation for "tail" effect
                color = Config.GREEN_OK
                if random.random() > 0.95:
                    color = Config.WHITE # Sparkle
                
                cv2.putText(overlay, char, (x, y), Config.FONT, 0.4, color, 1)
            
            # Reset drop
            if y > self.height:
                if random.random() > 0.98: # Random reset
                    self.drops[i] = 0
            else:
                self.drops[i] += Config.MATRIX_SPEED
                
        # Blend overlay with original image
        # Use addWeighted for transparency
        cv2.addWeighted(overlay, Config.MATRIX_OPACITY, img, 1.0 - Config.MATRIX_OPACITY, 0, img)
        return img
