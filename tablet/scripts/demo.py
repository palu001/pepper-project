import sys
import time
import os
import random
import argparse

global user

try:
    sys.path.insert(0, os.getenv('MODIM_HOME')+'/src/GUI')
except Exception as e:
    print("Please set MODIM_HOME environment variable to MODIM folder.")
    sys.exit(1)

try:
    sys.path.insert(1, '/home/robot/playground/Pepper-Interaction/project-pepper')
except Exception as e:
    print("Please set HOME environment variable to plaground folder.")
    sys.exit(1)

# Set MODIM_IP to connnect to remote MODIM server

import ws_client
from ws_client import *

def i1():

    im.init()
    lan = im.ask('language')

    if lan == "it":
        im.setProfile(['*','*','it','*'])

    q = 'choose-activity'
    a = im.ask(q)
    while a != "exit":
        if a == "meteo":
            while a != "back":
                q = "choose-" + str(random.choice(["sunny", "cloudy", "snow", "stormy", "foggy", "rainy", "windy"]))
                a = im.ask(q)
            a = im.ask("choose-activity")

        elif a == "news":
            # list_news = database.patients[user]["tablet"]
            # count, a = max(list_news)
            while a != "back":
                a = im.ask("choose-topic")
                if a == "politics":
                    im.ask("choose-politics")
                elif a == "sport":
                    im.ask("choose-sport")
                elif a == "health":
                    im.ask("choose-health")
                elif a == "science":
                    im.ask("choose-science")    
                elif a == "entertainment":
                    im.ask("choose-entertainment")
            
            a = im.ask("choose-activity")

        elif a == "game":
            try_again = True
            while try_again:
                a = im.ask("game-intro")
                if a == "play":
                    points = 0
                    a = im.ask("2-phrases-part1", timeout= 999)
                    if a == "cat":
                        points+=1
                    a = im.ask("2-phrases-part2",  timeout= 999)
                    if a == "antarctica":
                        points+=1
                    a = im.ask("2-maths-part1",  timeout= 999)
                    if a == "sette":
                        points+=1
                    a = im.ask("2-maths-part2",  timeout= 999)
                    if a == "tre":
                        points+=1
                    a = im.ask("2-images-part1",  timeout= 999)
                    if a == "tulip":
                        points+=1
                    a = im.ask("2-images-part2",  timeout= 999)
                    if a == "amatriciana":
                        points+=1
                    
                    if points>=4:
                        im.execute("positive")
                        try_again = False
                    else:
                        a = im.ask("negative", timeout=999)
                        if a == "try":
                            try_again = True

                        elif a == "back":
                            try_again = False

            a = im.ask("choose-activity")

    im.execute('goodbye')
    
    #im.init()




if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--user", type=str, required=True, help="user name")

    args = parser.parse_args()
    user = args.user    

    mws = ModimWSClient()

    # local execution
    mws.setDemoPathAuto(__file__)
    # remote execution
    # mws.setDemoPath('<ABSOLUTE_DEMO_PATH_ON_REMOTE_SERVER>')

    mws.run_interaction(i1)


