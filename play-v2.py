from datetime import datetime
import pyautogui
import numpy as np
import cv2
from PIL import ImageGrab
import time
import math
import sys, getopt
from subprocess import call

minsBetweenCollects=10

#from collections import OrderedDict

# set the size of the tsumtsum game screen region within which we will operate
#   isolating the pyautogui locate functions to a screen_region speed up the functions
#   The offset values are from the center of the nox logo in the header of the window
region_offset_x=-20
region_offset_y=21
region_size_x=680
region_size_y=1100
isDebug=False

tsumRegion=(0, 0, 0, 0)

timeStarted = time.time()
lastClaimTimeCounter = 0
lastClaimTimeClock = "Never"
receivedAllCount = 0
heartCount = 0

# parse command-line arguments
argv = sys.argv
while len(argv) > 0:
    arg = argv.pop()
    #print(arg)
    if arg in ('-d', '--debug'):
        isDebug = True

# base_path='//kidspc/Users/Reid/Pictures/TsumTsum/'
base_path='//sagetv/TsumTsum/'
image_path=base_path+'images/'
#base_path='//sagetv/TsumTsum/'
rrdTool='C:/Program Files (x86)/rrdtool/rrdtool.exe'
rrdDbFile='C:\\Users\\Reid\\Pictures\\TsumTsum\\tracker.rrd'
rrdDbFileGraph='C\:\\Users\\Reid\\Pictures\\TsumTsum\\tracker.rrd'
rrdGraphPath='//sagetv/TsumTsum'


# Define the 'dictionary' variable to hold template image information
# structure: (nameKey, filePath, templateSensitivityValue)
clickablesDict = {'red_heart': [image_path+'red_heart.jpg', 0.6], #0.745  ** 0.65
                'empty_heart': [image_path+'heart_sent.jpg', 0.90],
                'close_button': [image_path+'close_button.jpg', 0.8],
                'close_button_error_code_7': [image_path+'close_button_error_code_7.jpg', 0.8],
                'claim_all_button': [image_path+'claim_all_button.jpg', 0.80],                                      #0.90
                'tsum_launch': [image_path+'tsum_app_launcher.jpg', 0.90],
                'tap_to_start': [image_path+'tap_to_start.jpg', 0.80],
                'message_box': [image_path+'message_box.jpg', 0.80],
#                'claim_all': [image_path+'claim_all.jpg', 0.90],
                'ok_button': [image_path+'ok_button.jpg', 0.7],
                'heart_sent': [image_path+'heart_sent.jpg', 0.9],
                'play_again': [image_path+'play_again.jpg', 0.90],
                'retry_button': [image_path+'retry_button.jpg', 0.80],
                'changes_in_paid_items_close': [image_path+'changes_in_paid_items_close.jpg', 0.90],
                'root_detection_permit_button': [image_path+'root_detection_permit_button.jpg', 0.85],
                'tap_to_start_button': [image_path+'tap_to_start.jpg', 0.80],
                'check_button': [image_path+'check_button.jpg', 0.80],  #  The button to receive coins and send heart back to the sender
                'you_got_a_heart_from-coins': [image_path+'you_got_a_heart_from-coins.jpg', 0.80],  #The text to the left of the 'check' button.  This is the key to which records we want to click
                'you_got_a_heart_from-no_coins': [image_path+'you_got_a_heart_from-no_coins.jpg', 0.80], 
                'received_single_confirmation': [image_path+'received_single_confirmation.jpg', 0.70]
                }

# This png image is a shot of the top-left title bar "nox" icon image                
nox_window_top_left_img = image_path+'nox_left_header.png'

listPositionDict = {'top': [image_path+'list_top.jpg', 0.979],
                    'bottom': [image_path+'list_bottom.jpg', 0.9]
                    }

