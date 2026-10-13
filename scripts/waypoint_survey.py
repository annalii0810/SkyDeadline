
#!/usr/bin/env python3
"""SkyDeadline Phase I.0 - Mission 2 SITL waypoint survey."""

import math
import time
from pymavlink import mavutil

CONNECTION = "udpin:127.0.0.1:14550"
ALTITUDE = 10.0
TOLERANCE = 1.5
MIN_BATTERY = 20
WAYPOINT_TIMEOUT = 90

# North/East offsets from the recorded starting position.
ROUTE = [(10, 0), (10, 10), (0, 10), (0, 0)]


class Survey:
    def __init__(self):
        self.master = mavutil.mavlink_connection(
            CONNECTION,
            source_system=250,
            source_component=1,
        )
        self.state = {}
        self.last_seen = {}
        self.armed_once = False

    def update(self, duration=1):
        end = time.monotonic() + duration

        while time.monotonic() < end:
            msg = self.master.recv_match(
                blocking=True, timeout=0.2
            )
            if msg is None:
                continue

            now = time.monotonic()
            kind = msg.get_type()

            if kind == "LOCAL_POSITION_NED":
                self.state["position"] = (
                    msg.x, msg.y, msg.z
                )
                self.last_seen["position"] = now

            elif kind == "SYS_STATUS":
                self.state["battery"] = msg.battery_remaining
                self.last_seen["battery"] = now

            elif kind == "HEARTBEAT" and msg.get_srcComponent() == 1:
                self.state["armed"] = bool(
                    msg.base_mode &
                    mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED
                )
                self.state["mode"] = mavutil.mode_string_v10(msg)
                self.last_seen["heartbeat"] = now

            elif kind == "STATUSTEXT":
                print("Autopilot:", msg.text)

        return self.state

    def check(self, expected_mode=None):
        self.update()
        now = time.monotonic()

        for key in ("heartbeat", "position"):
            if now - self.last_seen.get(key, 0) > 5:
                raise RuntimeError(f"Stale {key} telemetry")

        battery = self.state.get("battery")
        if battery is not None and 0 <= battery < MIN_BATTERY:
            raise RuntimeError("Battery below safety threshold")

        if expected_mode and self.state.get("mode") != expected_mode:
            raise RuntimeError(
                "Unexpected mode: " + str(self.state.get("mode"))
            )

        return self.state

    def connect(self):
        hb = self.master.wait_heartbeat(timeout=15)
        if hb is None or hb.get_srcComponent() != 1:
            raise RuntimeError("Autopilot heartbeat missing")

        self.master.target_system = hb.get_srcSystem()
        self.master.target_component = hb.get_srcComponent()

        print("Connected to ArduCopter")
        self.update(3)
        self.check()

    def set_mode(self, mode, timeout=10):
        mapping = self.master.mode_mapping()
        if mode not in mapping:
            raise RuntimeError(f"Unsupported mode: {mode}")

        self.master.set_mode(mapping[mode])
        deadline = time.monotonic() + timeout

        while time.monotonic() < deadline:
            self.update()
            if self.state.get("mode") == mode:
                print("Mode confirmed:", mode)
                return

        raise TimeoutError(f"{mode} mode not confirmed")

    def wait_armed(self, expected, timeout=15):
        deadline = time.monotonic() + timeout

        while time.monotonic() < deadline:
            self.check()
            if self.state.get("armed") is expected:
                return

        raise TimeoutError("Arming state confirmation timed out")

    def wait_takeoff(self, origin):
        deadline = time.monotonic() + 45
        stable = 0

        while time.monotonic() < deadline:
            state = self.check("GUIDED")

            if not state.get("armed"):
                raise RuntimeError("Disarmed during takeoff")

            x, y, z = state["position"]
            height = origin[2] - z

            print(f"Takeoff height: {height:.2f} m")

            if abs(height - ALTITUDE) <= TOLERANCE:
                stable += 1
                if stable >= 3:
                    print("TAKEOFF VERIFIED")
                    return
            else:
                stable = 0

        raise TimeoutError("Takeoff altitude not reached")

    def send_target(self, target):
        north, east, down = target

        self.master.mav.set_position_target_local_ned_send(
            0,
            self.master.target_system,
            self.master.target_component,
            mavutil.mavlink.MAV_FRAME_LOCAL_NED,
            0x0DF8,
            north, east, down,
            0, 0, 0,
            0, 0, 0,
            0, 0,
        )

    def waypoint(self, number, target):
        deadline = time.monotonic() + WAYPOINT_TIMEOUT
        stable = 0

        while time.monotonic() < deadline:
            state = self.check("GUIDED")

            if not state.get("armed"):
                raise RuntimeError("Unexpected disarming")

            self.send_target(target)

            position = state["position"]
            error = math.dist(position, target)

            print(
                f"WP{number}: position={position}, "
                f"error={error:.2f} m"
            )

            if error <= TOLERANCE:
                stable += 1
                if stable >= 3:
                    print(f"WAYPOINT {number} VERIFIED")
                    return
            else:
                stable = 0

        raise TimeoutError(f"Waypoint {number} timed out")

    def land(self):
        print("Requesting LAND")
        self.set_mode("LAND")
        self.wait_armed(False, timeout=90)
        print("LANDING AND DISARM CONFIRMED")

    def run(self):
        try:
            self.connect()
            initial = self.check()

            if initial.get("armed"):
                raise RuntimeError("Vehicle must start disarmed")

            origin = initial["position"]
            print("Starting position:", origin)

            self.set_mode("GUIDED")

            self.master.arducopter_arm()
            self.wait_armed(True)
            self.armed_once = True
            print("ARMED")

            self.master.mav.command_long_send(
                self.master.target_system,
                self.master.target_component,
                mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
                0, 0, 0, 0, 0, 0, 0, ALTITUDE
            )

            self.wait_takeoff(origin)

            for number, (north, east) in enumerate(ROUTE, 1):
                target = (
                    origin[0] + north,
                    origin[1] + east,
                    origin[2] - ALTITUDE,
                )
                self.waypoint(number, target)

            print("ALL FOUR WAYPOINTS VERIFIED")
            self.land()
            print("MISSION 2 FLIGHT COMPLETE")

        finally:
            try:
                if self.armed_once and self.state.get("armed"):
                    self.land()
            except Exception as exc:
                print("WARNING: Landing unconfirmed:", exc)
                print("Check MAVProxy and SITL immediately.")
            self.master.close()


if __name__ == "__main__":
    Survey().run()

