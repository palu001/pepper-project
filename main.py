# -*- coding: utf-8 -*-
# main_cinema.py
from __future__ import division

import sys
import os

# Add the project root directory to the Python path
# This assumes main_cinema.py is directly in the project root
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import argparse
import qi 
import random
import time
import operator
from classes.database import Database

tablet = "./tablet"
scripts = "./scripts"

global session, index, database, ALDialog, topic_name, topic_path, name 

index = 1
name = ""

def handleLastAnswer(lastAnswer):
    global name, topic_name
    if "Hi" in lastAnswer:
        name = lastAnswer.split()[1].lower()
        if name not in database.patients:
            database.addPatient(name)
            tts_service.say("Nice to meet you!\n"+" "*5, _async=True)
        else:
            tts_service.say("Welcome back, %s!\n"+" "*5 % name, _async=True)

def main(session):
    stop_flag = False
    robot_position = (0,0)

    tts_service.setLanguage("English")
    tts_service.setVolume(1.0)
    tts_service.setParameter("speed", 1.0)
    tts_service.say("Searching for humans ..." + " "*5, _async=True)
    time.sleep(2)
    # Ricerca Uomo skippata per ora
    tts_service.say("Hello, I am Pepper, your cinema assistant.\n"+" "*5, _async=True)
    time.sleep(2)

    ALDialog.activateTopic(topic_name)
    ALDialog.subscribe('pepper_assistant')

    lastAnswer = ALMemory.subscriber("Dialog/LastAnswer")
    lastAnswer.signal.connect(handleLastAnswer)


    while not stop_flag:
        try:
           value = raw_input("Talk to robot (insert stop to finish the conversation) or touch him (LHand, RHand, HeadMiddle): ") 

        except KeyboardInterrupt:
            stop_flag = True
            ALDialog.unsubscribe('pepper_assistant')
            ALDialog.deactivateTopic(topic_name)
            ALDialog.unloadTopic(topic_name)

        if value == "stop":
            stop_flag = True
            ALDialog.unsubscribe('pepper_assistant')
            ALDialog.deactivateTopic(topic_name)
            ALDialog.unloadTopic(topic_name)
            tts_service.say("Goodbye! See you soon!" + " "*5, _async=True)
            time.sleep(2)
    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="127.0.0.1",
                        help="Robot's IP address. If on a robot or a local Pepper - use '127.0.0.1' (this is the default value).")
    parser.add_argument("--port", type=int, default=9559,
                        help="port number, the default value is OK in most cases")
   
    args = parser.parse_args()
    session = qi.Session()

    project_path = os.path.dirname(os.path.abspath(__file__))

    try:
        session.connect("tcp://{}:{}".format(args.ip, args.port))
    except RuntimeError:
        print ("\nCan't connect to Pepper at IP {} (port {}).\nPlease check your script's arguments."
               " Run with -h option for help.\n".format(args.ip, args.port))
        sys.exit(1)

    ALDialog = session.service('ALDialog')
    ALMemory = session.service('ALMemory')
    ALMotion = session.service("ALMotion")
    tts_service = session.service("ALTextToSpeech")

    # Setup ALDialog
    ALDialog.setLanguage('English')

    topic_path = os.path.join(project_path, "topicFiles", "main.top")
    
    topf_path = topic_path.decode('utf-8')
    topic_name = ALDialog.loadTopic(topf_path.encode('utf-8'))
    ALDialog.activateTopic(topic_name)
    ALDialog.subscribe('pepper_assistant')

    # Database
    database = Database()

    main(session)