game_state_img_templates = {'error_code_6': [image_path+'error_code_6.jpg', 0.90],
                            'network_unstable_retry': [image_path+'network_unstable_retry.jpg',0.90],
                            'info_unable_log_in': [image_path+'info_unable_to_log_in.jpg', 0.98],
                            'error_code_-1': [image_path+'error_code_-1.jpg', 0.80],
                            'error_code_7': [image_path+'error_code_7.jpg',0.90],
                            'heart_sent': [image_path+'heart_sent.jpg', 0.90],                               # 0.96
                            'gift_a_heart': [image_path+'gift_a_heart.jpg', 0.88],
                           # 'list_top': [image_path+'list_top.jpg', 0.979],
                           # 'list_bottom': [image_path+'list_bottom.jpg', 0.9],
                            'tsum_launch': [image_path+'tsum_app_launcher.jpg', 0.9],
                            'information': [image_path+'information.jpg', 0.90],
                            'weekly_ranking': [image_path+'weekly_ranking.jpg', 0.90],
                            'receive_gifts': [image_path+'receive_all_your_gifts_dialog.jpg', 0.70],
                            'received_all_confirmation': [image_path+'received_all_confirmation.jpg', 0.9],
                            'no_messages': [image_path+'no_messages.jpg', 0.9],
                            'receive_gift_confirmation_dialog': [image_path+'receive_gift_confirmation_dialog.jpg', 0.60],
                            'player_info_screen': [image_path+'player_info_screen.jpg', 0.85],
                            'changes_in_paid_items': [image_path+'changes_in_paid_items.jpg', 0.90],
                            'invite_dialog': [image_path+'invite_dialog.jpg', 0.90],
                            'root_detection_screen': [image_path+'root_detection_screen.jpg',0.80],
                            'splash': [image_path+'tap_to_start.jpg', 0.80],  #  This should always go after root detection screen
                            'received_single_confirmation': [image_path+'received_single_confirmation.jpg', 0.70],
                            'any_close': [image_path+'close_button.jpg',0.80],
                            'mail_box': [image_path+'mail_box.jpg',0.8]                                     #0.9
                            }
                            
                
#print(img_templates.keys())
#print(img_templates['tap_to_start'][0])
#print(img_templates['red_heart'][0])

###############################################################################################
### Start defining functions
###############################################################################################

def grabWindow():

    # determine the window region for the nox emulator.  This allows for faster image searching
    # the variable 'k' ends up being the screen coordinates of the nox window icon (top left corner of the title bar)
    k = pyautogui.locateOnScreen(nox_window_top_left_img, grayscale=True)
    # print(k)
    # find the center of the nox_header_logo
    s = pyautogui.center(k)
    # #pyautogui.moveTo(s[0], s[1], duration=1)

    # set the tuple for the screen region coordinates
    global tsumRegion
    tsumRegion=(s[0]+region_offset_x, s[1]+region_offset_y, s[0]+region_offset_x+region_size_x, s[1]+region_offset_y+region_size_y)

    # find the center of the nox_header_logo.  This is needed to calculate the click point later, so it will be returned with the image of the window
    centerPoint = pyautogui.center(k)
    
    # grab the image of the nox window having the dimensions of the game space
    window_img = ImageGrab.grab(bbox=tsumRegion)
    #print (window_img.show())
    
    # Convert the nox window image variable to a format that is usable by the cv2 library
    img_nox = np.array(window_img)

    #bg_img_nox=cv2.cvtColor(img_nox, cv2.COLOR_BGR2GRAY)
    #cv2.imshow('window', bg_img_nox)

    # # Return the grayscale of the nox window areas
    return cv2.cvtColor(img_nox, cv2.COLOR_BGR2GRAY), centerPoint
    # #print(img_nox.show())

def clickObject(name):
    # This function will click the first returned coordinates for an object that matches the template image
    
    # get the width and height of the template image
    w, h = clickablesDict[name][0].shape[::-1]
    
    # Get the current nox window screen image
    gameWindow, centerPoint = grabWindow()
    
    # Find the parts of the image where the template is like the image 
    res = cv2.matchTemplate(gameWindow, clickablesDict[name][0], cv2.TM_CCOEFF_NORMED)

    # Find areas of the image where the template matches are only within the threshold specified
    loc = np.where(res >= clickablesDict[name][1])
    
#    for pt in zip(*loc[::-1]):
#        print ("pt[0]: " + str(pt[0]) + "   pt[1]:" + str(pt[1]))

    
    
    #print("got here")
    if (len(loc[0]) == 0):
        # If we get here, the object requested to click was not found
        if (isDebug == 1):
            print ('Couldn\'t find object: ' + name)
    
        return -1
    else:
        # Click the object.  The location of the click is calculated by:
        #   region_offset_[x/y] - The 0,0 coordinate of the nox window in relationship to the 0,0 coordinate of the desktop screen
        #   centerPoint[0/1] - The centerpoint of the nox window image
        #   loc[0/1][0] - The observed coordinate of the matched template (0,0 point of the template) object within the Window image
        #   w/2 and h/2 - Half of the width and height of the template image
        #print("region_offset: x:" + str(region_offset_x) + "   y: " + str(region_offset_y))
        #print("centerPoint:   x:" + str(centerPoint[0]) + "   y: " + str(centerPoint[1]))
        #print("loc[0]:            x:" + str(loc[1][0]) + "   y: " + str(loc[0][0]))
        #print("w/h:            w:" + str(w) + "   h: " + str(h))
        #print(loc)
        # Remember that the variable loc is formatted y,x
        pyautogui.click( (region_offset_x + centerPoint[0] + loc[1][0] + (w/2)), (region_offset_y + centerPoint[1] + loc[0][0] + (h/2)) )
        return 0
    
    
    

