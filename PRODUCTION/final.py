
import time
import cv2
import numpy as np
from Controller import UDP_Controller

IMG_PATH = r"C:\Users\USER\Simumatik\workspace\cameras\Camera_0.jpeg"
TEMPLATE_PATH = r"C:\Users\USER\Simumatik\workspace\cameras\template.jpeg"

template_master = cv2.imread(TEMPLATE_PATH, 0)

if template_master is None:
    print("ERROR: Template not found")
    exit()


def detect_bottle(path):

    img = cv2.imread(path, 0)
    if img is None:
        return False

    h, w = img.shape

    roi = img[int(h * 0.2):int(h * 0.9),
              int(w * 0.3):int(w * 0.7)]

    template = template_master.copy()

    rh, rw = roi.shape
    th, tw = template.shape

    if th >= rh or tw >= rw:
        scale = min((rh - 5) / th, (rw - 5) / tw)
        template = cv2.resize(template, (0, 0), fx=scale, fy=scale)

    roi = cv2.GaussianBlur(roi, (5, 5), 0)
    template = cv2.GaussianBlur(template, (5, 5), 0)

    res = cv2.matchTemplate(roi, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(res)

    detected = max_val > 0.55

    if detected:
        print("BOTTLE DETECTED")
    else:
        print("NO BOTTLE")

    return detected


# ================= MAIN =================

if __name__ == "__main__":

    controller = UDP_Controller()

    # Digital signals
    controller.addVariable("digital_inputs1", "byte", 0)
    controller.addVariable("digital_outputs1", "byte", 0)
    controller.addVariable("digital_inputs2", "byte", 0)
    controller.addVariable("digital_outputs2", "byte", 0)

    # Analog counters
    controller.addVariable("A01", "int", 0)
    controller.addVariable("A02", "int", 0)
    controller.addVariable("A03", "int", 0)

    controller.start()

    # ========= STATES =========
    latched_out0 = False

    cam_timer_active = False
    cam_timer_start = 0
    cam_duration = 5.0

    prev_IN2 = False
    last_bottle_result = False

    prev_IN1 = False
    in1_seen = False

    pulse_start = time.monotonic()
    pulse_interval = 6.0

    # Counter states
    count_A01 = 0
    count_A02 = 0
    count_A03 = 0

    prev_IN0 = False
    prev_IN3 = False
    prev_IN4 = False

    # ========= LOOP =========
    while True:

        inputs = controller.getMappedValue("digital_inputs1")

        IN0 = inputs[-1]
        IN1 = inputs[-2]
        IN2 = inputs[-3]
        IN3 = inputs[-4]
        IN4 = inputs[-5]

        OUT0 = False
        OUT1 = False
        OUT2 = False
        OUT3 = False
        OUT4 = False
        OUT5 = False

        # ---------- IN1 FIRST RISE ----------
        if IN1 and not prev_IN1:
            in1_seen = True
            pulse_start = time.monotonic()

        prev_IN1 = IN1

        # ---------- 6s pulse ----------
        if in1_seen:
            if time.monotonic() - pulse_start >= pulse_interval:
                OUT5 = True
                pulse_start = time.monotonic()

        # ---------- LATCH ----------
        if IN1:
            latched_out0 = True

        if latched_out0:
            OUT0 = True

        if IN0:
            OUT0 = False

        OUT1 = IN0
        OUT3 = IN3

        # ---------- CAMERA ----------
        if IN2 and not prev_IN2:
            cam_timer_active = True
            cam_timer_start = time.monotonic()
            OUT4 = True

            last_bottle_result = detect_bottle(IMG_PATH)

        prev_IN2 = IN2

        if cam_timer_active:
            OUT4 = True
            OUT0 = False

            if time.monotonic() - cam_timer_start >= cam_duration:
                cam_timer_active = False

        # ---------- VISION RESULT ----------
        if IN4 and last_bottle_result:
            OUT2 = True

        # ---------- ANALOG COUNTERS ----------

        # A01: count IN0 rising edge
        if IN0 and not prev_IN0:
            count_A01 += 1
            controller.setValue("A01", count_A01)
        prev_IN0 = IN0

        # A02: count IN4 rising edge ONLY if bottle detected
        if IN4 and not prev_IN4 and last_bottle_result:
            count_A02 += 1
            controller.setValue("A02", count_A02)
        prev_IN4 = IN4

        # A03: count IN3 rising edge
        if IN3 and not prev_IN3:
            count_A03 += 1
            controller.setValue("A03", count_A03)
        prev_IN3 = IN3

        # ---------- OUTPUT MAP ----------
        controller.setMappedValue(
            "digital_outputs1",
            [False, False, OUT5, OUT4, OUT3, OUT2, OUT1, OUT0]
        )

        time.sleep(0.05)
