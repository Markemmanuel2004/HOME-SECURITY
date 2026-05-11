# 🏠 HOME SECURITY SYSTEM - FINAL PROJECT
## Face Recognition + Hand Gesture Authentication

---

## 📁 PROJECT STRUCTURE

```
D:\MARK\FINAL PROJECT\
│
├── DATASET/                    # Your raw images (INPUT)
│   ├── ADNAN/                  # 66 images
│   ├── ANKIT/                  # 47 images  
│   ├── CHIRAG/                 # 43 images
│   └── MARK/                   # 49 images
│
├── OUTPUT/                     # Preprocessed faces (will be created)
│   ├── ADNAN/
│   ├── ANKIT/
│   ├── CHIRAG/
│   ├── MARK/
│   ├── preprocessing_report.txt
│   ├── face_samples.png
│   ├── face_count_by_identity.png
│   ├── face_contrast_by_identity.png
│   └── intensity_histograms.png
│
└── SECURITY_SYSTEM/            # Python scripts (create this folder)
    ├── preprocess_faces.py     # Step 1: Preprocess dataset
    ├── gesture_recognition.py  # Step 2: Test gestures
    ├── secure_entry_system.py  # Step 3: Run full system
    ├── test_setup.py           # Verify installation
    ├── requirements.txt
    ├── README.md
    └── security_logs/          # Generated during runtime
        ├── access_log.json
        └── distress_log.json
```

---

## 🚀 INSTALLATION & SETUP

### Step 1: Install Python Packages

Open Command Prompt in the `SECURITY_SYSTEM` folder and run:

```bash
pip install -r requirements.txt
```

This installs:
- OpenCV (face detection, camera)
- MediaPipe (hand tracking)
- NumPy (math operations)
- Matplotlib (visualizations)

### Step 2: Verify Installation

```bash
python test_setup.py
```

This will test:
- ✓ All packages installed
- ✓ Camera access
- ✓ MediaPipe hand tracking
- ✓ Face detection cascade
- ✓ Gesture module

**If all tests pass, you're ready to proceed!**

---

## 📊 DATA PREPROCESSING

### Run Face Preprocessing

```bash
python preprocess_faces.py
```

**What it does:**
1. Reads images from `D:\MARK\FINAL PROJECT\DATASET\`
2. Detects faces using Haar Cascade
3. Crops and resizes to 224x224 pixels
4. Applies histogram equalization
5. Filters low-quality images
6. Saves to `D:\MARK\FINAL PROJECT\OUTPUT\`

**Expected output:**
```
📊 SUMMARY:
   MARK            49 faces
   CHIRAG          43 faces
   ANKIT           47 faces
   ADNAN           66 faces
   
   TOTAL PROCESSED 205 faces
```

**Visualizations created:**
- `face_samples.png` - Grid of sample faces
- `face_count_by_identity.png` - Bar chart
- `face_contrast_by_identity.png` - Quality metrics
- `intensity_histograms.png` - Pixel distributions

---

## 🎮 TESTING THE SYSTEM

### Test 1: Gesture Recognition Only

```bash
python gesture_recognition.py
```

**Try these gestures (hold for 2 seconds):**

✅ **UNLOCK GESTURES:**
- 👍 Thumbs up
- ✌️ Peace sign
- ✋ Open palm

🚨 **DISTRESS GESTURES:**
- ✊ Closed fist
- 👌 OK sign

**Tips:**
- Keep hand 50-100cm from camera
- Ensure good lighting
- Hold gesture steady for 2 seconds
- Green text = detected, Red text = waiting

Press 'q' to quit.

---

### Test 2: Full Security System

```bash
python secure_entry_system.py
```

**How it works:**

1. **Look at camera**
   - System detects and recognizes your face
   - Green box = recognized, Red box = unknown

2. **Show gesture**
   - After face recognized, show unlock gesture
   - Hold for 2 seconds
   - Progress bar shows hold time

3. **Door unlocks**
   - Success message displayed
   - Door auto-locks after 5 seconds

**State Flow:**
```
[LOCKED] 
    ↓ Face recognized