# Load the clickable image templates to cache them in memory
def loadTemplates():

    global clickablesDict
    
    img_template = []

    # Iterate through every element in the clickablesDict dictionary
    for key, templateInfo in clickablesDict.items():
    
        
        #print(key, templateInfo[0], templateInfo[1])
        # Load the image template (the graphical data itself) and the threshold into an array
        #img_template.append(cv2.imread(templateInfo[0], 0))
        
        #cv2.waitKey(0)
        #print(templateInfo[0])
        #cv2.imshow('window', cv2.imread(templateInfo[0], 0))
        
        # Replace the path to the image (located in position zero of each dictionary item) with the actual graphical data of the image
        clickablesDict[key][0] = cv2.imread(templateInfo[0], 0)
        
        #print(templateInfo[0])
        
        #template_img_file, threshold = template
        #thresholding.
        
    # Iterate through every element in the listPositionDict dictionary
    for key, templateInfo in listPositionDict.items():
            
        #print(key, templateInfo[0], templateInfo[1])
        # Load the image template (the graphical data itself) and the threshold into an array
        #img_template.append(cv2.imread(templateInfo[0], 0))
        
        #cv2.waitKey(0)
        #print(templateInfo[0])
        #cv2.imshow('window', cv2.imread(templateInfo[0], 0))
        
        # Replace the path to the image (located in position zero of each dictionary item) with the actual graphical data of the image
        listPositionDict[key][0] = cv2.imread(templateInfo[0], 0)
        
        
    
def showAllClickables():

    # Iterate through every element in the clickablesDict dictionary
    for key, templateInfo in clickablesDict.items():
    
        # Set the CV2 waitkey to wait until a button is pushed before moving to the next image
        cv2.waitKey(0)
        cv2.imshow('window', templateInfo[0])
        
def showClickable(name):

    
    cv2.imshow('window', clickablesDict[name][0])
    # Set the CV2 waitkey to wait until a button is pushed before moving to the next image
    cv2.waitKey(0)
    
 
    
    
