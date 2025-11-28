# Controls & Gestures

## 🖱️ Hand Mouse Control
The Hand Mouse system uses MediaPipe to track your hand landmarks.

- **Activation**: Say "Enable mouse" or ensure your hand is visible if enabled.
- **Pointer**: Extend your **Index Finger**. The cursor maps to your finger tip.
- **Left Click**: Pinch your **Index Finger** and **Thumb** together.
- **Right Click**: Pinch your **Middle Finger** and **Thumb** together.
- **Pause/Safety**: Make a **Fist** (close all fingers) to temporarily pause cursor movement. This prevents accidental clicks while typing or resting.
- **Keyboard Toggle**: Press `ESC` to toggle mouse control on/off instantly.

## 🗣️ Voice Commands
The system listens for the wake word **"Jarvis"**.

### System
- **"Shutdown"**: Safely closes the application.
- **"Goodbye"**: Same as shutdown.

### Vision
- **"Enable object detection"**: Loads the YOLOv8 model and starts detecting objects.
- **"Disable object detection"**: Unloads/pauses the vision module to save resources.

### Identity
- **"Register my name is [Name]"**: Starts the face registration process. Look at the camera and hold still.

### Applications
- **"Open YouTube"**: Launches YouTube in your default browser.
- **"Open Google"**: Launches Google.
- **"Search for [Query]"**: Performs a Google search for the specified query.
