#!/usr/bin/env python
# -*- coding: utf-8 -*-

import qi
import argparse
import sys
import os
import time
import signal
from classes.motion_manager import MotionManager
from classes.cinema_database import CinemaDatabase
from classes.cinema_assistant import CinemaAssistant

try:
    sys.path.insert(0, os.getenv('MODIM_HOME')+'/src/GUI')
except Exception as e:
    print("Please set MODIM_HOME environment variable to MODIM folder.")
    sys.exit(1)

from ws_client import *

def init_client():
    im.init()

def delete_db():
    DB_PATH = "data/cinema.db"

    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("[INFO] File cancellato.")
    else:
        print("[INFO] File non esiste o è già stato cancellato.")



def main():
 
    parser = argparse.ArgumentParser()
    parser.add_argument("--pip", type=str, default=os.environ.get('PEPPER_IP', '127.0.0.1'), help="Robot IP")
    parser.add_argument("--pport", type=int, required=True, help="Naoqi port")
    args = parser.parse_args()

    project_path = os.path.dirname(os.path.abspath(__file__))

    try:
        connection_url = "tcp://{}:{}".format(args.pip, args.pport)
        app = qi.Application(["Cinema Assistant", "--qi-url=" + connection_url])
    except RuntimeError:
        print("Could not connect to NAOqi.")
        sys.exit(1)

    app.start()
    session = app.session
    print("Successfully connected to the robot at {}:{}".format(args.pip, args.pport))

    ALMemory = session.service("ALMemory")
    ALMotion = session.service("ALMotion")
    ALAnimation = session.service("ALAnimationPlayer")
    

    
    db = CinemaDatabase(project_path)
    db.initialize_database()
    #Initialize tablet

    mws = ModimWSClient()
    path = os.path.join(project_path,"tablet/placeholder/another")
    
    mws.setDemoPathAuto(path)
    mws.run_interaction(init_client)
    mws.cconnect()

    motion = MotionManager(ALMotion)
    try:
        cinema_assistant = CinemaAssistant(ALAnimation,ALMemory, db, mws , motion)
    except Exception as e:
        print("Failed to initialize Cinema Assistant:", e)
        sys.exit(1)
    try:
        service_id = session.registerService("CinemaAssistantApp", cinema_assistant)
        print("Cinema Assistant service registered with ID:", service_id)
    except Exception as e:
        print("Failed to register Cinema Assistant service:", e)
        sys.exit(1)
    
    ALDialog = session.service("ALDialog")
    try: 
        topic_path = os.path.join(project_path, "topicFiles", "main.top")
        topic_name = ALDialog.loadTopic(topic_path.encode('utf-8'))
        ALDialog.activateTopic(topic_name)
        ALDialog.subscribe("cinema_assistant")
    except Exception as e:
        print("Failed to load or activate dialog topic:", e)
        sys.exit(1)

    function_sub = ALMemory.subscriber("cinema/function")
    function_sub.signal.connect(cinema_assistant.handle_function)

    tablet_sub = ALMemory.subscriber("cinema/tablet")
    tablet_sub.signal.connect(cinema_assistant.handle_tablet)

    print("Cinema Assistant is running...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")
        ALDialog.unsubscribe("cinema_assistant")
        ALDialog.deactivateTopic(topic_name)
        ALDialog.unloadTopic(topic_name)
        print("Dialog topic stopped and unloaded.")
        session.unregisterService(service_id)
        print("CinemaAssistantApp service unregistered.")
        
        app.stop()
        print("Application stopped.")
        delete_db()
 


if __name__ == "__main__":
    main()

