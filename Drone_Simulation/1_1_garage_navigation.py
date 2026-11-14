from djitellopySim import Tello
import time

drone = Tello()
drone.connect()
drone.takeoff()

drone.rotate_clockwise(50)
drone.set_speed(100)  # Tello max speed is 100 cm/s (pysimverse used 200)
drone.move_forward(350)

drone.land()
drone.end()
time.sleep(1)