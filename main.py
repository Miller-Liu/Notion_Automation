from Home_Page.Home_Page import *
from Productivity.Calendar_Page import *
import json
import os
import sys
import time
import pyautogui
import keyboard
from multiprocessing import Process
from multiprocessing import freeze_support
import multiprocessing

bundle_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
path = os.path.abspath(os.path.join(bundle_dir, 'IDS.json'))
file = open(path)

# file = open("IDS.json")
data = json.load(file)


def run_periodically(global_var, last_time, IDS):
    while True:
        if global_var.value:
            last_time = fun_home_page(last_time, IDS)
            time.sleep(60*10)


def switch_periodic_function(global_var):
    global_var.value = not global_var.value


def specific_functions_controller(IDS):
    controller_dict = {"2": productivity_functions}
    print(
        f'''
Below are the shortcuts corresponding with each function:
    Home page functions: 1
    Productivity functions: 2
        '''
    )
    choice = input("Please enter your choice: ")
    if choice in controller_dict.keys():
        controller_dict[choice](IDS)
    else:
        if choice != "q":
            print("Invalid entry")
            specific_functions_controller(IDS)


def controller(global_var, IDS):
    controller_dict = {"1": sync_google_calendar, "2": daily_reset, "3": switch_periodic_function,
                       "4": sync_to_do_list_and_task_list, "5": specific_functions_controller}
    print(
        f'''
Below are the shortcuts corresponding with each function:
    Sync google calendar with calendar view: 1
    Daily update: 2
    Switch periodic functions to {not global_var.value}: 3
    Sync to do list and task list database: 4
    Specific functions: 5
        '''
    )
    sys.stdin = open(0)
    choice = input("Please enter your choice: ")
    if choice in controller_dict.keys():
        if choice != "5" and choice != "1":
            pyautogui.getWindowsWithTitle('Notion Automation App')[0].minimize()
        if choice == "1":
            months_from_now = int(input("Please enter how many months from now: "))
            controller_dict[choice](IDS, months_from_now)
        elif choice == "3":
            controller_dict[choice](global_var)
        else:
            controller_dict[choice](IDS)
    else:
        if choice != "q":
            print("Invalid entry")
            controller(global_var, IDS)


def activated(global_var, IDS):
    win = pyautogui.getWindowsWithTitle('Notion Automation App')[0]
    win.maximize()
    controller(global_var, IDS)
    print("finished")
    win.maximize()
    time.sleep(3)
    win.minimize()
    os.system("cls")


def wait_for_hotkey(global_var, IDS):
    win = pyautogui.getWindowsWithTitle('Notion Automation App')[0]
    win.maximize()
    win.minimize()
    keyboard.add_hotkey("ctrl+shift+alt+space", activated, args=(global_var, IDS, ))
    keyboard.wait()


if __name__ == '__main__':
    freeze_support()
    variable = multiprocessing.Value("i", True)
    p1 = Process(target=wait_for_hotkey, args=(variable, data, ))
    p1.start()
    p2 = Process(target=run_periodically, args=(variable, -1, data, ))
    p2.start()
    p1.join()
    p2.join()
