# Troubleshooting Guide

## Common Issues

### 🎤 Microphone Not Working
- **Symptom**: JARVIS doesn't respond to "Jarvis".
- **Fix**:
    1. Check your Windows Sound Settings. Ensure your desired microphone is set as **Default Device**.
    2. Check the console logs. If you see `[VOICE] Microphone Error`, the system is retrying.
    3. Ensure no other application has exclusive control of the microphone.

### 📷 Camera Not Working
- **Symptom**: The window opens but shows a black screen or crashes immediately.
- **Fix**:
    1. Ensure your webcam is plugged in.
    2. Check if another app (Zoom, Discord, Camera App) is using the webcam.
    3. Verify `cv2.VideoCapture(0)` index in `jarvis/jarvis_core.py`. Try changing `0` to `1` if you have multiple cameras.

### 🐢 System Lag / Low FPS
- **Symptom**: The UI is choppy or mouse movement is delayed.
- **Fix**:
    1. **Disable Object Detection**: Say "Disable object detection". YOLOv8 is heavy on resources.
    2. **Reduce Mouse Smoothing**: In `jarvis/config.py`, lower `MOUSE_SMOOTHING` to `3` or `2`.
    3. **Check Power Mode**: Ensure your laptop is plugged in and set to "High Performance".

### ⚠️ "ModuleNotFoundError"
- **Symptom**: Crash on startup saying a module is missing.
- **Fix**: Run `pip install -r requirements.txt` again.

### 🛑 GPU Not Used
- **Symptom**: Console says "Falling back to CPU".
- **Fix**:
    1. Ensure you have an NVIDIA GPU.
    2. Install PyTorch with CUDA support: [https://pytorch.org/get-started/locally/](https://pytorch.org/get-started/locally/)
    3. Verify `torch.cuda.is_available()` returns `True` in a Python shell.