def sendScreenOfHearts():

    global region_offset_x, region_offset_y, region_size_x, region_size_y, tsum_region, rrdHeartCount
    
    if (isDebug == 1):
        print(readableTimeStamp() + ": Entered 'sendScreenOfHearts'")
    
    # get the width and height of the template image
    w, h = clickablesDict['red_heart'][0].shape[::-1]
    
    # Get the current nox window screen image
    gameWindow, centerPoint = grabWindow()
    
    # Find the parts of the image where the template is like the image 
    res = cv2.matchTemplate(gameWindow, clickablesDict['red_heart'][0], cv2.TM_CCOEFF_NORMED)
        
    # Find areas of the image where the template matches are only within the threshold specified
    loc = np.where(res >= clickablesDict['red_heart'][1])
    #print(loc)
    
    # As a failsafe, see if there is an "Gift a Heart" dialog waiting for dismissal
    if (clickObject('ok_button') == 1):
        #If we get here, there was a "gift a heart" dialog to dismiss.  No we need to wait a second and dismiss the "Heart Sent" popup
        time.sleep(1.0)
        clickObject('heart_sent')
    
    
    # Using the matched coordinates, ensure that we are not going to be clicking on points that are very close to each other
    #  Sometimes cv2 will identify a match for the same heart multiple times....resulting in multiple clicks if we do not
    #  eliminate the points that are within the same heart
    old_x = 0
    old_y = 0
    
    for pt in zip(*loc[::-1]):
        # Using the Pythagorean theorem, figure out click proximity to the last set of points
        #  If the distance is too close (within the same heart) then skip this one
        ptDistance = math.sqrt(math.fabs((old_x-pt[0])**2) + math.fabs((old_y-pt[1])**2))
        
        if ( ptDistance > 100 ):
            # Set the "old" x/y variables to be equal to this set of points
            old_x = pt[0]
            old_y = pt[1]
            # Click the heart.  The location of the click is calculated by:
            #   region_offset_[x/y] - The 0,0 coordinate of the nox window in relationship to the 0,0 coordinate of the desktop screen
            #   centerPoint[0/1] - The centerpoint of the nox window image
            #   pt[0/1] - The observed coordinate of the matched template (0,0 point of the template) object within the Window image
            #   w/2 and h/2 - Half of the width and height of the template image
            #print("region_offset: x:" + str(region_offset_x) + "   y: " + str(region_offset_y))
            #print("centerPoint:   x:" + str(centerPoint[0]) + "   y: " + str(centerPoint[1]))
            #print("pt:            x:" + str(pt[0]) + "   y: " + str(pt[1]))
            
            #pyautogui.click( (pt[0]+region_offset_x+centerPoint[0]+(w/2)), (pt[1]+region_offset_y+centerPoint[1]+(h/2)) )
            pyautogui.click( (region_offset_x + centerPoint[0] + pt[0] + (w/2)), (region_offset_y + centerPoint[1] + pt[1] + (h/2)) )
            if (isDebug == 1):
                print(readableTimeStamp() + ": Clicked Heart")
            # Update the rrd counter
            rrdHeartCount += 1
            if (isDebug == 1):
                print(readableTimeStamp() + ": rrdHeartCount: " + str(rrdHeartCount))
            
            # We clicked a heart, now we need to click the 'OK' button on the "Gift a Heart" confirmation dialog
            #  Let's wait for an affirmative response from clicking the "OK" button
            timeEntered = time.time()  # Get the time prior to the while loop so we can measure up to a break out if we get stuck in the loop
            time.sleep(0.8)
            i = 0
            while (clickObject('ok_button') != 0):
                # Going to loop until the OK button was clicked....but, need to have some handling for non-standard conditions
                # If, after 3 iterations waiting for the OK button to be clicked, check for close_button
                if (isDebug == 1):
                    print(readableTimeStamp() + ": In while loop for clicking ok_button: " + str(i))
                if (i > 2):
                    if (isDebug == 1):
                        print(readableTimeStamp() + ": Looped > 2")
                    if (clickObject('close_button') == 0):
                        if (isDebug == 1):
                            print(readableTimeStamp() + ": In 'close_button' if statement")
                        # If we get here, the close button was present and clicked.  Need to click the heart again...possibly
                        pyautogui.click( (region_offset_x + centerPoint[0] + pt[0] + (w/2)), (region_offset_y + centerPoint[1] + pt[1] + (h/2)) )
                        time.sleep(1.0)
                    else:
                        # It is possible the initial heart click didn't register...try again...
                        break
                i += 1
                
                    
            # We clicked to confirm sending a heart.  The next thing to look for is the 'Heart Sent' dialog
            timeEntered = time.time()  # Get the time prior to the while loop so we can measure up to a break out if we get stuck in the loop
            time.sleep(1.8)
            i = 0
            while (clickObject('heart_sent') != 0):
                            
                # Going to loop until the OK button was clicked
                # failsafe logic here so we don't get stuck in here forever
                if (time.time() - timeEntered > 10 ):
                    break
                    
                if (i > 2):
                    if (isDebug == 1):
                        print(readableTimeStamp() + ": Looped > 2")
                    if (clickObject('ok_button') == 0):
                    
                        if (isDebug == 1):
                            print("In 'sent_hearts' if statement")
                        # If we get here, the close button was present and clicked.  Need to click the heart again...possibly
                        pyautogui.click( (region_offset_x + centerPoint[0] + pt[0] + (w/2)), (region_offset_y + centerPoint[1] + pt[1] + (h/2)) )
                        time.sleep(1.0)
                    else:
                        break
            # Pause a moment before going on to the next heart
            time.sleep(0.1)
                    
def scrollDown():
    # scroll one screen of hearts down (usually 4 people)
    global tsumRegion, heartCount
    pyautogui.moveTo(tsumRegion[0]+50, tsumRegion[1]+800, duration=0)
    pyautogui.dragTo(tsumRegion[0]+50, tsumRegion[1]+314, duration=1.15, button='left')
    #print("Total hearts sent: ", heartCount)

def scrollTop():
    # #print(tsumRegion)
    # global tsumRegion
    # myState = determineState()
    while (listPosition() != 'top'):
        for i in range(1, 20):
            pyautogui.moveTo(tsumRegion[0]+50, tsumRegion[1]+292, duration=0.0)
            pyautogui.dragTo(tsumRegion[0]+50, tsumRegion[1]+800, duration=0.15, button='left')
    
def listPosition():

    # Get the current nox window screen image
    gameWindow, centerPoint = grabWindow()
    
    #See if we are at the 'top' or 'bottom' of the list.  Everything else is 'middle'
    for key, value in listPositionDict.items():
        #print(key, ", ", value[0], ", ", value[1])
        
        w, h = value[0].shape[::-1]
        res = cv2.matchTemplate(gameWindow, value[0], cv2.TM_CCOEFF_NORMED)
        #print(res)
        
        loc = np.where(res >= value[1])
        #print(loc)
        #print("matches: ", len(loc[0]))
        #print("length at 2: ",len(loc[0]), "contents:")
        #for i in range(0, len(loc[0])):
        #   print(loc[i])
        if (len(loc[0]) > 0):
            return key
    
    # If we get here, then we are somewhere in the middle of the list because there was no match for either top or bottom
    return 'middle'

