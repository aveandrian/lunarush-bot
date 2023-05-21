# -*- coding: utf-8 -*-    
from email.mime import image
from src.logger import logger, loggerBossFight, loggerBossHunt, loggerMapClicked
from cv2 import cv2
from os import listdir
from random import randint
from random import random
import numpy as np
import mss
import pyautogui
import time
import sys
import yaml

time_to_check = {
    "close" : 1,  
    "login" : 1,
    "ship_to_fight" : 15,
    "ship" : 10,
    "fight" : 5,
    "fight_boss" : 20,
    "ship_tela_boss": 15,
    "continue": 1,
    }

time_start = {
    "close" : 0,
    "login" : 0,
    "ship_to_fight" : 0,
    "ship" : 0,
    "fight" : 0,
    "fight_boss" : 0,
    "ship_tela_boss": 0,
    "continue": 0,
    }

# Load config file.
stream = open("config.yaml", 'r')
c = yaml.safe_load(stream)
ct = c['threshold']
pause = c['time_intervals']['interval_between_moviments']
pyautogui.PAUSE = pause

welcome_text = ""

def addRandomness(n, randomn_factor_size=None):
    """Returns n with randomness
    Parameters:
        n (int): A decimal integer
        randomn_factor_size (int): The maximum value+- of randomness that will be
            added to n

    Returns:
        int: n with randomness
    """

    if randomn_factor_size is None:
        randomness_percentage = 0.1
        randomn_factor_size = randomness_percentage * n

    random_factor = 2 * random() * randomn_factor_size
    if random_factor > 5:
        random_factor = 5
    without_average_random_factor = n - randomn_factor_size
    randomized_n = int(without_average_random_factor + random_factor)
    # logger('{} with randomness -> {}'.format(int(n), randomized_n))
    return int(randomized_n)

def moveToWithRandomness(x,y,t):
    pyautogui.moveTo(addRandomness(x,10),addRandomness(y,10),t+random()/2)


def remove_suffix(input_string, suffix):
    """Returns the input_string without the suffix"""

    if suffix and input_string.endswith(suffix):
        return input_string[:-len(suffix)]
    return input_string

def load_images(dir_path='./targets/'):
    """ Programatically loads all images of dir_path as a key:value where the
        key is the file name without the .png suffix

    Returns:
        dict: dictionary containing the loaded images as key:value pairs.
    """

    file_names = listdir(dir_path)
    targets = {}
    for file in file_names:
        path = 'targets/' + file
        targets[remove_suffix(file, '.png')] = cv2.imread(path)

    return targets

def clickBtn(img, timeout=3, threshold = ct['default']):
    """Search for img in the screen, if found moves the cursor over it and clicks.
    Parameters:
        img: The image that will be used as an template to find where to click.
        timeout (int): Time in seconds that it will keep looking for the img before returning with fail
        threshold(float): How confident the bot needs to be to click the buttons (values from 0 to 1)
    """

    print("\n");
    logger(None, progress_indicator=True)
    start = time.time()
    has_timed_out = False
    while(not has_timed_out):
        matches = positions(img, threshold=threshold)

        if(len(matches)==0):
            has_timed_out = time.time()-start > timeout
            continue

        x,y,w,h = matches[0]
        pos_click_x = x+w/2
        pos_click_y = y+h/2
        moveToWithRandomness(pos_click_x,pos_click_y,1)
        pyautogui.click()
        return True

    return False

def printSreen():
    with mss.mss() as sct:
        monitor = sct.monitors[0]
        sct_img = np.array(sct.grab(monitor))
        # The screen part to capture
        # monitor = {"top": 160, "left": 160, "width": 1000, "height": 135}

        # Grab the data
        return sct_img[:,:,:3]

