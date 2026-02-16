import time
from Controller import UDP_Controller, DataType

if __name__ == "__main__":
    controller = UDP_Controller()

    # Add AO1 as an Analog Output (int)
    controller.addVariable("analog_inputs1", "int", 0)
    controller.addVariable("analog_inputs2", "int", 0)
    controller.addVariable("analog_inputs3", "int", 0)
    controller.addVariable("analog_inputs4", "int", 0)
    controller.addVariable("analog_outputs1", DataType.INT, 0)
    controller.addVariable("analog_outputs2", "int", 0)
    controller.addVariable("analog_outputs3", "int", 0)
    controller.addVariable("analog_outputs4", "int", 0)
    controller.addVariable("digital_inputs1", "byte", 0)
    controller.addVariable("digital_outputs1", "byte", 0)
    controller.addVariable("digital_inputs2", "byte", 0)
    controller.addVariable("digital_outputs2", "byte", 0)

    # Write a value to AO1 (example: 12000)
    controller.start()

    print("Waiting for Simumatik to connect (poll)...")

    # keep writing (ensures update is sent once Simumatik polls)
    value = 12000

    while True:
        controller.setValue("analog_outputs1", value)
        print(f"Writing analog_outputs1 = {value}")
        time.sleep(0.2)