import tkinter as tk
from tkinter import font
from load_data import DepartureBoard
import RPi.GPIO as GPIO
import subprocess

def turn_on_screen():
    subprocess.run(["vcgencmd", "display_power", "1"])

update_job = None
button_lock = False

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
    dep = DepartureBoard()
    departures = DepartureBoard.get_departures(dep)

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

root = tk.Tk()
root.title("Abfahrtstafel")

departure_frame = tk.Frame(root, bg="black")
departure_frame.pack(fill=tk.BOTH, expand=True)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.add_event_detect(10, GPIO.RISING, callback=button_callback)

root.attributes("-fullscreen", True)
root.bind("<Escape>", lambda e: root.destroy())
update_departure_board()
root.mainloop()
