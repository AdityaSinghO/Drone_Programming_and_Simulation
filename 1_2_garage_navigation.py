from djitellopySim import Tello
import time

drone = Tello()
drone.connect()
drone.set_speed(100)  # Tello max speed is 100 cm/s (pysimverse used 200)

# Leg 1 — pysimverse take_off(height=100, speed=100) -> takeoff, then climb
drone.takeoff()
drone.move_up(100)
drone.rotate_counter_clockwise(80)
drone.move_forward(240)
drone.land()

# Leg 2
drone.takeoff()
drone.move_up(100)
drone.rotate_clockwise(140)
drone.move_forward(270)
drone.land()

# Leg 3
drone.takeoff()
drone.move_up(100)
drone.rotate_clockwise(15)
drone.move_forward(270)

drone.land()
drone.end()
time.sleep(1)
