import tkinter as tk
from tkinter import font
from loadDataNewAPI import DepartureBoardNew

def update_departure_board():
    dep = DepartureBoardNew()
    departures = DepartureBoardNew.get_departures(dep, "esch")

    for widget in departure_frame.winfo_children():
        widget.destroy()

    max_width = 420
    font_size = max_width // 60
    custom_font = font.Font(family="Goddonis Font", size=font_size + 60)

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

    root.after(30000, update_departure_board)

root = tk.Tk()
root.title("Abfahrtstafel")

departure_frame = tk.Frame(root, bg="black")
departure_frame.pack(fill=tk.BOTH, expand=True)


root.attributes("-fullscreen", True)
root.bind("<Escape>", lambda e: root.destroy())
update_departure_board()
root.mainloop()