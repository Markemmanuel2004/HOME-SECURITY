import cv2
import os
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict

# ==============================
# CONFIGURATION - UPDATED FOR YOUR DATASET
# ==============================
input_folder = r'D:\MARK\FINAL PROJECT\DATASET'
output_folder = r'D:\MARK\FINAL PROJECT\OUTPUT'

# Updated to match your actual identities
identities = ['MARK', 'CHIRAG', 'ANKIT', 'ADNAN']
IMG_SIZE = 224

# Create output folders
for identity in identities:
    os.makedirs(os.path.join(output_folder, identity), exist_ok=True)

# ==============================
# FACE DETECTION + CROP
# ==============================
def detect_and_crop_face(img):
    """
    Detect face in image and crop it
    Returns list of cropped face images
    """
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    )

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=4,
        minSize=(50, 50)
    )

    if len(faces) == 0:
        return []

    h_img, w_img = gray.shape
    valid_faces = []

    for (x, y, w, h) in faces:
        aspect = w / float(h)
        area = w * h

        # Filter out non-face-like rectangles
        if not (0.5 < aspect < 1.6):
            continue

        if area < 0.02 * w_img * h_img or area > 0.6 * w_img * h_img:
            continue

        valid_faces.append((x, y, w, h))

    if not valid_faces:
        return []

    # Get largest face
    x, y, w, h = sorted(valid_faces, key=lambda f: f[2]*f[3], reverse=True)[0]

    # Add padding
    pad = 10
    x1, y1 = max(x-pad, 0), max(y-pad, 0)
    x2, y2 = min(x+w+pad, img.shape[1]), min(y+h+pad, img.shape[0])

    crop = img[y1:y2, x1:x2]
    return [crop]

# ==============================
# PREPROCESSING LOOP
# ==============================
count_per_identity = defaultdict(int)
contrast_per_identity = defaultdict(list)
mean_intensity_per_identity = defaultdict(list)
skipped_files = []
processed_files = []

print("="*60)
print("FACE PREPROCESSING - STARTING")
print("="*60)
print(f"\nInput folder: {input_folder}")
print(f"Output folder: {output_folder}")
print(f"Expected identities: {identities}")
print("\n" + "="*60)

