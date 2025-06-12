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


    def point_direction(self, direction_type):
        try:
            mapping = {
                "bathroom": (0.5, -0.2), "screen": (0.0, 0.0), "concession": (-0.7, -0.1),
                "exit": (1.0, -0.2), "entrance": (-1.0, -0.2), "box office": (-0.5, -0.1)
            }
            yaw, pitch = mapping.get(direction_type.lower(), (0.0, 0.0))
            self.motion.angleInterpolation(["HeadYaw", "HeadPitch"], [yaw, pitch], [1.0, 1.0], True)
            point_names = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll"]
            point_angles = [-0.5, -0.2, yaw, 0.3]
            self.motion.angleInterpolation(point_names, point_angles, [1.5], True)
        except Exception as e:
            print("Pointing failed:", e)

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
            names = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll", "RWristYaw"]
            self.motion.angleInterpolation(names, [-0.8, -0.1, 0.5, 1.2, -0.5], [1.0], True)
            for _ in range(2):
                self.motion.angleInterpolation(names, [-0.6, -0.1, 0.5, 1.0, -0.5], [0.3], True)
                self.motion.angleInterpolation(names, [-0.8, -0.1, 0.5, 1.2, -0.5], [0.3], True)
            self.motion.angleInterpolation(names, [1.5, -0.15, 0.0, 0.0, 0.0], [1.0], True)
        except Exception as e:
            print("Concession gesture failed:", e)
