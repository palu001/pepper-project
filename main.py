#!/usr/bin/env python
# -*- coding: utf-8 -*-

import qi
import argparse
import sys
import os
import time
from classes.motion_manager import *
from classes.database import *
from classes.handle_function import handle_cinema_functions, set_dependencies

# Global variables
project_path = None
ALMemory = None
ALDialog = None
tts_service = None
ALMotion = None
tablet_service = None
current_customer = None
db = None 

def main():
    global project_path, ALMemory, ALDialog, tts_service, ALMotion, tablet_service, db

    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--pip", type=str, default=os.environ.get('PEPPER_IP', '127.0.0.1'), 
                       help="Robot IP address")
    parser.add_argument("--pport", type=int, required=True, help="Naoqi port number")
    args = parser.parse_args()
    
    # Find project path
    project_path = os.path.dirname(os.path.abspath(__file__))

    # Crea istanza del database
    db = CinemaDatabase(project_path)
    
    # Connect to session
    try:
        connection_url = "tcp://{}:{}".format(args.pip, args.pport)
        print("Connecting to {}".format(connection_url))
        app = qi.Application(["Cinema Assistant", "--qi-url=" + connection_url])
    except RuntimeError:
        print("Can't connect to Naoqi at ip {} on port {}.".format(args.pip, args.pport))
        sys.exit(1)
    
    app.start()
    session = app.session
    
    # Initialize database
    db.initialize_database()
    
    # Create service connections
    ALDialog = session.service('ALDialog')
    ALMemory = session.service('ALMemory')
    ALMotion = session.service("ALMotion")
    tts_service = session.service("ALTextToSpeech")
    
    try:
        tablet_service = session.service("ALTabletService")
    except:
        print("Tablet service not available")
        tablet_service = None
    
    # Setup ALDialog with topic file
    topic_path = os.path.join(project_path, "topicFiles", "main.top")
    topf_path = topic_path.decode('utf-8')
    topic_name = ALDialog.loadTopic(topf_path.encode('utf-8'))
    ALDialog.activateTopic(topic_name)
    ALDialog.subscribe('cinema_assistant')
    
    for key in ALMemory.getDataList("cinema/"):
        ALMemory.insertData(key, "")    
    
    # Connect function handler
    function_sub = ALMemory.subscriber("cinema/function")
    function_sub.signal.connect(handle_cinema_functions)

    set_dependencies(ALMemory, db, tablet_service)
    
    print("Cinema Assistant is running... Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nTerminating Cinema Assistant...\n")
        ALDialog.unsubscribe('cinema_assistant')
        ALDialog.deactivateTopic(topic_name)
        ALDialog.unloadTopic(topic_name)
        return 0
        

if __name__ == "__main__":
    main()