def gameState():
    
    # Get the current nox window screen image
    gameWindow, centerPoint = grabWindow()
    
    for key, value in game_state_img_templates.items():
        #print(key, ", ", value[0], ", ", value[1])
        img_template = cv2.imread(value[0], 0)
        w, h = img_template.shape[::-1]
        res = cv2.matchTemplate(gameWindow, img_template, cv2.TM_CCOEFF_NORMED)
        #print(res)
        threshold = value[1]
        loc = np.where(res >= threshold)
        #print("matches: ", len(loc[0]))
        #print("length at 2: ",len(loc[0]), "contents:")
        #for i in range(0, len(loc[0])):
        #    print(loc[i])

        if (len(loc[0]) > 0):
        
            #print("got to 1")
        
            if (isDebug == 1):
                print(readableTimeStamp() + ": Current state: ", key)
            if (key=='player_info_screen'):
                # force close this screen in all cases
                if (isDebug == 1):
                    print(readableTimeStamp() + ": detected player info screen...clicking close")
                clickObject('close_button')
                return key
            elif (key=='network_unstable_retry'):
                # force close this screen in all cases
                if (isDebug == 1):
                    print(readableTimeStamp() + ": detected network_unstable_retry screen...clicking retry")
                time.sleep(5)
                #clickObject('play_again')
                while (clickObject('retry_button') != 0):
                    time.sleep(1)
                    if (gameState() != 'network_unstable_retry'):
                        break
                return key
            elif (key=='error_code_-1'):
                # force close this screen in all cases
                if (isDebug == 1):
                    print(readableTimeStamp() + ": detected network_error_-1 screen...clicking retry")
                time.sleep(5)
                #clickObject('play_again')
                while (clickObject('retry_button') != 0):
                    time.sleep(1)
                    if (gameState() != 'error_code_-1'):
                        break
                return key
            elif (key=='changes_in_paid_items'):
                # force close this screen in all cases
                if (isDebug == 1):
                    print(readableTimeStamp() + ": detected changes in paid items screen...clicking play_again")
                clickObject('changes_in_paid_items_close')
                return key
            elif (key=='error_code_6'):
                # force close this screen in all cases
                if (isDebug == 1):
                    print(readableTimeStamp() + ": detected error_code_6 screen...clicking close")
                time.sleep(5)
                clickObject('close_button')
                return key
            elif (key=='error_code_7'):
                # force close this screen in all cases
                if (isDebug == 1):
                    print(readableTimeStamp() + ": detected error_code_7 screen...clicking close")
                time.sleep(5)
                clickObject('close_button_error_code_7')
                return key
            elif (key=='error_code_1'):
                # force close this screen in all cases
                if (isDebug == 1):
                    print(readableTimeStamp() + ": detected error_code_1 screen...clicking close")
                time.sleep(5)
                while (clickObject('close_button') != 0):
                    time.sleep(1)
                    if (gameState() != 'error_code_1'):
                        break
                return key
            elif (key=='root_detection_screen'):
                # Press 'permit' on this screen 
                if (isDebug == 1):
                    print(readableTimeStamp() + ": Root Detection screen detected")
                clickObject('root_detection_permit_button')
                return key
            elif (key=='splash'):
                # We are on the initial startup screen
                if (isDebug == 1):
                    print(readableTimeStamp() + ": Detected splash screen...clicking 'tap to start' button")
                clickObject('tap_to_start_button')
                return key
            else:
                return key
    
    # If we get here, none of the game state template images matched
    return 'unknown_state_2'
    
            # This one should go last
    #        elif (key=='any_close'):
    #            # If we are on a screen with a close_button...always click it
    #            if (isDebug == 1):
    #                print('We are on a screen with a close_button...always click it')
    #            clickObject('close_button')
                
            

