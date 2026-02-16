import time
from Controller import UDP_Controller

if __name__ == "__main__":
    controller = UDP_Controller()

    controller.addVariable("digital_inputs1", "byte", 0)
    controller.addVariable("digital_inputs2", "byte", 0)
    controller.addVariable("digital_outputs2", "byte", 0)
    controller.addVariable("digital_outputs1", "byte", 0)
    controller.start()

    latched_out0 = False

    while True:
        inputs = controller.getMappedValue("digital_inputs1")

        # Bit mapping (LSB at end of list)
        IN0 = inputs[-1]
        IN1 = inputs[-2]

        # Default outputs
        OUT0 = False
        OUT1 = False

        # Latch OUT0 when IN1 = 1
        if IN1:
            latched_out0 = True

        # Apply latch
        if latched_out0:
            OUT0 = True

        # Override when IN0 = 1
        if IN0:
            OUT0 = False
            OUT1 = True

        controller.setMappedValue(
            "digital_outputs1",
            [False, False, False, False, False, False, OUT1, OUT0]
        )

        time.sleep(0.05)
