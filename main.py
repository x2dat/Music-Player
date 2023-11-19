import os
import threading
import time
from tkinter import *
from tkinter import filedialog
import tkinter as tk
from tkinter import ttk
from colorama import Fore
from mutagen.mp3 import MP3
from pygame import mixer

mixer.init()
o = 1

# Store the current position of the music
current_position = 0
paused = False
selected_folder_path = ""  # Store the selected folder path


def update_progress():
    global current_position
    while True:
        if mixer.music.get_busy() and not paused:
            current_position = mixer.music.get_pos() / 1000
            pbar["value"] = current_position

            # Check if the current song has reached its maximum duration
            if current_position >= pbar["maximum"]:
                stop_music()  # Stop the music playback
                pbar["value"] = 0  # Reset the pbar

            current_time = time.strftime('%M:%S', time.gmtime(current_position))
            time_label.config(text=f"Time Elapsed: {current_time}")

            remaining_time = time.strftime('%M:%S', time.gmtime(pbar["maximum"] - current_position))
            remaining_time_label.config(text=f"Time Left: {remaining_time}")

            window.update()
        time.sleep(0.1)


# Create a thread to update the progress bar and time labels
pt = threading.Thread(target=update_progress)
pt.daemon = True
pt.start()


def select_music_folder():
    global selected_folder_path
    selected_folder_path = filedialog.askdirectory()
    if selected_folder_path:
        lbox.delete(0, tk.END)
        for filename in os.listdir(selected_folder_path):
            if filename.endswith(".mp3"):
                lbox.insert(tk.END, filename)  # Insert only the filename, not the full path
        print(Fore.LIGHTGREEN_EX, "Folder selected", Fore.LIGHTWHITE_EX)


def previous_song():
    if len(lbox.curselection()) > 0:
        current_index = lbox.curselection()[0]
        if current_index > 0:
            lbox.selection_clear(0, tk.END)
            lbox.selection_set(current_index - 1)
            play_selected_song()
    print(Fore.LIGHTGREEN_EX, "<", Fore.LIGHTWHITE_EX)


def next_song():
    if len(lbox.curselection()) > 0:
        current_index = lbox.curselection()[0]
        if current_index < lbox.size() - 1:
            lbox.selection_clear(0, tk.END)
            lbox.selection_set(current_index + 1)
            play_selected_song()
    print(Fore.LIGHTGREEN_EX, ">", Fore.LIGHTWHITE_EX)


def play_selected_song():
    stop_music()
    play_music()


def play_music():
    global paused, current_position
    if paused:
        mixer.music.unpause()
        paused = False
    else:
        if len(lbox.curselection()) > 0:
            selected_song = lbox.get(lbox.curselection())
            song_path = os.path.join(selected_folder_path, selected_song)
            audio = MP3(song_path)
            mixer.music.load(song_path)
            mixer.music.play()
            paused = False
            pbar["maximum"] = audio.info.length  # Set the maximum value of the progress bar to the song duration
            current_position = 0  # Reset the current position of the music


def pause_music():
    global paused
    if not paused:
        mixer.music.pause()
        paused = True


def stop_music():
    global paused, current_position
    mixer.music.stop()
    paused = False
    pbar["value"] = 0  # Reset the progress bar to zero
    current_position = 0  # Reset the current position of the music


# Create the main window
window = Tk()
window.title("Music Player")
window.geometry("500x500")

# Create a label for the time elapsed and remaining time
time_label = Label(window, text="Time Elapsed: 00:00")
time_label.pack(pady=5)

remaining_time_label = Label(window, text="Time Left: 00:00")
remaining_time_label.pack(pady=5)

# Create a progress bar to show the progress of the song playback
pbar = ttk.Progressbar(window, orient=HORIZONTAL, length=300, mode='determinate')
pbar.pack(pady=10)

# Create a listbox to display the available songs in the selected folder
lbox = Listbox(window, height=15, width=70)
lbox.pack(pady=10)

button_frame = tk.Frame(window)

play_button = Button(window, text="Play", command=play_selected_song)
play_button.pack(pady=10)
play_button.pack(side=tk.LEFT, padx=40)

select_folder_button = Button(window, text="Select Music Folder", command=select_music_folder)
select_folder_button.pack(pady=10)
select_folder_button.pack(side=tk.LEFT, padx=80)

stop_button = Button(window, text="Stop", command=stop_music)
stop_button.pack(pady=10)
stop_button.pack(side=tk.RIGHT, padx=40)

button_frame.pack(pady=10)

window.mainloop()
