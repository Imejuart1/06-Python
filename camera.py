import os
import time
import cv2
import numpy as np

FOLDER = r"C:\Users\USER\Downloads"   # ✅ change to your Simumatik camera folder

def get_latest_png(folder):
    files = [f for f in os.listdir(folder) if f.lower().endswith(".png")]
    if not files:
        return None
    full_paths = [os.path.join(folder, f) for f in files]
    return max(full_paths, key=os.path.getmtime)

def classify_color_rgb(mean_rgb):
    r, g, b = mean_rgb

    if r > 180 and g < 100 and b < 100:
        return "RED"
    if g > 180 and r < 100 and b < 100:
        return "GREEN"
    if b > 180 and r < 100 and g < 100:
        return "BLUE"
    if r > 180 and g > 180 and b < 140:
        return "YELLOW"
    if r > 200 and g > 200 and b > 200:
        return "WHITE"
    if r < 60 and g < 60 and b < 60:
        return "BLACK"

    return "MIXED/UNKNOWN"

last_file = None

print("✅ Watching folder:", FOLDER)

while True:
    try:
        img_path = get_latest_png(FOLDER)

        if img_path and img_path != last_file:
            last_file = img_path

            img = cv2.imread(img_path)
            if img is None:
                print("❌ Failed to read:", img_path)
                time.sleep(0.5)
                continue

            # Resize for speed
            img_small = cv2.resize(img, (200, 200))

            # Convert BGR -> RGB
            img_rgb = cv2.cvtColor(img_small, cv2.COLOR_BGR2RGB)

            # Mean color
            mean_rgb = np.mean(img_rgb.reshape(-1, 3), axis=0)

            color_name = classify_color_rgb(mean_rgb)

            print(f"📸 {os.path.basename(img_path)}  =>  {color_name}  | meanRGB={mean_rgb.astype(int)}")

        time.sleep(0.5)

    except Exception as e:
        print("❌ Error:", e)
        time.sleep(1)
