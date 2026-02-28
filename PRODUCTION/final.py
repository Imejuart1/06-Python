import time
import cv2
import numpy as np
from Controller import UDP_Controller


# =====================================================
# CAMERA IMAGE PATH
# =====================================================
IMG_PATH = r"C:\Users\USER\Simumatik\workspace\cameras\Camera_0.jpeg"


# =====================================================
# BOTTLE DETECTION
# =====================================================
def detect_bottle(path, debug=True):

    print("VISION: Capturing image...")

    img = cv2.imread(path)
    if img is None:
        print(f"ERROR: Could not read image at {path}")
        return False

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)

    kernel = np.ones((5, 5), np.uint8)
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

    contours, _ = cv2.findContours(
        binary,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    detected = False

    for cnt in contours:
        area = cv2.contourArea(cnt)

        if area > 3000:
            detected = True
            x, y, w, h = cv2.boundingRect(cnt)

            cv2.rectangle(img, (x, y), (x+w, y+h), (0,255,0), 3)
            cv2.putText(img, "BOTTLE", (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 2)

    if debug:
        cv2.imshow("Original with Detection", img)
        cv2.imshow("Binary", binary)
        print(f"BOTTLE DETECTED: {detected}")
        cv2.waitKey(1)

    return detected


# ================= MAIN =================

if __name__ == "__main__":

    controller = UDP_Controller()

    controller.addVariable("digital_inputs1", "byte", 0)
    controller.addVariable("digital_outputs1", "byte", 0)
    controller.addVariable("digital_inputs2", "byte", 0)
    controller.addVariable("digital_outputs2", "byte", 0)

    controller.addVariable("A01", "int", 0)
    controller.addVariable("A02", "int", 0)
    controller.addVariable("A03", "int", 0)

    controller.start()

    latched_out0 = False

    # CAMERA STATE MACHINE
    cam_timer_active = False
    cam_timer_start = 0
    cam_state = 0   # 0=idle,1=wait before shot,2=wait before vision

    prev_IN2 = False
    feed_blocked = False
    last_bottle_result = False
    release_requested = False
    in11_active = False
    in11_timer = 0
    in11_hold_time = 4.0
    prev_IN11 = False

    prev_IN1 = False
    in1_seen = False

    pulse_start = time.monotonic()
    pulse_interval_startup = 1 # before start button
    pulse_interval_run = 5      # after start
    feed_open = False
    feed_timer = 0
    feed_release_time = 0.5
    prev_OUT0 = False
    count_A01 = 0
    count_A02 = 0
    count_A03 = 0
    out7_timer = time.monotonic()
    out7_state = False
    out7_interval = 5.0

    prev_IN0 = False
    prev_IN3 = False
    prev_IN4 = False

    while True:

        inputs = controller.getMappedValue("digital_inputs1")

        IN0 = inputs[-1]
        IN1 = inputs[-2]
        IN2 = inputs[-3]
        IN3 = inputs[-4]
        IN4 = inputs[-5]
        inputs2 = controller.getMappedValue("digital_inputs2")
        IN11 = inputs2[-4]

        OUT0 = False
        OUT1 = False
        OUT2 = False
        OUT3 = False
        OUT4 = False
        OUT5 = False
        OUT6 = False
        OUT7 = False
        OUT8 = False

        feed_blocked = False

        # ================= START BUTTON =================
        if IN1 and not prev_IN1:
            in1_seen = True
            pulse_start = time.monotonic()
            print("SYSTEM: START BUTTON PRESSED")

        prev_IN1 = IN1

        # Detect IN11 trigger
# IN11 rising edge trigger
        if IN11 and not prev_IN11:
            in11_active = True
            in11_timer = time.monotonic()
            print("IN11 TRIGGERED")

        prev_IN11 = IN11

        # ================= OUT5 PULSE LOGIC =================
        if in1_seen:
            interval = pulse_interval_run
        else:
            interval = pulse_interval_startup

        if time.monotonic() - pulse_start >= interval:
            OUT5 = True
            pulse_start = time.monotonic()

        # Conveyor latch
        if IN1:
            latched_out0 = True

        if latched_out0:
            OUT0 = True

        if OUT0 and not cam_timer_active:
            release_requested = True

        # Metal detection
        if IN0:
            OUT0 = False
            print("METAL DETECTED")
        
        # Bottle position stop
        if IN4 and last_bottle_result:
            OUT0 = False

        OUT1 = IN0
        OUT3 = IN3
        # ================= OUT7 GRAVITY STOCK RELEASE =================
        if in1_seen:
            if time.monotonic() - out7_timer >= out7_interval:
                out7_state = not out7_state
                out7_timer = time.monotonic()

            OUT7 = out7_state
        else:
            OUT7 = False
            out7_state = False
        # ================= CAMERA TRIGGER =================
        if IN2 and not prev_IN2:
            print("CAMERA: TRIGGERED")
            cam_timer_active = True
            cam_timer_start = time.monotonic()
            cam_state = 1

        prev_IN2 = IN2

        # ================= CAMERA SEQUENCE =================
        if cam_timer_active:

            OUT0 = False   # STOP conveyor always

            # STEP 1: wait 2 sec before snapshot
            if cam_state == 1:
                if time.monotonic() - cam_timer_start >= 2.0:
                    OUT4 = True
                    print("CAMERA: SNAPSHOT")
                    cam_timer_start = time.monotonic()
                    cam_state = 2

            # STEP 2: wait 2 sec for disk update
            elif cam_state == 2:
                OUT4 = True
                if time.monotonic() - cam_timer_start >= 2.0:
                    print("CAMERA: PROCESS IMAGE")
                    last_bottle_result = detect_bottle(
                        IMG_PATH,
                        debug=True
                    )
                    cam_timer_active = False
                    cam_state = 0
                    print("CAMERA: DONE")

        # ================= VISION RESULT =================
        if IN4 and last_bottle_result:
            OUT2 = True
            print("ACTION: BOTTLE PUSHER ACTIVATED")
        
        # ================= OUT8 SAFE TIMED CONTROL =================
        
        if in11_active:

            OUT8 = False
            feed_blocked = True

            if time.monotonic() - in11_timer >= in11_hold_time:

                if OUT0:
                    in11_active = False
                    print("IN11 RELEASED: OUT0 CLEAR")
                else:
                    in11_timer = time.monotonic()
                    print("WAITING: OUT0 NOT CLEAR")

        else:
            if OUT0:
                OUT8 = True
            else:
                OUT8 = False
                feed_blocked = True

        # ================= GRAVITY FEED BLOCKER =================

        if feed_blocked:
            OUT6 = True
            feed_open = False

        # MASTER STOP
        elif IN11:
            OUT6 = True      # close blocker
            feed_open = False

        else:
            # existing OUT6 logic continues here
            if not OUT0:
                OUT6 = True
                feed_open = False

            else:
                # Open only when release requested
                if release_requested:
                    feed_open = True
                    feed_timer = time.monotonic()
                    release_requested = False

                if feed_open:
                    OUT6 = False

                    if time.monotonic() - feed_timer >= feed_release_time:
                        OUT6 = True
                        feed_open = False
                else:
                    OUT6 = True


        # ================= COUNTERS =================
        if IN0 and not prev_IN0:
            count_A01 += 1
            controller.setValue("A01", count_A01)
        prev_IN0 = IN0

        if IN4 and not prev_IN4 and last_bottle_result:
            count_A02 += 1
            controller.setValue("A02", count_A02)
        prev_IN4 = IN4

        if IN3 and not prev_IN3:
            count_A03 += 1
            controller.setValue("A03", count_A03)
        prev_IN3 = IN3

        controller.setMappedValue(
            "digital_outputs1",
            [OUT7, OUT6, OUT5, OUT4, OUT3, OUT2, OUT1, OUT0]
        )
        controller.setMappedValue(
            "digital_outputs2",
            [False, False, False, False, False, False, False, OUT8]
        )

        time.sleep(0.05)