[FACE_RECOGNIZED] 
    ↓ Unlock gesture                 ↓ Distress gesture
[UNLOCKED]                        [DISTRESS]
    ↓ 5 seconds                       ↓ Alert sent
[LOCKED]                          [LOCKED]
```

---

## 🎯 SYSTEM FEATURES

### Two-Factor Authentication
1. **Face Recognition** (Who you are)
2. **Hand Gesture** (What you know)

### Security Features
- ✅ Real-time face detection
- ✅ Live hand tracking (no training needed!)
- ✅ Gesture stability check (2-second hold)
- ✅ Auto-locking (5 seconds)
- ✅ Unknown face logging
- ✅ Security event logs (JSON)

### Distress Signal
- 🚨 Silent alarm (doesn't alert attacker)
- 🚨 Unlocks door (protects you)
- 🚨 Logs event with timestamp
- 🚨 Ready for SMS/email alerts

---

## ⚙️ CONFIGURATION

### Adjust Recognition Sensitivity

In `secure_entry_system.py`, line ~70:

```python
# Face recognition threshold
threshold = 8000  # Lower = stricter matching
```

**Tuning guide:**
- Too many false rejections? **Increase** to 10000-12000
- Getting false positives? **Decrease** to 6000-7000
- Test with each person and adjust

### Change Gesture Hold Time

In `gesture_recognition.py`, line ~15:

```python
stability_window=30  # frames (~1 second)
```

In `secure_entry_system.py`, line ~236:

```python
if gesture_info['hold_time'] >= 2.0:  # 2 seconds
```

### Change Door Unlock Duration

In `secure_entry_system.py`, line ~23:

```python
unlock_time=5.0  # seconds
```

---

## 🔧 TROUBLESHOOTING

### Problem: Face not recognized

**Solutions:**
1. Increase threshold in code (line 70)
2. Ensure good lighting on face
3. Face camera directly
4. Add more training images
5. Run preprocessing again

### Problem: Gesture not detected

**Solutions:**
1. Improve lighting
2. Keep hand in frame
3. Maintain 50-100cm distance
4. Hold gesture steady for full 2 seconds
5. Try different gesture (thumbs up is most reliable)

### Problem: Camera not working

**Solutions:**
1. Close other apps using camera
2. Try different camera index: `cv2.VideoCapture(1)` or `(2)`
3. Check camera permissions in Windows settings
4. Restart computer

### Problem: Slow performance

**Solutions:**
1. Lower resolution in code:
   ```python
   cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
   cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
   ```
2. Reduce stability_window to 20
3. Close other programs
4. Use wired camera (not wireless)

---

## 📈 IMPROVING ACCURACY

### Add More Training Images

**Current counts:**
- MARK: 49 images
- CHIRAG: 43 images
- ANKIT: 47 images
- ADNAN: 66 images

**Recommendations:**
1. Capture 50-100 more images per person
2. Vary conditions:
   - Different lighting (bright, dim, natural)
   - Different angles (front, slight turn)
   - Different expressions (neutral, smile)
   - With/without glasses
   - Different times of day
3. Run preprocessing again

### Upgrade to Deep Learning (Optional)

For better accuracy (95%+), upgrade to FaceNet:

```python
# Install
pip install facenet-pytorch

# In secure_entry_system.py, replace Haar Cascade with:
from facenet_pytorch import MTCNN, InceptionResnetV1

