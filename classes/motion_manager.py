class MotionManager(object):
    def __init__(self, motion_proxy):
        self.motion = motion_proxy

    def greeting(self):
        try:
            # Giunti coinvolti
            names = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll"]
            
            # Salva le posizioni iniziali
            initial_angles = self.motion.getAngles(names, True)

            # Movimento iniziale per preparare il saluto
            angles = [-0.5, -0.3, 1.0, 0.5]
            self.motion.angleInterpolation(names, angles, [1.0]*4, True)

            # Movimento del saluto (3 volte avanti e indietro del gomito)
            for _ in range(3):
                self.motion.angleInterpolation(["RElbowRoll"], [0.2], [0.3], True)
                self.motion.angleInterpolation(["RElbowRoll"], [0.8], [0.3], True)

            # Movimento finale prima del rientro
            self.motion.angleInterpolation(names, [1.5, -0.15, 0.0, 0.0], 1.5, True)

            # Ritorna alla posizione iniziale
            self.motion.angleInterpolation(names, initial_angles, [1.0]*4, True)

        except Exception as e:
            print("Greeting failed:", e)



    def point_direction(self, direction_type, screen_number=None):
        try:
            # Base mapping for general locations (relative to robot's initial orientation)
            mapping = {
                "bathroom": (1.57, -0.2),      # 90 degrees right
                "concession": (-1.57, -0.1),   # 90 degrees left
                "exit": (0.0, -0.2),           # Straight ahead
                "entrance": (3.14, -0.2),      # Behind (180 degrees)
                "box_office": (-1.57, -0.1)    # 90 degrees left (ticket office on left)
            }
            
            # Screen-specific mapping based on screen number
            if direction_type.lower() == "screen" and screen_number:
                screen_mapping = {
                    1: (-0.52, -0.1),   # Screen 1 - 30 degrees left
                    2: (0.0, 0.0),      # Screen 2 - straight ahead
                    3: (0.52, -0.1),    # Screen 3 - 30 degrees right
                    4: (-1.05, -0.1),   # Screen 4 - 60 degrees left
                    5: (1.05, -0.1),    # Screen 5 - 60 degrees right
                    6: (-1.57, -0.2),   # Screen 6 - 90 degrees left
                    7: (1.57, -0.2),    # Screen 7 - 90 degrees right
                    8: (0.0, -0.5),     # Screen 8 - straight but lower (upstairs?)
                }
                target_angle, pitch = screen_mapping.get(screen_number, (0.0, 0.0))
            else:
                target_angle, pitch = mapping.get(direction_type.lower(), (0.0, 0.0))
            
            # First, rotate the robot to face the direction
            if screen_number:
                print("[Motion] Rotating to face {} {}".format(direction_type, screen_number))
            else:
                print("[Motion] Rotating to face {}".format(direction_type))
            self.motion.moveTo(0.0, 0.0, target_angle)
            
            # Then point with head and arm in the direction (now should be straight ahead)
            self.motion.angleInterpolation(["HeadYaw", "HeadPitch"], [0.0, pitch], [1.0, 1.0], True)
            
            # Point with arm straight ahead after rotation
            point_names = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll"]
            point_angles = [-0.5, -0.2, 0.0, 0.3]  # Point straight ahead
            point_durations = [1.5, 1.5, 1.5, 1.5]
            
            self.motion.angleInterpolation(point_names, point_angles, point_durations, True)
            
            # Hold the pointing position
            import time
            time.sleep(2)
            
            # Return arm to neutral position
            neutral_angles = [1.5, -0.15, 0.0, 0.0]
            self.motion.angleInterpolation(point_names, neutral_angles, point_durations, True)
            
            # Reset head to center
            self.motion.angleInterpolation(["HeadYaw", "HeadPitch"], [0.0, 0.0], [1.0, 1.0], True)
            
        except Exception as e:
            print("Pointing failed:", e)

    def guide_to_location(self, location_type, screen_number=None):
        """
        Generalized function to guide to any location based on the pointing direction.
        For screens, uses the specific screen number to determine direction and path.
        """
        try:
            if screen_number:
                print("[Motion] Guiding to {} {}".format(location_type, screen_number))
            else:
                print("[Motion] Guiding to {}".format(location_type))
            
            # Store initial robot orientation to calculate return rotation
            initial_orientation = 0.0  # Assuming robot starts facing forward
            
            # General location direction mapping (rotation angles)
            direction_mapping = {
                "bathroom": 1.57,       # 90 degrees right
                "concession": -1.57,    # 90 degrees left
                "exit": 0.0,            # Straight ahead
                "entrance": 3.14,       # Behind (180 degrees)
                "box_office": -1.57     # 90 degrees left (ticket office on left)
            }
            
            # Screen-specific direction mapping
            screen_direction_mapping = {
                1: -0.52,    # Screen 1 - 30 degrees left
                2: 0.0,      # Screen 2 - straight ahead
                3: 0.52,     # Screen 3 - 30 degrees right
                4: -1.05,    # Screen 4 - 60 degrees left
                5: 1.05,     # Screen 5 - 60 degrees right
                6: -1.57,    # Screen 6 - 90 degrees left
                7: 1.57,     # Screen 7 - 90 degrees right
                8: 0.0,      # Screen 8 - straight ahead (special case)
            }
            
            # Get the target direction
            if location_type.lower() == "screen" and screen_number:
                target_rotation = screen_direction_mapping.get(screen_number, 0.0)
            else:
                target_rotation = direction_mapping.get(location_type.lower(), 0.0)
            
            # First, rotate to face the target direction
            if target_rotation != 0.0:
                print("[Motion] Rotating {} radians to face target".format(target_rotation))
                self.motion.moveTo(0.0, 0.0, target_rotation)
            
            # Define movement patterns (now all movements are forward since we've rotated)
            if location_type.lower() == "screen" and screen_number:
                # Screen-specific movement patterns (simplified - mostly forward movement)
                screen_movement_patterns = {
                    1: [(0.8, 0.0, 0.0), (0.6, 0.0, 0.0)],      # Screen 1
                    2: [(1.0, 0.0, 0.0), (0.0, 0.0, 1.57), (0.5, 0.0, 0.0)], # Screen 2 - special case
                    3: [(0.8, 0.0, 0.0), (0.6, 0.0, 0.0)],      # Screen 3
                    4: [(0.6, 0.0, 0.0), (0.8, 0.0, 0.0)],      # Screen 4
                    5: [(0.6, 0.0, 0.0), (0.8, 0.0, 0.0)],      # Screen 5
                    6: [(0.4, 0.0, 0.0), (1.0, 0.0, 0.0)],      # Screen 6
                    7: [(0.4, 0.0, 0.0), (1.0, 0.0, 0.0)],      # Screen 7
                    8: [(1.2, 0.0, 0.0), (0.3, 0.0, 0.0)],      # Screen 8
                }
                movements = screen_movement_patterns.get(screen_number, [(1.0, 0.0, 0.0)])
            else:
                # General location movement patterns (mostly forward movement)
                movement_patterns = {
                    "bathroom": [(0.8, 0.0, 0.0), (0.6, 0.0, 0.0)],
                    "concession": [(1.2, 0.0, 0.0), (0.4, 0.0, 0.0)],
                    "exit": [(1.5, 0.0, 0.0), (0.3, 0.0, 0.0)],
                    "entrance": [(1.0, 0.0, 0.0), (0.5, 0.0, 0.0)],
                    "box_office": [(0.8, 0.0, 0.0), (0.4, 0.0, 0.0)]
                }
                movements = movement_patterns.get(location_type.lower(), [(1.0, 0.0, 0.0)])
            
            # Execute movements
            total_rotation = target_rotation
            for x, y, theta in movements:
                self.motion.moveTo(x, y, theta)
                total_rotation += theta
            
            # Face customer at the end - calculate the rotation needed to face back
            self.face_customer(total_rotation)
            
        except Exception as e:
            if screen_number:
                print("[Motion] Failed to guide to {} {}: {}".format(location_type, screen_number, e))
            else:
                print("[Motion] Failed to guide to {}: {}".format(location_type, e))

    def face_customer(self, current_total_rotation=0.0):
        """
        Turn to face the customer, accounting for the robot's current orientation.
        current_total_rotation: total rotation accumulated during the guidance movement
        """
        try:
            # Calculate the rotation needed to face back to the customer
            # We want to face the opposite direction from where we came
            # This is more complex than just rotating 180 degrees (3.14 radians)
            # because we need to account for the total rotation made during guidance
            
            # The robot should turn to face back toward the starting position
            # If we've rotated X radians total, we need to rotate -X to face back
            return_rotation = -current_total_rotation
            
            print("[Motion] Rotating {} radians to face customer".format(return_rotation))
            self.motion.moveTo(0.0, 0.0, return_rotation)
            
        except Exception as e:
            print("[Motion] Failed to turn to face customer:", e)

    def emergency(self):
        try:
            names = ["RShoulderPitch", "RShoulderRoll", "LShoulderPitch", "LShoulderRoll"]
            for _ in range(3):
                self.motion.angleInterpolation(names, [-1.0, -0.3, -1.0, 0.3], [0.5], True)
                self.motion.angleInterpolation(names, [-0.5, -0.1, -0.5, 0.1], [0.5], True)
            self.motion.angleInterpolation(names, [1.5, -0.15, 1.5, 0.15], [1.0], True)
        except Exception as e:
            print("Emergency gesture failed:", e)

    def concession(self):
        try:
            # Giunti coinvolti per il gesto di concessione/indicazione
            names = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll", "RWristYaw"]

            # Salva le posizioni iniziali
            initial_angles = self.motion.getAngles(names, True)

            # Movimento per portare il braccio in avanti come a indicare un menu
            target_angles = [0.5, -0.3, 1.2, 0.4, 0.0]
            self.motion.angleInterpolation(names, target_angles, [1.0]*5, True)

            # Piccolo gesto con il polso (simile a un invito a scegliere)
            self.motion.angleInterpolation(["RWristYaw"], [0.5], [0.4], True)
            self.motion.angleInterpolation(["RWristYaw"], [-0.5], [0.4], True)
            self.motion.angleInterpolation(["RWristYaw"], [0.0], [0.3], True)

            # Pausa breve per enfatizzare il gesto
            self.motion.wait(0.5)

            # Ritorna alla posizione iniziale
            self.motion.angleInterpolation(names, initial_angles, [1.0]*5, True)

        except Exception as e:
            print("Concession gesture failed:", e)
