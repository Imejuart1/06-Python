import cv2
import numpy as np

# =====================================================
# CAMERA IMAGE PATH
# =====================================================
# Removed the trailing comma from your original code which created a tuple
IMG_PATH = r"C:\Users\USER\Simumatik\workspace\cameras\template1.jpeg"

def detect_bottle(path, debug=True):
    # 1. Load the image in color
    img = cv2.imread(path)
    if img is None:
        print(f"ERROR: Could not read image at {path}")
        return False

    # 2. Convert to Grayscale for easier "brightness" detection
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 3. Apply Threshold (Find bright white objects)
    # 200 is the sensitivity. If it's not picking up the bottle, lower it to 150.
    _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)

    # 4. Cleanup the noise (small dots)
    kernel = np.ones((5,5), np.uint8)
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

    # 5. Find Outlines (Contours)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    detected = False
    
    # 6. Analyze the shapes found
    for cnt in contours:
        area = cv2.contourArea(cnt)
        
        # Only count it as a bottle if the white shape is big enough
        # This prevents tiny glints of light from being called "bottles"
        if area > 3000:
            detected = True
            
            if debug:
                # Draw a green box around what we found
                x, y, w, h = cv2.boundingRect(cnt)
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 3)
                cv2.putText(img, "BOTTLE", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 2)

    # =====================================================
    # DEBUG VISUALIZATION
    # =====================================================
    if debug:
        cv2.imshow("Original with Detection", img)
        cv2.imshow("What the AI sees (Binary)", binary)
        print(f"BOTTLE DETECTED: {detected}")
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return detected

if __name__ == "__main__":
    result = detect_bottle(IMG_PATH, debug=True)
    if result:
        print(">>> PLC ACTION: BOTTLE TRUE")
    else:
        print(">>> PLC ACTION: BOTTLE FALSE")