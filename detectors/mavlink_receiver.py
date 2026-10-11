from pymavlink import mavutil
from detector_stub import detect_attack

connection = mavutil.mavlink_connection("udpin:0.0.0.0:14550")

print("Waiting for MAVLink heartbeat...")
connection.wait_heartbeat()
print("Connection to MAVLink!")

while True:
    msg = connection.recv_match(blocking=True)

    if msg is not None:
        print(msg)