mtcnn = MTCNN(keep_all=False)
model = InceptionResnetV1(pretrained='vggface2').eval()
```

See README.md for full instructions.

---

## 🔐 SECURITY BEST PRACTICES

### 1. Anti-Spoofing
Add liveness detection:
- Require eye blink during face recognition
- Check for gesture movement (not static photo)

### 2. Backup Access
Always maintain:
- Physical key
- PIN code backup
- Admin mobile override

### 3. Logging & Monitoring
- Review access logs daily
- Set up alerts for unknown faces
- Keep video recordings (optional)

### 4. Privacy
- Store all data locally (no cloud)
- Encrypt security logs
- Clear old logs periodically
- Inform users of recording

---

## 🔌 HARDWARE INTEGRATION (Next Step)

### Connecting to Real Door Lock

**Required Hardware:**
- Raspberry Pi 4 (4GB) - ₹4000
- Relay module (5V) - ₹150
- Electric door lock - ₹2000-5000
- Camera module - ₹1500
- UPS/Power backup - ₹3000

**Wiring:**
```
Raspberry Pi GPIO → Relay → Door Lock
     Pin 17      →  IN1   →  12V Lock
```

**Code Integration:**
```python
import RPi.GPIO as GPIO

RELAY_PIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)

def unlock_door(self):
    GPIO.output(RELAY_PIN, GPIO.HIGH)  # Unlock
    time.sleep(5)
    GPIO.output(RELAY_PIN, GPIO.LOW)   # Lock
```

---

## 📱 ADDING SMS ALERTS (Distress Signal)

### Setup Twilio

1. Sign up at twilio.com (free trial)
2. Get phone number + API keys
3. Install: `pip install twilio`

### Code:

```python
from twilio.rest import Client

TWILIO_SID = "your_account_sid"
TWILIO_TOKEN = "your_auth_token"
TWILIO_FROM = "+1234567890"
ALERT_TO = "+0987654321"

def send_distress_alert(self, event):
    client = Client(TWILIO_SID, TWILIO_TOKEN)
    
    message = client.messages.create(
        body=f"🚨 DISTRESS SIGNAL\n"
             f"Person: {event['identity']}\n"
             f"Time: {event['timestamp']}\n"
             f"Location: Front Door",
        from_=TWILIO_FROM,
        to=ALERT_TO
    )
    
    print(f"Alert sent! SID: {message.sid}")
```

---

## 📊 SECURITY LOGS

Logs are saved in `security_logs/` folder:

### access_log.json
```json
[
  {
    "timestamp": "2026-04-20T15:30:45",
    "identity": "MARK",
    "event_type": "UNLOCK",
    "state": "UNLOCKED"
  }
]
```

### distress_log.json
```json
[
  {
    "timestamp": "2026-04-20T16:15:22",
    "identity": "MARK",
    "location": "Front Door",
    "status": "ACTIVE"
  }
]
```

---

## ✅ TESTING CHECKLIST

Before deploying on real lock:

- [ ] All 4 identities recognized correctly
- [ ] Unknown faces rejected
- [ ] Unlock gestures work reliably
- [ ] Distress gestures trigger alarm
- [ ] Auto-lock after 5 seconds works
- [ ] Logs created correctly
- [ ] System stable for 1+ hour
- [ ] Works in different lighting
- [ ] Backup access method ready
- [ ] Hardware wired correctly (if using lock)

---

## 🎓 PROJECT DEMONSTRATION

### For Presentation:

1. **Show Dataset**
   - 205 preprocessed faces across 4 identities
   - Visualizations of distribution

2. **Demo Preprocessing**
   - Run preprocess_faces.py
   - Show before/after images

3. **Demo Gesture Recognition**
   - Show live hand tracking
   - Demonstrate all gestures

4. **Demo Full System**
   - Face recognition
   - Gesture unlock
   - Distress signal
   - Auto-locking

5. **Show Security Logs**
   - Access events
   - Distress events

6. **Explain Architecture**
   - Two-factor authentication
   - State machine flow
   - Hardware integration plan

---

## 📞 SUPPORT

If you encounter issues:

1. Run `python test_setup.py`
2. Check error messages
3. Review troubleshooting section
4. Verify dataset paths are correct
5. Ensure good lighting for camera

---

## 🎉 PROJECT COMPLETE!

Your home security system is ready to use. Remember to:
- ✅ Test thoroughly before production
- ✅ Maintain backup access
- ✅ Review logs regularly
- ✅ Keep system updated

**Good luck with your project! 🚀**