def claimAll():

    global lastClaimTimeCounter, lastClaimTimeClock, receivedAllCount
    timeEntered = time.time()
    
    # press the messageBox button (envelope)
    myState = gameState()
    if (isDebug == 1):
        print ('game state: ' + myState)
    
    while (myState == 'weekly_ranking' or myState == 'list_top' or myState == 'list_bottom'):
        if (isDebug == 1):
            print (readableTimeStamp() + ': waiting for message_box button to display mail box')
        clickObject('message_box')
        myState = gameState()
    
    if (isDebug == 1):
        print (readableTimeStamp() + ': Got out of "waiting for message_box button to display mail box')    
    
    lastClaimTimeCounter = time.time()
    lastClaimTimeClock = time.localtime(time.time())
    
    # wait for the "Mail Box" dialog to appear
    i = 0
    myState = gameState()
    while (myState != 'mail_box' and myState != 'no_messages'):
        if (isDebug == 1):
            print(readableTimeStamp() + ": waiting...for claim all dialog")
        myState = gameState()
        # This next if statement is a failsafe mechanism in case we get stuck in here
        if (time.time() - timeEntered > 20 ):
            break
        
    if (gameState() == 'no_messages'):
        clickObject('close_button')
        return
    
    while (gameState() == 'mail_box'):
        # press the "Claim All" button
        if (isDebug == 1):
            print (readableTimeStamp() + ': In mail box trying to click claim_all')
    
        clickObject('claim_all_button')
        # This next if statement is a failsafe mechanism in case we get stuck in here
        if (time.time() - timeEntered > 30 ):
            break

    #while (gameState() != 'claim_all'):
    #    print("waiting...for claim all dialog")
    #    i=i+1
    #    if i > 7:
    #        break
    
    i = 0
    while (gameState() != 'receive_gifts'):
        if (isDebug == 1):
            print(readableTimeStamp() + ": waiting...for receive all gifts")
        # This next if statement is a failsafe mechanism in case we get stuck in here
        if (time.time() - timeEntered > 30 ):
            break

        
    while (gameState() == 'receive_gifts'):
        clickObject('ok_button')
        #time.sleep(0.5)
        # This next if statement is a failsafe mechanism in case we get stuck in here
        if (time.time() - timeEntered > 30 ):
            break

        
    i = 0
    while (gameState() != 'received_all_confirmation'):
        if (isDebug == 1):
            print(readableTimeStamp() + ": waiting...for \"received\" Info confirmation")
        # This next if statement is a failsafe mechanism in case we get stuck in here
        if (time.time() - timeEntered > 30 ):
            break


    while (gameState() == 'received_all_confirmation'):        
        clickObject('close_button')
        receivedAllCount += 1 
        #time.sleep(0.5)
        # This next if statement is a failsafe mechanism in case we get stuck in here
        if (time.time() - timeEntered > 30 ):
            break

        
    myState = gameState()
    while ( ( myState != 'mail_box' ) and ( myState != 'no_messages' ) ):
        if (isDebug == 1):
            print(readableTimeStamp() + ": waiting...for return to mail box")
        myState = gameState()
        # This next if statement is a failsafe mechanism in case we get stuck in here
        if (time.time() - timeEntered > 30 ):
            break

        
    myState = gameState()
    while ( myState == 'mail_box' or myState == 'no_messages'):
        clickObject('close_button')
        #time.sleep(0.5)
        myState = gameState()
        # This next if statement is a failsafe mechanism in case we get stuck in here
        if (time.time() - timeEntered > 30 ):
            break

            
def readableTimeStamp():
    
    return datetime.fromtimestamp(time.time()).strftime('%a %b %d %H:%M:%S %Y')
            
