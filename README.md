# 🔐 Home Security System - Face Recognition + Hand Gesture Authentication

A two-factor authentication system for home security using:
1. **Face Recognition** - Verify identity
2. **Hand Gesture Detection** - Unlock or distress signal

## 🎯 Features

### Core Security
- ✅ **Two-factor authentication** (Face + Gesture)
- ✅ **Real-time hand tracking** (no training required!)
- ✅ **Multiple unlock gestures** (thumbs up, peace sign, open palm)
- ✅ **Distress signal** (closed fist, OK sign) - silent alarm
- ✅ **Auto-locking** after 5 seconds
- ✅ **Security logging** (JSON logs with timestamps)
- ✅ **Unknown face detection**

### Distress Features
- 🚨 Silent alarm (doesn't alert attacker)
- 🚨 Unlocks door (protects user)
- 🚨 Logs event with timestamp
- 🚨 Ready for SMS/email integration

## 📋 System Requirements

### Software
- Python 3.8+
- Webcam/Camera
- Windows/Linux/Mac

### Hardware (Minimum)
- Any computer with camera
- For production: Raspberry Pi 4 (4GB) + Camera Module

### Hardware (Recommended for Production)
- NVIDIA Jetson Nano
- IR Camera (night vision)
- Electric door lock (solenoid/magnetic)
- UPS backup power

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Test Gesture Recognition Only

```bash
python gesture_recognition.py
```

This will open your webcam and show gesture detection in real-time.

**Try these gestures:**
- 👍 **Thumbs up** - Unlock gesture
- ✌️ **Peace sign** - Alternative unlock
- ✋ **Open palm** - Alternative unlock
- ✊ **Closed fist** - Distress signal
- 👌 **OK sign** - Alternative distress

**Hold each gesture for 2 seconds to confirm!**

### 3. Run Full Security System

First, make sure you have preprocessed face images:

```bash
# Run your preprocessing script first
python datapreprocessing.py
```

Then run the security system:

```bash
python secure_entry_system.py
```

## 🎨 How to Customize Gestures

The system uses **geometric relationships** between hand landmarks (no training needed!). Here's how to add your own gestures:

### Understanding Hand Landmarks

MediaPipe detects 21 landmarks on each hand:

```
Landmarks:
  0  - Wrist
  1-4   - Thumb (1=base, 4=tip)
  5-8   - Index (5=base, 8=tip)
  9-12  - Middle (9=base, 12=tip)
  13-16 - Ring (13=base, 16=tip)
  17-20 - Pinky (17=base, 20=tip)
```

### Adding a Custom Gesture

Edit `gesture_recognition.py` in the `recognize_gesture()` method:

```python
def recognize_gesture(self, hand_landmarks, handedness):
    fingers = self.get_finger_states(hand_landmarks, handedness)
    # fingers = [thumb, index, middle, ring, pinky] - True if extended
    
    # Example: Add "POINT" gesture (only index extended)
    if not fingers[0] and fingers[1] and not fingers[2] and not fingers[3] and not fingers[4]:
        return "point", 0.9
    
    # Example: Add "HORN" gesture (index + pinky extended)
    if not fingers[0] and fingers[1] and not fingers[2] and not fingers[3] and fingers[4]:
        return "horn", 0.85
    
    # Example: Add "THREE" gesture (index + middle + ring)
    if not fingers[0] and fingers[1] and fingers[2] and fingers[3] and not fingers[4]:
        return "three", 0.8
```

### Using Landmark Distances

For more complex gestures (like finger touching):

```python
# Get landmarks
landmarks = hand_landmarks.landmark
thumb_tip = landmarks[4]
index_tip = landmarks[8]

# Calculate distance
distance = np.sqrt(
    (thumb_tip.x - index_tip.x)**2 + 
    (thumb_tip.y - index_tip.y)**2
)

# Fingers touching if distance < 0.05
if distance < 0.05:
    return "pinch", 0.9
```

### Gesture Ideas

**Simple (finger combinations):**
- 🤘 Rock sign (index + pinky)
- 🤙 Shaka (thumb + pinky)
- 🖖 Vulcan salute (split fingers)
- ☝️ Point (index only)
- 👆 Number gestures (1, 2, 3, 4, 5 fingers)

**Complex (distances/angles):**
- 🤏 Pinch (thumb + index close)
- 🤌 Italian gesture (all fingertips together)
- 👌 OK sign (thumb + index circle)
- ✍️ Writing pose (thumb + index + middle)

## ⚙️ Configuration

### In `secure_entry_system.py`:

```python
# Gesture hold time (seconds)
stability_window=30  # frames to confirm (30 frames ≈ 1 sec)

# Door unlock duration
unlock_time=5.0  # seconds

# Face recognition threshold
threshold = 8000  # Lower = stricter (adjust after testing)
```

### In `gesture_recognition.py`:

```python
# Detection sensitivity
min_detection_confidence=0.7  # Higher = fewer false detections
min_tracking_confidence=0.5   # Higher = more stable tracking

# Gesture confirmation
confidence_threshold=0.7  # Higher = more certain gestures
```

## 📊 State Machine Flow

```
[LOCKED]
   ↓ (Face recognized)
[FACE_RECOGNIZED]
   ↓ (Unlock gesture held 2s)     ↓ (Distress gesture held 2s)
[UNLOCKED]                      [DISTRESS]
   ↓ (5 seconds)                   ↓ (5 seconds + Alert sent)
[LOCKED]                        [LOCKED]
```

## 🔧 Hardware Integration (Future)

### Connecting to Door Lock

For Raspberry Pi + Relay module:

```python
import RPi.GPIO as GPIO

# Setup
RELAY_PIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)

# Unlock
GPIO.output(RELAY_PIN, GPIO.HIGH)
time.sleep(5)
GPIO.output(RELAY_PIN, GPIO.LOW)
```

### Adding SMS Alerts

```python
from twilio.rest import Client

def send_distress_alert(self, event):
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=f"🚨 DISTRESS: {event['identity']} at {event['timestamp']}",
        from_='+1234567890',
        to='+0987654321'
    )
```

## 📈 Improving Face Recognition

Your current method uses Haar Cascades + simple distance matching. To upgrade:

### Option 1: Use FaceNet (Recommended)

```python
from facenet_pytorch import MTCNN, InceptionResnetV1

# Detection
mtcnn = MTCNN(keep_all=False, device='cuda')

# Recognition
model = InceptionResnetV1(pretrained='vggface2').eval()

# Get embedding
aligned_face = mtcnn(frame)
embedding = model(aligned_face).detach().cpu().numpy()
```

### Option 2: Use OpenCV's DNN Face Recognition

```python
# Load pre-trained model
model = cv2.dnn.readNetFromTorch('openface.nn4.small2.v1.t7')

# Get 128-D embedding
face_blob = cv2.dnn.blobFromImage(face_crop, 1.0/255, (96, 96), 
                                   (0, 0, 0), swapRB=True, crop=False)
model.setInput(face_blob)
embedding = model.forward()
```

## 🐛 Troubleshooting

### Gesture not detected
- Ensure good lighting
- Keep hand within camera frame
- Hold gesture steady for full 2 seconds
- Check hand is at comfortable distance (50-100cm)

### Face not recognized
- Increase `threshold` in code (makes matching less strict)
- Add more training images per person
- Ensure good lighting on face
- Face camera directly

### Camera lag
- Lower resolution: `cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)`
- Reduce `stability_window` to 20 frames
- Close other camera-using apps

## 📁 Project Structure

```
home-security/
├── gesture_recognition.py      # Standalone gesture detection
├── secure_entry_system.py      # Full integrated system
├── datapreprocessing.py        # Your face preprocessing
├── requirements.txt            # Dependencies
├── README.md                   # This file
│
├── D:\MARK\FINAL PROJECT\
│   ├── DATASET/                # Original face images
│   │   ├── MARK/
│   │   ├── CHIRAG/
│   │   └── ...
│   └── OUTPUT/                 # Preprocessed faces (used by system)
│       ├── MARK/
│       ├── CHIRAG/
│       └── ...
│
└── security_logs/              # Generated logs
    ├── access_log.json
    └── distress_log.json
```

## 🔐 Security Best Practices

1. **Anti-Spoofing**: Add liveness detection
   - Require eye blink during face recognition
   - Check for gesture movement (not static photo)

2. **Backup Access**: Always have manual override
   - Physical key
   - PIN code on keypad
   - Admin mobile app

3. **Logging**: Keep detailed logs
   - All access attempts (successful + failed)
   - Timestamps and identities
   - Photos/videos of attempts

4. **Network Security**:
   - Use local processing (no cloud dependency)
   - Encrypt logs
   - Secure API keys for alerts

5. **Privacy**:
   - Store face data locally only
   - Clear old logs periodically
   - Inform users of recording

## 📝 License

MIT License - feel free to use and modify!

## 🙏 Credits

- MediaPipe by Google (hand tracking)
- OpenCV (computer vision)
- Your preprocessing pipeline (face detection)

---

**Questions? Issues?**
Test thoroughly before deploying on actual door lock!
Always maintain physical backup access method.
