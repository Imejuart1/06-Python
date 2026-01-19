import time
from Controller import UDP_Controller

if __name__ == "__main__":
    controller = UDP_Controller()

    # Digital input and output
    controller.addVariable("digital_inputs1", "byte", 0)
    controller.addVariable("digital_outputs1", "byte", 0)
    controller.start()

    # Force OUT0 = TRUE immediately
    controller.setMappedValue(
        "digital_outputs1",
        [False, False, False, False, False, False, True, True]  # OUT0 = True
    )

    count = 0
    prev_IN0 = False

    while True:
        inputs1 = controller.getMappedValue("digital_inputs1")

        # IN0 = bit 0 (LSB)
        IN0 = inputs1[-1]

        # Rising edge detection (0 → 1)
        if IN0 and not prev_IN0:
            count += 1
            print(f"IN0 count: {count}")

        prev_IN0 = IN0
        time.sleep(0.05)
