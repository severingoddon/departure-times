import os
import tkinter as tk
from datetime import datetime
from tkinter import font
from load_data import DepartureBoard
import RPi.GPIO as GPIO
import subprocess
import time

command = "unclutter -idle 0"
subprocess.Popen(command, shell=True)

GPIO.setmode(GPIO.BOARD)
PIR_PIN = 10
update_job = None
button_lock = False
pir_lock = False
motion_detected = False
loadType = "hb"

dep = DepartureBoard()


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


def button_callback_hb(channel):
    global update_job
    global button_lock
    global loadType

    if button_lock:
        return

    loadType = "hb"
    button_lock = True
    root.after(2000, unlock_button)
    root.after_cancel(update_job)
    update_departure_board()

def button_callback_esch(channel):
    global update_job
    global button_lock
    global loadType

    if button_lock:
        return

    loadType = "esch"
    button_lock = True
    root.after(2000, unlock_button)
    root.after_cancel(update_job)
    update_departure_board()


def button_callback_bus(channel):
    global update_job
    global button_lock
    global loadType

    if button_lock:
        return

    loadType = "bus"
    button_lock = True
    root.after(2000, unlock_button)
    root.after_cancel(update_job)
    update_departure_board()


def pir_callback(channel):
    global update_job
    global pir_lock

    if pir_lock:
        return

    pir_lock = True
    root.after(30000, unlock_pir)
    root.after_cancel(update_job)
    update_departure_board()


def unlock_button():
    global button_lock
    button_lock = False


def unlock_pir():
    global pir_lock
    pir_lock = False


def update_departure_board():
    global update_job
    global motion_detected
    global dep
    global loadType

    if GPIO.input(PIR_PIN) == 1:
        turn_on_screen()
        departures = DepartureBoard.get_departures(dep, loadType)
        write_to_file()  # only for debug purpose

        for widget in departure_frame.winfo_children():
            widget.destroy()

        max_width = 420
        font_size = max_width // 60
        custom_font = font.Font(family="Goddonis Font", size=font_size + 62)

        for index, departure in enumerate(departures, start=1):
            line_label = tk.Label(departure_frame, text=departure['line'], font=custom_font, fg="#fb7500", bg='black',
                                  anchor=tk.E)
            direction_label = tk.Label(departure_frame, text=departure['direction'], font=custom_font, fg="#fb7500",
                                       bg='black', anchor=tk.W)

            if departure['minutes_until_departure'] == 0:
                minutes_label = tk.Label(departure_frame, text=f"ÿ", font=custom_font,
                                         fg="#fb7500", bg='black', anchor=tk.W)

            else:
                minutes_label = tk.Label(departure_frame, text=f"{departure['minutes_until_departure']}'",
                                         font=custom_font,
                                         fg="#fb7500", bg='black', anchor=tk.W)

            line_label.grid(row=index, column=0, sticky="ew", padx=(40, 60))
            direction_label.grid(row=index, column=1, sticky="ew", padx=(0, 65))
            minutes_label.grid(row=index, column=2, sticky="ew")
    else:
        turn_off_screen()

    update_job = root.after(30000, update_departure_board)


def setup_gpio():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.add_event_detect(16, GPIO.RISING, callback=button_callback_hb) # Zürich HB Button
    GPIO.add_event_detect(22, GPIO.RISING, callback=button_callback_esch) # Escherwyss Button
    GPIO.add_event_detect(18, GPIO.RISING, callback=button_callback_bus)  # Bus 32 Button
    GPIO.add_event_detect(10, GPIO.RISING, callback=pir_callback)


root = tk.Tk()
root.title("Abfahrtstafel")

departure_frame = tk.Frame(root, bg="black", pady=10)
departure_frame.pack(fill=tk.BOTH, expand=True)

setup_gpio()
root.attributes("-fullscreen", True)
root.bind("<Escape>", lambda e: root.destroy())
update_departure_board()

root.mainloop()