from djitellopySim import Tello
import time

drone = Tello()
drone.connect()
drone.set_speed(100)  # Tello max speed is 100 cm/s (pysimverse used 200)

# Leg 1 — pysimverse take_off(height=100, speed=200) -> takeoff, then climb
drone.takeoff()
drone.move_up(100)
drone.rotate_counter_clockwise(35)
drone.move_forward(400)
drone.land()

# Leg 2 — pysimverse take_off(height=50, speed=100) -> takeoff, then climb
drone.takeoff()
drone.move_up(50)
drone.rotate_clockwise(150)
drone.move_forward(470)
drone.land()

drone.end()
time.sleep(1)
