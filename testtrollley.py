import time
from Controller import UDP_Controller

if __name__ == "__main__":
    # Create UDP controller
    controller = UDP_Controller()
    controller.addVariable("digital_inputs1", "byte", 0)
    controller.addVariable("digital_inputs2", "byte", 0)
    controller.addVariable("digital_outputs1", "byte", 0)
    controller.addVariable("digital_outputs2", "byte", 0)
    controller.start()

    # --- Initialize ---
    start_time = time.time()
    out2 = True   # OUT2 = 1 immediately
    out3 = False  # OUT3 = 0 initially
    stage_done = False

    while True:
        # --- Time-based logic ---
        elapsed = time.time() - start_time

        if elapsed >= 10 and not stage_done:
            # After 2 seconds → switch states
            out2 = False
            out3 = True
            stage_done = True

        # --- Prepare output bits (OUT7 ... OUT0) ---
        # OUT3 = out3, OUT2 = out2
        outputs1 = [False, False, False, False, out3, out2, False, False]

        # --- Write outputs ---
        controller.setMappedValue("digital_outputs1", outputs1)

        time.sleep(0.01)