def positions(target, threshold=ct['default'],img = None):
    if img is None:
        img = printSreen()
    result = cv2.matchTemplate(img,target,cv2.TM_CCOEFF_NORMED)
    w = target.shape[1]
    h = target.shape[0]

    yloc, xloc = np.where(result >= threshold)


    rectangles = []
    for (x, y) in zip(xloc, yloc):
        rectangles.append([int(x), int(y), int(w), int(h)])
        rectangles.append([int(x), int(y), int(w), int(h)])

    rectangles, weights = cv2.groupRectangles(rectangles, 1, 0.2)
    return rectangles

def refreshHeroesPositions():
    logger('🔃 Refreshing Heroes Positions')
    clickBtn(images['ok'])
    clickBtn(images['go-back-arrow'])
    clickBtn(images['boss_hunt_icon'])

    # time.sleep(3)
    # clickBtn(images['boss_hunt_icon'])


def scroll_ships():
    global x_scroll
    global y_scroll
    global h_scroll
    global w_scroll
    use_click_and_drag_instead_of_scroll = True
    click_and_drag_amount = 80
    scroll_size = 60

    moveToWithRandomness(x_scroll+(w_scroll/2),y_scroll+300+(h_scroll/2),1)
    if not use_click_and_drag_instead_of_scroll:
        pyautogui.scroll(-scroll_size)
        time.sleep(2)
    else:
        pyautogui.dragRel(0,-click_and_drag_amount,duration=1, button='left')
        time.sleep(2)

def go_to_continue():
    if clickBtn(images['confirm']):
        print('Found confirm')
        return True
    else:
        return False

def tela_close():
    if clickBtn(images['close']):
        print('Found close')
        return True
    else:
        return False

def go_to_ship():
    if clickBtn(images['ship']):
        print('Found ship buttom')
        return True
    else:
        return False

def go_to_fight():
    if clickBtn(images['fight-boss']):
        print('Im going to fight boss!!')
        time_to_check['ship_to_fight'] = 15
        time_to_check['ship_tela_boss'] = 7
        time_start["ship_tela_boss"] = time.time()
    else:
        print('Nao found fight boss!!')

def ships_15_15():
    start = time.time()
    has_timed_out = False
    while(not has_timed_out):
        matches = positions(images['15-15'], 0.98)

        if(len(matches)==0):
            has_timed_out = time.time()-start > 3
            continue
        print('Found 15-15 fabric ships')
        return True
    return False

def ships_15_15_boss():
    start = time.time()
    has_timed_out = False
    while(not has_timed_out):
        matches = positions(images['15-15-boss'], 0.9)

        if(len(matches)==0):
            has_timed_out = time.time()-start > 3
            continue
        print('Found 15-15 boss')
        return True
    return False

def time_is_zero():
    start = time.time()
    has_timed_out = False
    while(not has_timed_out):
        matches = positions(images['time-zero'], 0.8)

        if(len(matches)==0):
            has_timed_out = time.time()-start > 3
            continue
        print('Found time-zero')
        return True
    print('Time different from zero')
    return False

def click_fight_ship_new():
    global x_scroll
    global y_scroll
    global h_scroll
    global w_scroll

    offset_x = 130
    offset_y = 50
    y_ship_final = 0

    green_bars = positions(images['green-bar-short'], threshold=0.9)
    print('Green bars detected', len(green_bars))
    buttons = positions(images['fight'], threshold=0.8)
    print('Buttons fight detected', len(buttons))

    for key,(x, y, w, h) in enumerate(buttons):
        print('key: ', key)
        # if key == 0:
        #     x_scroll = x
        #     y_scroll = y
        #     h_scroll = h
        #     w_scroll = w
        # elif key > 0:
        y_ship_final = y
        print("Y ship final: ", y_ship_final)        

    yellow_bars = positions(images['yellow-bar-short'], threshold=0.9)
    print('Yellow bars detected', len(yellow_bars))

    not_working_green_bars = []
    for bar in green_bars:
        not_working_green_bars.append(bar)
    for bar in yellow_bars:
        not_working_green_bars.append(bar)
    print("not_working_green_bars:") 
    print(not_working_green_bars)
    #if len(not_working_green_bars) > 0:
        #print('buttons with green bar detected', len(not_working_green_bars))
        #print('Naves disponiveis', len(not_working_green_bars))
    ship_clicks_cnt = 0
    for (x, y, w, h) in not_working_green_bars:
        #print("Entrou for x y w h. Y:", y)
        if ( y < y_ship_final+50):
            moveToWithRandomness(x+offset_x+(w/2),y+offset_y+(h/2),1)
            for i in range(len(not_working_green_bars)):
                pyautogui.click()
                time.sleep(1)
                global ship_clicks
                ship_clicks = ship_clicks + 1
                ship_clicks_cnt = ship_clicks_cnt + 1
                # if ship_clicks > 15:
                #     return            
            print("Qtd ship shipped: " + str(ship_clicks_cnt) + ". " + "Qtd total ship shipped: " + str(ship_clicks))   
            #print("Qtd ship total enviadas", ship_clicks) 
            return
        else:
            print("Scroll down")
    print(not_working_green_bars)      
    return ship_clicks_cnt #len(not_working_green_bars)

       
