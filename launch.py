#!/usr/bin/env python3
"""
HOME SECURITY SYSTEM - INTERACTIVE LAUNCHER
Guides you through setup, preprocessing, testing, and running the system
"""

import os
import sys
import time

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def print_step(number, text):
    """Print step number"""
    print(f"\n{'='*70}")
    print(f"STEP {number}: {text}")
    print(f"{'='*70}\n")

def wait_for_user(prompt="Press Enter to continue..."):
    """Wait for user input"""
    input(f"\n{prompt}")

def run_command(command, description):
    """Run a command and show description"""
    print(f"\n▶ {description}")
    print(f"  Command: {command}\n")
    
    response = input("Run this command? (y/n): ").strip().lower()
    if response == 'y':
        os.system(command)
        return True
    else:
        print("  Skipped.")
        return False

def main():
    """Main launcher"""
    
    print_header("🏠 HOME SECURITY SYSTEM - PROJECT LAUNCHER")
    
    print("""
    This launcher will guide you through:
    
    1. ✓ Verify installation
    2. 📊 Preprocess face dataset
    3. 🎮 Test gesture recognition
    4. 🔐 Run full security system
    
    Your Dataset:
    - MARK:   49 images
    - CHIRAG: 43 images
    - ANKIT:  47 images
    - ADNAN:  66 images
    - TOTAL:  205 images
    """)
    
    wait_for_user("Ready to begin? Press Enter...")
    
    # ==========================================
    # STEP 1: Verify Installation
    # ==========================================
    print_step(1, "VERIFY INSTALLATION")
    
    print("""
    First, let's verify that all required packages are installed
    and your camera is working.
    
    This will test:
    - OpenCV
    - MediaPipe
    - NumPy
    - Matplotlib
    - Camera access
    - Face detection
    - Hand tracking
    """)
    
    if run_command("python test_setup.py", "Running installation verification"):
        print("\n✅ Installation verified!")
    else:
        print("\n⚠️  Skipped installation check.")
        response = input("\nContinue anyway? (y/n): ").strip().lower()
        if response != 'y':
            print("Exiting. Please run test_setup.py manually first.")
            return
    
    wait_for_user()
    
    # ==========================================
    # STEP 2: Preprocess Dataset
    # ==========================================
    print_step(2, "PREPROCESS FACE DATASET")
    
    print("""
    Now we'll preprocess your face images.
    
    This will:
    - Detect faces in each image
    - Crop and resize to 224x224 pixels
    - Apply histogram equalization
    - Filter low-quality images
    - Save to OUTPUT folder
    - Generate visualizations
    
    Input:  D:\\MARK\\FINAL PROJECT\\DATASET\\
    Output: D:\\MARK\\FINAL PROJECT\\OUTPUT\\
    
    Expected: ~205 processed faces
    Time: ~1-2 minutes
    """)
    
    if run_command("python preprocess_faces.py", "Running face preprocessing"):
        print("\n✅ Faces preprocessed!")
        print("\nCheck OUTPUT folder for:")
        print("  - Processed face images")
        print("  - preprocessing_report.txt")
        print("  - Visualization images")
    else:
        print("\n⚠️  Skipped preprocessing.")
        print("Note: You need preprocessed faces to run the security system.")
    
    wait_for_user()
    
    # ==========================================
    # STEP 3: Test Gestures
    # ==========================================
    print_step(3, "TEST GESTURE RECOGNITION")
    
    print("""
    Let's test the hand gesture recognition system.
    
    This will open your camera and track your hand in real-time.
    
    Try these gestures (hold for 2 seconds):
    
    UNLOCK GESTURES:
    - 👍 Thumbs up
    - ✌️ Peace sign
    - ✋ Open palm
    
    DISTRESS GESTURES:
    - ✊ Closed fist
    - 👌 OK sign
    
    Tips:
    - Keep hand 50-100cm from camera
    - Ensure good lighting
    - Hold gesture steady
    
    Press 'q' to quit the demo
    """)
    
    if run_command("python gesture_recognition.py", "Opening gesture recognition demo"):
        print("\n✅ Gesture demo complete!")
    else:
        print("\n⚠️  Skipped gesture demo.")
    
    wait_for_user()
    
    # ==========================================
    # STEP 4: Run Full System
    # ==========================================
    print_step(4, "RUN FULL SECURITY SYSTEM")
    
    print("""
    Now let's run the complete two-factor security system!
    
    HOW IT WORKS:
    
    1. Look at the camera
       → System will recognize your face
       → Green box = recognized
       → Red box = unknown
    
    2. Show unlock gesture
       → Thumbs up, Peace, or Open palm
       → Hold for 2 seconds
       → Watch progress bar fill
    
    3. Door unlocks!
       → Success message shown
       → Auto-locks after 5 seconds
    
    DISTRESS MODE:
    - Show fist or OK sign instead
    - Door unlocks (to protect you)
    - Silent alarm activated
    - Alert logged
    
    Press 'q' to quit the system
    
    """)
    
    print("⚠️  IMPORTANT NOTES:")
    print("  - This is a demo system (no real lock connected)")
    print("  - Test thoroughly before connecting hardware")
    print("  - Always maintain backup access method")
    print("  - Review security logs after testing")
    
    wait_for_user("\nReady to run? Press Enter...")
    
    if run_command("python secure_entry_system.py", "Starting security system"):
        print("\n✅ Security system demo complete!")
    else:
        print("\n⚠️  Skipped security system.")
    
    # ==========================================
    # COMPLETION
    # ==========================================
    print_header("✅ PROJECT LAUNCHER COMPLETE")
    
    print("""
    Your home security system is ready!
    
    📁 Check these files:
    - security_logs/access_log.json     (access attempts)
    - security_logs/distress_log.json   (distress signals)
    - OUTPUT/preprocessing_report.txt   (preprocessing stats)
    
    📖 Next Steps:
    1. Review SETUP_GUIDE.md for detailed instructions
    2. Read README.md for customization options
    3. Tune face recognition threshold if needed
    4. Add more training images for better accuracy
    5. Plan hardware integration (Raspberry Pi + lock)
    
    🔐 For Production Deployment:
    - Connect to real door lock (see SETUP_GUIDE.md)
    - Set up SMS/email alerts for distress signals
    - Add liveness detection (anti-spoofing)
    - Implement backup access (PIN/key)
    - Regular security log reviews
    
    🎓 For Project Presentation:
    1. Show dataset and preprocessing results
    2. Demo gesture recognition
    3. Demo full system with all identities
    4. Explain two-factor authentication
    5. Show security logs
    6. Discuss hardware integration plan
    
    Good luck with your project! 🚀
    """)
    
    print("\n" + "="*70)
    print("  Thank you for using the Home Security System!")
    print("="*70 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Launcher interrupted by user.")
        print("You can run individual scripts manually:")
        print("  - python test_setup.py")
        print("  - python preprocess_faces.py")
        print("  - python gesture_recognition.py")
        print("  - python secure_entry_system.py")
        sys.exit(0)
