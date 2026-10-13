import tkinter as tk
import time
import random
import pyautogui
import csv
from datetime import datetime

# Config
num_targets = 10
target_radius = 30
screen_w, screen_h = pyautogui.size()
results = []

def create_target():
    x = random.randint(target_radius, screen_w - target_radius)
    y = random.randint(target_radius, screen_h - target_radius)
    return x, y

def on_click(event):
    global start_time, target_id, target_x, target_y

    # Get cursor position
    mouse_x, mouse_y = pyautogui.position()
    dist = ((mouse_x - target_x) ** 2 + (mouse_y - target_y) ** 2) ** 0.5

    # Record time and distance
    click_time = time.time() - start_time
    results.append((target_id + 1, dist, round(click_time, 2)))

    canvas.delete("all")
    target_id += 1

    if target_id < num_targets:
        spawn_target()
    else:
        canvas.delete("all")
        canvas.create_text(screen_w//2, screen_h//2, text="Test Complete!", font=("Helvetica", 32))
        save_results()
        print("\nTest Results appended to eye_tracker_results.csv")
        root.after(5000, root.destroy)

def save_results():
    with open("eye_tracker_results.csv", mode="a", newline="") as file:
        writer = csv.writer(file)
        # Add test round header with timestamp
        writer.writerow([])
        writer.writerow([f"Test Round - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"])
        writer.writerow(["Target", "Distance (pixels)", "Time (seconds)"])
        for row in results:
            writer.writerow([row[0], int(row[1]), row[2]])

def spawn_target():
    global target_x, target_y, start_time
    target_x, target_y = create_target()
    canvas.create_oval(
        target_x - target_radius, target_y - target_radius,
        target_x + target_radius, target_y + target_radius,
        fill="red", outline=""
    )
    start_time = time.time()

# Setup GUI
root = tk.Tk()
root.attributes('-fullscreen', True)
root.configure(bg='white')
canvas = tk.Canvas(root, width=screen_w, height=screen_h, bg='white', highlightthickness=0)
canvas.pack()

# Start test
target_id = 0
canvas.bind("<Button-1>", on_click)
spawn_target()

root.mainloop()