def returnHeart():
    
    global region_offset_x, region_offset_y, region_size_x, region_size_y, tsum_region, rrdHeartCount
    
    if (isDebug == 1):
        print(readableTimeStamp() + ": Entered 'returnHeart'")
    
    # get the width and height of the template image
    w, h = clickablesDict['you_got_a_heart_from-coins'][0].shape[::-1]
    
    # Get the current nox window screen image
    gameWindow, centerPoint = grabWindow()
    
    # Find the parts of the image where the template is like the image 
    res = cv2.matchTemplate(gameWindow, clickablesDict['you_got_a_heart_from-coins'][0], cv2.TM_CCOEFF_NORMED)
        
    # Find areas of the image where the template matches are only within the threshold specified
    loc = np.where(res >= clickablesDict['you_got_a_heart_from-coins'][1])
    #print(loc)
    
    # Set this to false by default.
    heartPresent = False
    
    #only return the top heart, because as we return hearts, the list shrinks.  We do not need to scroll down or click different coordinates.  Just click the first match
    for pt in zip(*loc[::-1]):
        
        if (isDebug == 1):
            print(readableTimeStamp() + ": Found a 'check' button on a heart to return")
        #was there a "check" button to click?  If we got here, there was.
        heartPresent = True
        
        #Click on the first "check" button found
        pyautogui.click( (region_offset_x + centerPoint[0] + pt[0] + (w)), (region_offset_y + centerPoint[1] + pt[1] + (h)) ) # adding 'w' to the x coord and 'h' to the y coord because we want to click on the right side of the template....which should be the 'check' button
        if (isDebug == 1):
            print(readableTimeStamp() + ": Accepted Heart and returned heart")
        # Update the rrd counter
        rrdHeartCount += 1
        if (isDebug == 1):
            print(readableTimeStamp() + ": rrdHeartCount: " + str(rrdHeartCount))
        
        # We clicked a 'check' button, now we need to click the 'OK' button on the "Receive Gift" confirmation dialog
        #  Let's wait for an affirmative response from clicking the "OK" button
        timeEntered = time.time()  # Get the time prior to the while loop so we can measure up to a break out if we get stuck in the loop
        #time.sleep(0.7)
        i = 0
        if (isDebug == 1):
            print(readableTimeStamp() + ": clicking 'OK' button to 'Receive Gift'")
        while (clickObject('ok_button') != 0):
            # Going to loop until the OK button was clicked....but, need to have some handling for non-standard conditions
            # If, after 3 iterations waiting for the OK button to be clicked, check for close_button
            
            if (isDebug == 1):
                print(readableTimeStamp() + ": In while loop for clicking ok_button on 'Receive Gift' confirmation: " + str(i))
                gameState()
            if (i > 2):
                if (isDebug == 1):
                    print(readableTimeStamp() + ": Looped > 2")
                # If we get here, the click on the 'check' button may not have registered.  Click it again
                if (isDebug == 1):
                    print(readableTimeStamp() + ": Trying to click 'check' button again")
                pyautogui.click( (region_offset_x + centerPoint[0] + pt[0] + (w)), (region_offset_y + centerPoint[1] + pt[1] + (h)) ) # adding 'w' to the x coord and 'h' to the y coord because we want to click on the right side of the template....which should be the 'check' button
            i += 1
        
        time.sleep(0.5)
        
        # See if the gameState is still in "Receive Gift"
        myState = gameState()
        if (isDebug == 1):
            print(readableTimeStamp() + ": myState: " + myState)
        
        if (myState == 'receive_gift_confirmation_dialog'):
            print(readableTimeStamp() + ": trying to click OK button again")
            # If we get here, the pyautogui click on the OK button may not have registered.  Click ok again
            clickObject('ok_button')
            
        
        # We clicked 'OK' to confirm "Receive Gift" dialog.  The next thing to look for is the 'Received' confirmation dialog...which we need to click
        timeEntered = time.time()  # Get the time prior to the while loop so we can measure up to a break out if we get stuck in the loop
        
        i = 0
        #myState = gameState()
        #if (isDebug == 1):
        #    print(readableTimeStamp() + ": myState: " + myState)
        while (clickObject('received_single_confirmation') != 0):
            myState = gameState()
            if (isDebug == 1):
                print(readableTimeStamp() + ": myState: " + myState)
            if (myState == 'mail_box'):
                print('got to 1')
            # Going to loop until the dialog box (which is a whole 'button') was clicked
            # failsafe logic here so we don't get stuck in here forever
            if (time.time() - timeEntered > 10 ):
                break
                
            if (i > 2):
                if (isDebug == 1):
                    print(readableTimeStamp() + ": Looped > 2")
                if (clickObject('received_single_confirmation') == 0):
                
                    if (isDebug == 1):
                        print(readableTimeStamp() + ": In 'received_single_confirmation' if statement")
                    
                else:
                    break
        # Pause a moment before going on to the next heart
        time.sleep(0.1)
        break  # Get out of the for loop because we only need to send one heart
    
    # If we did not find a "check" button to click, there was not a heart present to return
    if (isDebug == 1):
            print(readableTimeStamp() + ": Done with returnHeart()")
    return heartPresent



if (isDebug == 1):
    print(readableTimeStamp() + ": Loading image templates....")
loadTemplates()
if (isDebug == 1):
    print(readableTimeStamp() + ": Image templates loaded....")
#showAllClickables()
#showClickable('red_heart')
gameState()

rrdHeartCount = 0
lastRrdUpdate = round(time.time())

#showClickable('you_got_a_heart_from')