def ship_to_fight():    
    global ship_clicks
    #if time_is_zero():
    if go_to_ship():
        time_to_check['ship_to_fight'] = 5
        ship_clicks = 0
        buttonsClicked = 1
        empty_scrolls_attempts = 3
        #/while(empty_scrolls_attempts >0):
        while(ships_15_15() == False and empty_scrolls_attempts >0):
            buttonsClicked = click_fight_ship_new()
            print("buttonsClicked: ")
            print(buttonsClicked)
            if buttonsClicked == 0:
                empty_scrolls_attempts = empty_scrolls_attempts - 1
            print("empty_scrolls_attempts: ")
            print(empty_scrolls_attempts)
            # if ships_15_15():
            #     break            
            # if ship_clicks > 15:
            #     break    
            # scroll_ships()
            time.sleep(1)
        if(ships_15_15()):    
            go_to_fight()
    else:
        return
    #else:
    #    return

def go_to_ship_tela_boss():
    if clickBtn(images['ship-boss'], 0.95):
        print('Volta for ships, boss fabric')
        time_to_check['ship_tela_boss'] = 15;
        return True
    else:   
        return False

def ship_tela_boss():
    # if ships_15_15_boss():
    #     return
    # elif ships_15_15_boss() == False:        
        if go_to_ship_tela_boss():
            time.sleep(5)
            
            buttonsClicked = 1
            empty_scrolls_attempts = 3

            # while(ships_15_15() == False and empty_scrolls_attempts >0):
            #     buttonsClicked = click_fight_ship_new()
            #     if buttonsClicked == 0:
            #         empty_scrolls_attempts = empty_scrolls_attempts - 1
            #     # if ships_15_15():
            #     #     break
            #     # scroll_ships()
            #     time.sleep(2)
            if(ships_15_15()):    
                go_to_fight()


def login():
    global login_attempts
    print("Checking if the game has been disconnected")
    print('login_attempts')
    print(login_attempts)
    if login_attempts > 3:
        print('Three login attempts, refreshing the page')
        login_attempts = 0
        pyautogui.hotkey('ctrl','f5')
        return

    print('Searching for Connect Wallet...')
    if clickBtn(images['connect-wallet'], timeout = 10):
        print('Connect wallet encontrado')
        login_attempts = login_attempts + 1
    else:
        return

    print('Searching for Close...')
    if clickBtn(images['close'], timeout = 10):
        print('''Close encontrado

            ''')
        pyautogui.hotkey('ctrl','f5')
        return

    print('Searching for Sign Wallet...')
    if clickBtn(images['sign'], timeout=10):
        login_attempts = login_attempts + 1
        print('Sign button encontrado')
        
        if clickBtn(images['play'], timeout = 15):
            print('play button found')
            print('Game started successfully!!')
            login_attempts = 0            
            return
        if clickBtn(images['close'], timeout = 12):
            print('Close encontrado')
            pyautogui.hotkey('ctrl','f5')
            return
    return

