from djitellopySim import Tello
import time

drone = Tello()
drone.connect()

drone.takeoff()

time.sleep(3)
drone.land()
drone.end()
time.sleep(1)