while (1 == 1):

    clickObject('message_box')
    
    heartsToClaim = True
    time.sleep(3)
    while (heartsToClaim):
        heartsToClaim = returnHeart()
        #scrollDown()
        
    # If there are no more hearts to claim, press the 'Close' button
    clickObject('close_button')
    lastTimeInMailBox = time.time()
    
    # I am out in the "Weekly Ranking" list now.  Send hearts for some amount of time
    while (time.time() - lastTimeInMailBox < minsBetweenCollects * 60):
        if (listPosition() != 'bottom'):
            print(readableTimeStamp() + ': List Position: ' + listPosition())
            myState = gameState()
            if (myState == "mail_box"):
                if (isDebug == 1):
                    print(readableTimeStamp() + ': state: ' + myState)
                break
            sendScreenOfHearts()
            myState = gameState()
            if (isDebug == 1):
                print(readableTimeStamp() + ': state: ' + myState)
            scrollDown()
            # Use gamteState to check the game status and clear any strange errors that may have occurred
            
        else:
            sendScreenOfHearts()
            myState = gameState()
            if (isDebug == 1):
                print(readableTimeStamp() + ': state: ' + myState)
            scrollTop()
            myState = gameState()
            if (isDebug == 1):
                print(readableTimeStamp() + ': state: ' + myState)
    
    try:
        print(readableTimeStamp() + ": Updating RRD Database with heartSent count: " + str(rrdHeartCount))
        call(rrdTool + ' ' + 'update ' + rrdDbFile + ' ' + str(lastRrdUpdate) + ":" + str(rrdHeartCount))
        print(readableTimeStamp() + ": Generating New RRD Graph")
        call(rrdTool + ' ' + 'graph ' + rrdGraphPath + '/sentHearts.png --start ' + str(lastRrdUpdate - 60*60*48) + ' --end ' + str(lastRrdUpdate) + ' DEF:x1=' + rrdDbFileGraph + ':heartsSent:AVERAGE LINE1:x1#FF0000:heartsSent')
        lastRrdUpdate = round(time.time())
        
    except:
        print(readableTimeStamp() + ": Couldn't update RRD database with sent heart count")
    else:
        print(readableTimeStamp() + ": Updated the RRD Database with the sent hearts count: " + str(rrdHeartCount))
        rrdHeartCount = 0

    
    

    

        
        #
        #if ( (time.time() - lastClaimTimeCounter) >= 30 * 60):
    #        claimAll()
       # myState = gameState()
       # if (myState == "any_close"):
       #     clickObject('close_button')
       # 
        
      #  if ( (time.time() - lastRrdUpdate) >= 5*60):
        # Do an update of the rrd database
        
            
    
    # We are at the bottom of the list, but there might be some hearts to send on this screen...so send them
    #sendScreenOfHearts()
    # If we get here we have reached 'list_bottom'.  Scroll to the top and start again
    #scrollTop()
#clickObject('ok_button')

 
    



        



       
    
# ###############################################################################################
# ### Done defining functions
# ###############################################################################################
    
# # Find the "TAP TO START BUTTON"
# #findTarget(img_templates['tap_to_start'])

# initialLaunch=False       ################ Get rid of this line ###############

# while (True):
    
    # #if (lastClaimTimeClock == 'Never'):
    # #    print('Last Hearts Claimed: ', lastClaimTimeClock)
    # #else:
    # #    print('Last Hearts Claimed: ',time.strftime('%X %x',lastClaimTimeClock))
    
    # myState = determineState()
    # if (isDebug == 1):
        # print("currentState=",myState)
    # if (myState == 'weekly_ranking' or myState == 'list_bottom'):
        # if (isDebug == 1):
            # print("Entered ", myState)
        # if (initialLaunch is True or myState == 'list_bottom'):
            # initialLaunch = False
            # if (isDebug == 1):
                # print("scrollTop")
            # scrollTop()
            # claimAll()
        # else:
            # if (isDebug == 1):
                # print("call sendHearts")
            # sendHearts()
    # elif myState == 'list_top':
        # if (isDebug == 1):
            # print("Entered ", myState)
        # sendHearts()
    # elif myState == 'information':
        # if (isDebug == 1):
            # print("Entered ", myState)
        # clickTarget(button_img_templates['close_button'])
    # elif myState == 'splash':
        # if (isDebug == 1):
            # print("Entered ", myState)
        # clickTarget(button_img_templates['tap_to_start'])
        # time.sleep(10)
    # elif myState == 'tsum_launch':
        # if (isDebug == 1):
            # print("Entered ", myState)
        # clickTarget(button_img_templates['tsum_launch'])
        # time.sleep(6)
    # elif myState == 'info_unable_log_in':
        # if (isDebug == 1):
            # print("Entered ", myState)
        # clickTarget(button_img_templates['close_button'])
    # elif myState == 'close_button':
        # if (isDebug == 1):
            # print("Entered ", myState)
        # clickTarget(button_img_templates['close_button'])
    # elif myState == 'mail_box':
        # if (isDebug == 1):
            # print("Entered ", myState)
        # clickTarget(button_img_templates['close_button'])
    # elif myState == 'heart_sent':
        # clickTarget(button_img_templates['heart_sent'])
        # #time.sleep(0.3)
    # elif myState == 'gift_a_heart':
        # clickTarget(button_img_templates['ok_button'])
    # elif myState == 'no_messages':
        # clickTarget(button_img_templates['close_button'])
    # elif myState == 'network_unstable':
        # clickTarget(button_img_templates['play_again'])
        # clickTarget(button_img_templates['retry_button'])
    # elif myState == 'error_code_1':
        # clickTarget(button_img_templates['close_button'])
    # elif myState == 'error_code_6':
        # clickTarget(button_img_templates['close_button'])
    # elif myState == 'invite_dialog':
        # clickTarget(button_img_templates['close_button'])
        
           
    # myState = ""

