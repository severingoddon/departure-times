import os
import tkinter as tk
from datetime import datetime
from tkinter import font
from load_data import DepartureBoard
import RPi.GPIO as GPIO
import subprocess
import time

# only for debug purpose
def write_to_file():
    directory = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(directory, "logfile.txt")
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(file_path, "a") as file:
        file.write(f"{current_time} - load called\n")

def turn_on_screen():
    subprocess.run(["vcgencmd", "display_power", "1"])

def turn_off_screen():
    subprocess.run(["vcgencmd", "display_power", "0"])

update_job = None
button_lock = False
motion_detected = False

def button_callback(channel):
    global update_job
    global button_lock

    if button_lock:
        return

    button_lock = True
    root.after(2000, unlock_button)
    root.after_cancel(update_job)
    update_departure_board()

def unlock_button():
    global button_lock
    button_lock = False

def update_departure_board():
    turn_on_screen()
    global update_job
    global motion_detected

    if not motion_detected:
        update_job = root.after(30000, update_departure_board)
        return

    dep = DepartureBoard()
    departures = DepartureBoard.get_departures(dep)
    write_to_file() # only for debug purpose

    for widget in departure_frame.winfo_children():
        widget.destroy()

    max_width = 420
    font_size = max_width // 60
    custom_font = font.Font(family="Goddonis Font", size=font_size + 64)

    for index, departure in enumerate(departures, start=1):
        line_label = tk.Label(departure_frame, text=departure['line'], font=custom_font, fg="#fb7500", bg='black',
                              anchor=tk.E)
        direction_label = tk.Label(departure_frame, text=departure['direction'], font=custom_font, fg="#fb7500",
                                   bg='black', anchor=tk.W)

        if departure['minutes_until_departure'] == 0:
            minutes_label = tk.Label(departure_frame, text=f"ÿ", font=custom_font,
                                     fg="#fb7500", bg='black', anchor=tk.W)

        else:
            minutes_label = tk.Label(departure_frame, text=f"{departure['minutes_until_departure']}'", font=custom_font,
                                     fg="#fb7500", bg='black', anchor=tk.W)

        line_label.grid(row=index, column=0, sticky="ew", padx=(40, 60))
        direction_label.grid(row=index, column=1, sticky="ew", padx=(0, 65))
        minutes_label.grid(row=index, column=2, sticky="ew")


    update_job = root.after(30000, update_departure_board)

def pir_motion_detected(channel):
    global motion_detected
    turn_on_screen()
    if not motion_detected:
        motion_detected = True
        time.sleep(300)
        turn_off_screen()
        motion_detected = False


def setup_pir_sensor():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # Button
    GPIO.setup(16, GPIO.IN)  # PIR-Sensor
    GPIO.add_event_detect(10, GPIO.RISING, callback=button_callback)
    GPIO.add_event_detect(16, GPIO.RISING, callback=pir_motion_detected)

root = tk.Tk()
root.title("Abfahrtstafel")

departure_frame = tk.Frame(root, bg="black")
departure_frame.pack(fill=tk.BOTH, expand=True)

setup_pir_sensor()

root.attributes("-fullscreen", True)
root.bind("<Escape>", lambda e: root.destroy())

root.mainloop()
