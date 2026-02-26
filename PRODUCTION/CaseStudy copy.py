import cv2

IMG_PATH = r"C:\Users\USER\Simumatik\workspace\cameras\Camera_0.jpeg"
TEMPLATE_PATH = r"C:\Users\USER\Simumatik\workspace\cameras\template.jpeg"

print("\n=== CAMERA TEST START ===")

img = cv2.imread(IMG_PATH, 0)
template = cv2.imread(TEMPLATE_PATH, 0)

if img is None or template is None:
    print("Image or template missing")
    exit()

print("Images loaded OK")

h, w = img.shape
th, tw = template.shape

print(f"Camera: {w}x{h}")
print(f"Template: {tw}x{th}")

# SIMPLE CENTER ROI
roi = img[int(h*0.2):int(h*0.9),
          int(w*0.3):int(w*0.7)]

rh, rw = roi.shape
print(f"ROI: {rw}x{rh}")

# -------- SIZE SAFETY --------
if th >= rh or tw >= rw:
    print("Resizing template to fit ROI")

    scale_h = (rh-5)/th
    scale_w = (rw-5)/tw
    scale = min(scale_h, scale_w)

    template = cv2.resize(template, (0,0), fx=scale, fy=scale)

    th, tw = template.shape
    print(f"New Template: {tw}x{th}")

# Blur for stability
roi = cv2.GaussianBlur(roi,(5,5),0)
template = cv2.GaussianBlur(template,(5,5),0)

# MATCH
res = cv2.matchTemplate(roi, template, cv2.TM_CCOEFF_NORMED)
_, max_val, _, _ = cv2.minMaxLoc(res)

print(f"Match score: {max_val:.3f}")

if max_val > 0.55:
    print(">>> BOTTLE DETECTED")
else:
    print(">>> NO BOTTLE")

print("=== CAMERA TEST END ===")
