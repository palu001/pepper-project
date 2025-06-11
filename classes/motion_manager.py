#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Motion Manager for Cinema Assistant Pepper Robot
Handles all physical movements, gestures, and animations
"""

import time
import random

def greeting_gesture():
    """Perform a welcoming greeting gesture"""
    try:
        from main import ALMotion
        
        # Wave gesture
        names = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll"]
        angles = [-0.5, -0.3, 1.0, 0.5]
        times = [1.0, 1.0, 1.0, 1.0]
        isAbsolute = True
        
        ALMotion.angleInterpolation(names, angles, times, isAbsolute)
        
        # Wave motion
        for _ in range(3):
            ALMotion.angleInterpolation(["RElbowRoll"], [0.2], [0.3], True)
            ALMotion.angleInterpolation(["RElbowRoll"], [0.8], [0.3], True)
        
        # Return to neutral position
        ALMotion.angleInterpolation(names, [1.5, -0.15, 0.0, 0.0], [1.5], True)
        
    except Exception as e:
        print("Could not perform greeting gesture: {}".format(e))

def point_direction(direction_type):
    """Point towards different areas of the cinema"""
    try:
        from main import ALMotion
        
        # Direction mappings (angles in radians)
        directions = {
            "bathroom": {"yaw": 0.5, "pitch": -0.2},
            "restroom": {"yaw": 0.5, "pitch": -0.2},
            "screen": {"yaw": 0.0, "pitch": 0.0},
            "theater": {"yaw": 0.0, "pitch": 0.0},
            "concession": {"yaw": -0.7, "pitch": -0.1},
            "snacks": {"yaw": -0.7, "pitch": -0.1},
            "exit": {"yaw": 1.0, "pitch": -0.2},
            "entrance": {"yaw": -1.0, "pitch": -0.2},
            "box office": {"yaw": -0.5, "pitch": -0.1},
            "tickets": {"yaw": -0.5, "pitch": -0.1}
        }
        
        direction_info = directions.get(direction_type.lower(), {"yaw": 0.0, "pitch": 0.0})
        
        # Look towards the direction
        ALMotion.angleInterpolation(["HeadYaw", "HeadPitch"], 
                                  [direction_info["yaw"], direction_info["pitch"]], 
                                  [1.0, 1.0], True)
        
        # Point with right arm
        point_names = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll"]
        point_angles = [-0.5, -0.2, direction_info["yaw"], 0.3]
        ALMotion.angleInterpolation(point_names, point_angles, [1.5], True)
        
        time.sleep(2)  # Hold the pointing pose
        
        # Return to neutral
        ALMotion.angleInterpolation(point_names, [1.5, -0.15, 0.0, 0.0], [1.0], True)
        ALMotion.angleInterpolation(["HeadYaw", "HeadPitch"], [0.0, 0.0], [1.0], True)
        
    except Exception as e:
        print("Could not point direction: {}".format(e))

def concession_gesture():
    """Gesture showing eating/drinking motions"""
    try:
        from main import ALMotion
        
        # Mimic eating popcorn
        names = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll", "RWristYaw"]
        
        # Bring hand to mouth level
        angles1 = [-0.8, -0.1, 0.5, 1.2, -0.5]
        ALMotion.angleInterpolation(names, angles1, [1.0], True)
        
        # Eating motion
        for _ in range(2):
            angles2 = [-0.6, -0.1, 0.5, 1.0, -0.5]
            ALMotion.angleInterpolation(names, angles2, [0.3], True)
            angles3 = [-0.8, -0.1, 0.5, 1.2, -0.5]
            ALMotion.angleInterpolation(names, angles3, [0.3], True)
        
        # Return to neutral
        ALMotion.angleInterpolation(names, [1.5, -0.15, 0.0, 0.0, 0.0], [1.0], True)
        
    except Exception as e:
        print("Could not perform concession gesture: {}".format(e))

def photo_pose():
    """Strike a pose for photos"""
    try:
        from main import ALMotion
        
        poses = [
            # Peace sign pose
            {
                "names": ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll", 
                         "LShoulderPitch", "LShoulderRoll", "LElbowYaw", "LElbowRoll"],
                "angles": [-0.5, -0.3, 1.0, 0.8, -0.5, 0.3, -1.0, -0.8]
            },
            # Welcome pose
            {
                "names": ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll",
                         "LShoulderPitch", "LShoulderRoll", "LElbowYaw", "LElbowRoll"],
                "angles": [0.0, -0.8, 0.0, 0.3, 0.0, 0.8, 0.0, -0.3]
            },
            # Thumbs up
            {
                "names": ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll"],
                "angles": [-0.3, -0.1, 0.0, 0.2]
            }
        ]
        
        # Choose random pose
        pose = random.choice(poses)
        ALMotion.angleInterpolation(pose["names"], pose["angles"], [1.5], True)
        
        # Hold pose for photo
        time.sleep(3)
        
        # Return to neutral
        neutral_names = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll",
                        "LShoulderPitch", "LShoulderRoll", "LElbowYaw", "LElbowRoll"]
        neutral_angles = [1.5, -0.15, 0.0, 0.0, 1.5, 0.15, 0.0, 0.0]
        ALMotion.angleInterpolation(neutral_names, neutral_angles, [1.0], True)
        
    except Exception as e:
        print("Could not perform photo pose: {}".format(e))

def emergency_gesture():
    """Alert gesture for emergencies"""
    try:
        from main import ALMotion
        
        # Raise both arms to get attention
        names = ["RShoulderPitch", "RShoulderRoll", "LShoulderPitch", "LShoulderRoll"]
        angles = [-1.0, -0.3, -1.0, 0.3]
        
        # Wave both arms
        for _ in range(4):
            ALMotion.angleInterpolation(names, angles, [0.5], True)
            ALMotion.angleInterpolation(names, [-0.5, -0.1, -0.5, 0.1], [0.5], True)
        
        # Return to neutral
        ALMotion.angleInterpolation(names, [1.5, -0.15, 1.5, 0.15], [1.0], True)
        
    except Exception as e:
        print("Could not perform emergency gesture: {}".format(e))

def thinking_gesture():
    """Gesture for when Pepper is "thinking" """
    try:
        from main import ALMotion
        
        # Hand to chin thinking pose
        names = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll"]
        angles = [-0.7, -0.1, 0.8, 1.0]
        
        ALMotion.angleInterpolation(names, angles, [1.0], True)
        time.sleep(2)
        
        # Return to neutral
        ALMotion.angleInterpolation(names, [1.5, -0.15, 0.0, 0.0], [1.0], True)
        
    except Exception as e:
        print("Could not perform thinking gesture: {}".format(e))

def excited_gesture():
    """Show excitement for movie recommendations"""
    try:
        from main import ALMotion
        
        # Clapping motion
        names = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll",
                "LShoulderPitch", "LShoulderRoll", "LElbowYaw", "LElbowRoll"]
        
        # Bring hands together
        angles1 = [0.0, -0.5, 0.0, 1.5, 0.0, 0.5, 0.0, -1.5]
        ALMotion.angleInterpolation(names, angles1, [0.8], True)
        
        # Clapping motion
        for _ in range(3):
            angles2 = [0.0, -0.3, 0.0, 1.2, 0.0, 0.3, 0.0, -1.2]
            ALMotion.angleInterpolation(names, angles2, [0.2], True)
            ALMotion.angleInterpolation(names, angles1, [0.2], True)
        
        # Return to neutral
        neutral = [1.5, -0.15, 0.0, 0.0, 1.5, 0.15, 0.0, 0.0]
        ALMotion.angleInterpolation(names, neutral, [1.0], True)
        
    except Exception as e:
        print("Could not perform excited gesture: {}".format(e))

def look_around():
    """Look around the cinema environment"""
    try:
        from main import ALMotion
        
        # Look left, center, right sequence
        positions = [
            [0.8, -0.1],   # Left
            [0.0, 0.0],    # Center
            [-0.8, -0.1],  # Right
            [0.0, 0.0]     # Back to center
        ]
        
        for pos in positions:
            ALMotion.angleInterpolation(["HeadYaw", "HeadPitch"], pos, [1.0], True)
            time.sleep(0.5)
            
    except Exception as e:
        print("Could not perform look around: {}".format(e))

def dance_move():
    """Simple dance move for entertainment"""
    try:
        from main import ALMotion
        
        # Simple arm dance
        moves = [
            # Move 1
            {
                "names": ["RShoulderPitch", "RShoulderRoll", "LShoulderPitch", "LShoulderRoll"],
                "angles": [0.0, -0.8, 0.0, 0.8]
            },
            # Move 2  
            {
                "names": ["RShoulderPitch", "RShoulderRoll", "LShoulderPitch", "LShoulderRoll"],
                "angles": [-0.5, -0.3, -0.5, 0.3]
            },
            # Move 3
            {
                "names": ["RShoulderPitch", "RShoulderRoll", "LShoulderPitch", "LShoulderRoll"],
                "angles": [0.5, -0.1, 0.5, 0.1]
            }
        ]
        
        # Perform dance sequence
        for move in moves:
            ALMotion.angleInterpolation(move["names"], move["angles"], [0.8], True)
            time.sleep(0.2)
        
        # Return to neutral
        neutral_names = ["RShoulderPitch", "RShoulderRoll", "LShoulderPitch", "LShoulderRoll"]
        neutral_angles = [1.5, -0.15, 1.5, 0.15]
        ALMotion.angleInterpolation(neutral_names, neutral_angles, [1.0], True)
        
    except Exception as e:
        print("Could not perform dance move: {}".format(e))

def idle_animation():
    """Subtle idle movements to appear more lifelike"""
    try:
        from main import ALMotion
        
        # Subtle breathing-like movement
        ALMotion.angleInterpolation(["HeadPitch"], [-0.1], [2.0], True)
        time.sleep(1)
        ALMotion.angleInterpolation(["HeadPitch"], [0.0], [2.0], True)
        
        # Occasional small head movements
        if random.random() < 0.3:  # 30% chance
            direction = random.choice([-0.2, 0.2])
            ALMotion.angleInterpolation(["HeadYaw"], [direction], [1.0], True)
            time.sleep(0.5)
            ALMotion.angleInterpolation(["HeadYaw"], [0.0], [1.0], True)
            
    except Exception as e:
        print("Could not perform idle animation: {}".format(e))

def farewell_wave():
    """Wave goodbye to customers"""
    try:
        from main import ALMotion
        
        # Raise arm for waving
        names = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll"]
        angles = [-0.5, -0.3, 1.0, 0.5]
        ALMotion.angleInterpolation(names, angles, [1.0], True)
        
        # Wave motion
        for _ in range(4):
            ALMotion.angleInterpolation(["RElbowRoll"], [0.2], [0.3], True)
            ALMotion.angleInterpolation(["RElbowRoll"], [0.8], [0.3], True)
        
        # Return to neutral
        ALMotion.angleInterpolation(names, [1.5, -0.15, 0.0, 0.0], [1.5], True)
        
    except Exception as e:
        print("Could not perform farewell wave: {}".format(e))