import time
from Controller import UDP_Controller

if __name__ == "__main__":
    controller = UDP_Controller()

    # Only using digital_inputs1 and digital_outputs1
    controller.addVariable("digital_inputs1", "byte", 0)
    controller.addVariable("digital_outputs1", "byte", 0)
    controller.start()

    # --- Latches ---
    out0_latch = False
    out1_latch = False

    while True:
        # --- Read digital inputs ---
        inputs1 = controller.getMappedValue("digital_inputs1")

        IN0 = inputs1[-1]   # bit 0
        IN1 = inputs1[-2]   # bit 1
        IN2 = inputs1[-3]   # bit 2
        IN3 = inputs1[-4]   # bit 3
        # --- Logic ---
        # IN0 sets OUT0 and OUT1 ON (latched)
        if IN0:
            out0_latch = True
            out1_latch = True

        # IN1 forces OUT1 OFF
        if IN1:
            out1_latch = False

        # IN2 forces OUT0 ON again
        if IN2:
            out1_latch = True


        # --- Output mapping (OUT7 → OUT0) ---
        outputs1 = [
            False,       # OUT7
            False,       # OUT6
            False,       # OUT5
            False,       # OUT4
            False,       # OUT3
            False,       # OUT2
            out1_latch,  # OUT1
            out0_latch   # OUT0
        ]

        controller.setMappedValue("digital_outputs1", outputs1)
        time.sleep(0.05)