for identity in os.listdir(input_folder):

    identity_path = os.path.join(input_folder, identity)

    if not os.path.isdir(identity_path):
        continue

    if identity.upper() not in identities:
        print(f"\n⚠️  Skipping unknown folder: {identity}")
        continue

    print(f"\n📁 Processing identity: {identity}")
    print("-" * 40)

    os.makedirs(os.path.join(output_folder, identity), exist_ok=True)

    image_files = [f for f in os.listdir(identity_path) 
                   if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
    
    print(f"   Found {len(image_files)} images")

    for img_name in image_files:

        img_path = os.path.join(identity_path, img_name)
        img = cv2.imread(img_path)

        if img is None:
            print(f"   ✗ Could not read: {img_name}")
            skipped_files.append((identity, img_name, "Cannot read"))
            continue

        crops = detect_and_crop_face(img)

        if not crops:
            print(f"   ✗ No face detected: {img_name}")
            skipped_files.append((identity, img_name, "No face detected"))
            continue

        for idx, crop in enumerate(crops):

            # Convert to grayscale
            gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
            
            # Resize to standard size
            resized = cv2.resize(gray, (IMG_SIZE, IMG_SIZE))

            # Normalize and equalize histogram
            norm = cv2.normalize(resized, None, 0, 255, cv2.NORM_MINMAX)
            eq = cv2.equalizeHist(norm)

            # Check contrast (skip very low contrast images)
            std_val = eq.std()
            if std_val < 20:
                print(f"   ✗ Low contrast: {img_name}")
                skipped_files.append((identity, img_name, "Low contrast"))
                continue

            # Stats
            count_per_identity[identity] += 1
            contrast_per_identity[identity].append(std_val)
            mean_intensity_per_identity[identity].append(eq.mean())

            # Save processed image
            out_name = f"{os.path.splitext(img_name)[0]}_face{idx}.jpg"
            out_path = os.path.join(output_folder, identity, out_name)
            cv2.imwrite(out_path, eq)
            processed_files.append((identity, img_name, out_name))

    print(f"   ✓ Processed: {count_per_identity[identity]} faces")

# ==============================
# SUMMARY
# ==============================
print("\n" + "="*60)
print("PREPROCESSING COMPLETE")
print("="*60)

total_processed = sum(count_per_identity.values())
total_skipped = len(skipped_files)

print(f"\n📊 SUMMARY:")
print("-" * 40)
for identity in identities:
    count = count_per_identity[identity]
    print(f"   {identity:15} {count:4} faces")

print(f"\n   {'TOTAL PROCESSED':15} {total_processed:4} faces")
print(f"   {'TOTAL SKIPPED':15} {total_skipped:4} images")

if total_processed < 50:
    print("\n⚠️  WARNING: Low image count!")
    print("   Recommendation: Add more images per person (aim for 100+)")
    print("   Current average: {:.1f} per person".format(total_processed / len(identities)))

# Save processing report
report_path = os.path.join(output_folder, "preprocessing_report.txt")
with open(report_path, 'w') as f:
    f.write("FACE PREPROCESSING REPORT\n")
    f.write("="*60 + "\n\n")
    f.write(f"Total processed: {total_processed}\n")
    f.write(f"Total skipped: {total_skipped}\n\n")
    
    f.write("Per Identity:\n")
    for identity in identities:
        f.write(f"  {identity}: {count_per_identity[identity]} faces\n")
    
    if skipped_files:
        f.write("\n\nSkipped Files:\n")
        for identity, filename, reason in skipped_files:
            f.write(f"  {identity}/{filename} - {reason}\n")

print(f"\n📄 Report saved to: {report_path}")

# ==============================
# VISUALIZATION 1 — FACE GRID
# ==============================
print("\n📊 Generating visualizations...")

gallery = []

for identity in identities:
    folder = os.path.join(output_folder, identity)
    if not os.path.isdir(folder):
        continue
    for f in os.listdir(folder):
        if f.lower().endswith('.jpg'):
            gallery.append((os.path.join(folder, f), identity))

if gallery:
    # Limit to 40 images for visualization
    gallery = gallery[:40]
    
    n_images = len(gallery)
    n_cols = 8
    n_rows = (n_images // n_cols) + (n_images % n_cols > 0)

    plt.figure(figsize=(16, 2*n_rows))
    for idx, (fname, identity) in enumerate(gallery):
        img = cv2.imread(fname, cv2.IMREAD_GRAYSCALE)
        plt.subplot(n_rows, n_cols, idx+1)
        plt.imshow(img, cmap='gray')
        plt.title(identity, fontsize=8)
        plt.axis('off')

    plt.suptitle("Sample Preprocessed Face Images", fontsize=16)
    plt.tight_layout(rect=[0, 0, 1, 0.97])
    
    # Save visualization
    viz_path = os.path.join(output_folder, "face_samples.png")
    plt.savefig(viz_path, dpi=150, bbox_inches='tight')
    print(f"   ✓ Face samples saved to: {viz_path}")

# ==============================
# VISUALIZATION 2 — COUNT BAR
# ==============================
plt.figure(figsize=(10, 6))
counts = [count_per_identity[id_] for id_ in identities]
colors = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12']
bars = plt.bar(identities, counts, color=colors)

plt.xlabel("Identity", fontsize=12)
plt.ylabel("Number of Faces", fontsize=12)
plt.title("Preprocessed Faces per Identity", fontsize=14, fontweight='bold')

for i, (bar, c) in enumerate(zip(bars, counts)):
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height,
            f'{c}',
            ha='center', va='bottom', fontsize=12, fontweight='bold')

plt.grid(axis='y', alpha=0.3)
plt.tight_layout()

count_viz_path = os.path.join(output_folder, "face_count_by_identity.png")
plt.savefig(count_viz_path, dpi=150, bbox_inches='tight')
print(f"   ✓ Count visualization saved to: {count_viz_path}")

# ==============================
# VISUALIZATION 3 — CONTRAST BAR
# ==============================
plt.figure(figsize=(10, 6))
avg_contrast = [
    np.mean(contrast_per_identity[id_]) if contrast_per_identity[id_] else 0
    for id_ in identities
]
bars = plt.bar(identities, avg_contrast, color=colors)

plt.xlabel("Identity", fontsize=12)
plt.ylabel("Average Contrast (Std Dev)", fontsize=12)
plt.title("Average Face Contrast per Identity", fontsize=14, fontweight='bold')

for bar, c in zip(bars, avg_contrast):
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height,
            f'{c:.1f}',
            ha='center', va='bottom', fontsize=11)

plt.grid(axis='y', alpha=0.3)
plt.tight_layout()

contrast_viz_path = os.path.join(output_folder, "face_contrast_by_identity.png")
plt.savefig(contrast_viz_path, dpi=150, bbox_inches='tight')
print(f"   ✓ Contrast visualization saved to: {contrast_viz_path}")

# ==============================
# VISUALIZATION 4 — INTENSITY HISTOGRAMS
# ==============================
plt.figure(figsize=(14, 10))

for idx, id_ in enumerate(identities):
    folder = os.path.join(output_folder, id_)
    pixels = []

    if os.path.isdir(folder):
        for f in os.listdir(folder):
            if f.lower().endswith('.jpg'):
                img = cv2.imread(os.path.join(folder, f), cv2.IMREAD_GRAYSCALE)
                if img is not None:
                    pixels.append(img.flatten())

    if not pixels:
        continue

    pixels = np.concatenate(pixels)

    plt.subplot(2, 2, idx+1)
    plt.hist(pixels, bins=32, range=(0, 255), color=colors[idx], alpha=0.7)
    plt.title(f"Intensity Distribution: {id_}", fontsize=12, fontweight='bold')
    plt.xlabel("Pixel Intensity")
    plt.ylabel("Frequency")
    plt.grid(alpha=0.3)

plt.tight_layout()

hist_viz_path = os.path.join(output_folder, "intensity_histograms.png")
plt.savefig(hist_viz_path, dpi=150, bbox_inches='tight')
print(f"   ✓ Histogram visualization saved to: {hist_viz_path}")

print("\n" + "="*60)
print("✅ ALL PROCESSING COMPLETE!")
print("="*60)
print(f"\nProcessed faces saved to: {output_folder}")
print(f"You can now run the security system:\n")
print(f"   python secure_entry_system.py")
print("\n" + "="*60)

# Optionally show plots
# plt.show()
