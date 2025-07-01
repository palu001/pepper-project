from classes.cinema_map import CinemaMap
import math
class MotionManager(object):
    def __init__(self, motion_proxy):
        self.motion = motion_proxy
        self.cinema_map = CinemaMap()
        self.current_orientation=0

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



    def point_and_describe_direction(self, target_location, screen_number=None):
        """Point to a location and give verbal directions"""
        try:
            # Determine target node
            if target_location.lower() == "screen" and screen_number:
                target_node = "screen{}".format(screen_number)
            else:
                target_node = self.cinema_map.location_mapping.get(target_location.lower())
                
            if not target_node or target_node not in self.cinema_map.nodes:
                print("Unknown location: {}".format(target_location))
                return "I'm not sure where that is."
                
            # Find path from current position to target
            path = self.cinema_map.find_shortest_path(target_node)
            
            if not path or len(path) < 2:
                return "You're already there!"
                
            # Get next node in path for pointing direction
            next_node = path[1]
            
            # Calculate pointing angle for robot
            current_pos = self.cinema_map.nodes[self.cinema_map.current_position]
            next_pos = self.cinema_map.nodes[next_node]
            
            dx = next_pos[0] - current_pos[0]
            dy = next_pos[1] - current_pos[1]
            target_angle = math.atan2(dy, dx)
            if hasattr(self, 'current_orientation'):
                    relative_angle = target_angle - self.current_orientation
                    # Normalize angle to [-pi, pi]
                    relative_angle = math.atan2(math.sin(relative_angle), math.cos(relative_angle))
            else:
                # If no orientation tracking, use absolute angle
                relative_angle = target_angle
            # Point with robot
            self.motion.moveTo(0.0, 0.0, relative_angle)
            names = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll"]
            
            initial_angles = self.motion.getAngles(names, True)

            # Movimento iniziale per preparare il saluto
            angles = [-0.5, -0.3, 1.0, 0.5]
            self.motion.angleInterpolation(names, angles, [1.0]*4, True)

            # Ritorna alla posizione iniziale
            self.motion.angleInterpolation(names, initial_angles, [1.0]*4, True)
            
            # Generate verbal directi
            verbal_direction = "Go "
            
            # Add landmarks if available
            landmarks = self._get_landmarks_on_path(path)
            if landmarks:
                verbal_direction += ". {}".format(landmarks)
                
            # Hold pointing position briefly
            import time
            time.sleep(2)
            
            # Return to neutral and face customer
            self.motion.moveTo(0.0, 0.0, -relative_angle)
            
            return verbal_direction
            
        except Exception as e:
            print("Pointing failed:", e)
            return "I had trouble pointing in that direction."
    
    def _get_landmarks_on_path(self, path):
        """Generate landmark descriptions for the path"""
        landmarks = []
        
        for i, node in enumerate(path):
            if 'lobby_center' in node and node != path[-1]:
                landmarks.append("you'll pass the lobby_center")
            elif 'screen2_entrance' in node and node != path[-1]:
                landmarks.append("you'll pass the screen2_entrance")
            elif 'screen5_entrance' in node and node != path[-1]:
                landmarks.append("you'll pass the screen5_entrance")
            elif 'hallway_center' in node and node != path[-1]:
                landmarks.append("you'll pass the hallway_center")
            elif 'screen7_entrance' in node and node != path[-1]:
                landmarks.append("you'll pass the screen7_entrance")
                
        return ", ".join(landmarks) if landmarks else ""

    def guide_to_location(self, location_type, screen_number=None):
        """Guide to location using graph-based pathfinding"""
        try:
            # Determine target node
            if location_type.lower() == "screen" and screen_number:
                target_node = "screen{}".format(screen_number)
                print("[Motion] Guiding to screen {}".format(screen_number))
            else:
                target_node = self.cinema_map.location_mapping.get(location_type.lower())
                print("[Motion] Guiding to {}".format(location_type))
                
            if not target_node or target_node not in self.cinema_map.nodes:
                print("Unknown location: {}".format(location_type))
                return
                
            # Find shortest path
            path = self.cinema_map.find_shortest_path( target_node)
            if len(path)<2:
                print("Already there")
                return
            
            if not path:
                print("No path found to {}".format(target_node))
                return
                
            print("Path found: {}".format(" -> ".join(path)))
            
            # Execute movement along path
            for i in range(len(path) - 1):
                current_node = path[i]
                next_node = path[i + 1]
                
                # Calculate movement vector
                current_pos = self.cinema_map.nodes[current_node]
                next_pos = self.cinema_map.nodes[next_node]
                
                dx = next_pos[0] - current_pos[0]
                dy = next_pos[1] - current_pos[1]
                distance = math.sqrt(dx**2 + dy**2)
                target_angle = math.atan2(dy, dx)
                
                if hasattr(self, 'current_orientation'):
                    relative_angle = target_angle - self.current_orientation
                    # Normalize angle to [-pi, pi]
                    relative_angle = math.atan2(math.sin(relative_angle), math.cos(relative_angle))
                else:
                    # If no orientation tracking, use absolute angle
                    relative_angle = target_angle
            
                print("Moving from {} to {} (distance: {:.2f}m, target_angle: {:.2f} rad, relative_angle: {:.2f} rad)".format(
                    current_node, next_node, distance, target_angle, relative_angle))
                
                # Use relative movements
                # First rotate to face direction (relative turn)
                if abs(relative_angle) > 0.01:  # Only rotate if significant angle difference
                    self.motion.moveTo(0.0, 0.0, relative_angle)
                    # Update current orientation after rotation
                    if hasattr(self, 'current_orientation'):
                        self.current_orientation = target_angle

                # Then move forward
                self.motion.moveTo(distance, 0.0, 0.0)
                
                # Update current position
                self.cinema_map.current_position = next_node
            
            # Face customer at destination
            self.current_orientation+=math.pi
            if target_node!="entrance":
                self.face_customer()
            
        except Exception as e:
            print("Guidance failed:", e)
            
    def face_customer(self):
        """Turn to face the customer (assumes customer is behind robot after guidance)"""
        try:
            # Simple 180-degree turn to face customer
            self.motion.moveTo(0.0, 0.0, math.pi)
            
            # Reset head and arm to neutral position
            self.motion.angleInterpolation(["HeadYaw", "HeadPitch"], [0.0, 0.0], [1.0, 1.0], True)
            
            # Return arm to neutral position
            neutral_names = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll"]
            neutral_angles = [1.5, -0.15, 0.0, 0.0]
            self.motion.angleInterpolation(neutral_names, neutral_angles, [1.5]*4, True)
            
        except Exception as e:
            print("Failed to face customer:", e)

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