def main():
    """Main execution setup and loop"""
    # ==Setup==
    global images    
    global ship_clicks
    global hero_clicks
    global login_attempts
    global last_log_is_progress
    hero_clicks = 0
    ship_clicks = 0
    login_attempts = 0
    last_log_is_progress = False

    global images
    images = load_images()

    print(welcome_text)
    time.sleep(7)
    t = c['time_intervals']

    last = {
    "login" : 0,
    "heroes" : 0,
    "new_map" : 0,
    "check_for_captcha" : 0,
    "refresh_heroes" : 0,
    "boss_hunt": 0,
    "tap": 0,
    }

    # time_start = {
    # "close" : 0,
    # "login" : 0,
    # "ship_to_fight" : 0,
    # "ship" : 0,
    # "fight" : 0,
    # "fight_boss" : 0,
    # "ship_tela_boss": 0,
    # "continue": 0,
    # }

    # time_to_check = {
    # "close" : 1,  
    # "login" : 1,
    # "ship_to_fight" : 76,
    # "ship" : 10,
    # "fight" : 5,
    # "fight_boss" : 20,
    # "ship_tela_boss": 15,
    # "continue": 1,
    # }
    # =========

    while True:
        now = time.time()
        actual_time = time.time()

        print("Time to fight:")
        print(actual_time - time_start["ship_to_fight"])
        print((time_to_check['ship_to_fight'] * 60))
        if actual_time - time_start["ship_to_fight"] > (time_to_check['ship_to_fight'] * 60):
                print("ship_to_fight")
                clickBtn(images['ping-ship'], 0.9)
                time_start["ship_to_fight"] = actual_time
                #print("Ship to fight")
                ship_to_fight()
        
        print("Time to close fight window:")
        print(actual_time - time_start["ship_tela_boss"])
        print((time_to_check['ship_tela_boss'] * 60))
        if actual_time - time_start["ship_tela_boss"] > (time_to_check['ship_tela_boss'] * 60):
                print("ship_tela_boss")
                clickBtn(images['ping-ship'])
                time_start["ship_tela_boss"] = actual_time
                #print("Ship tela boss")
                ship_tela_boss()

        if actual_time - time_start["continue"] > time_to_check['continue']:
                print("go_to_continue")
                clickBtn(images['ping-ship'])
                time_start["continue"] = actual_time
                #print("Ship continue")
                go_to_continue()   

        if actual_time - time_start["login"] > addRandomness(time_to_check['login'] * 60):
            print("flush")
            clickBtn(images['ping-ship'])
            sys.stdout.flush()
            print("login")
            time_start["login"] = actual_time
            login() 

        if actual_time - time_start["close"] > time_to_check['close']:
            print("tela_close")
            clickBtn(images['ping-ship'])
            time_start["close"] = actual_time
            #print("Ship continue")
            tela_close()   

        time.sleep(0.3)

        # if now - last["login"] > addRandomness(t['check_for_login'] * 60):
        #     sys.stdout.flush()
        #     last["login"] = now
        #     login()

        if now - last["refresh_heroes"] > addRandomness( t['refresh_heroes_positions'] * 10):
            logger('Refresh heroes')
            last["refresh_heroes"] = now
            refreshHeroesPositions()

        if now - last["boss_hunt"] > addRandomness(t['boss_hunt'] * 60):

            if clickBtn(images['boss_hunt']):
                last["boss_hunt"] = now
                logger('Boss hunt')
                loggerBossHunt()
                time.sleep(30)
                if(clickBtn(images['vs_icon'])):
                    loggerBossFight()


       

        if now - last["tap"] > 3:
            logger('Tap')
            last["tap"] = now
            clickBtn(images['luna_icon'])
            clickBtn(images['tap_to_open'])

        sys.stdout.flush()

        time.sleep(1)

if __name__ == '__main__':



    main()


# colocar o botao em pt
# soh resetar posiçoes se n tiver clickado em newmap em x segundos


