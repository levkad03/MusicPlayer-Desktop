import tkinter as tk
from tkinter import filedialog
from tkinter.ttk import Progressbar
import customtkinter as ctk
from mutagen.mp3 import MP3
import threading
import pygame
import time
import os

pygame.mixer.init()

current_position = 0
paused = False
selected_folder_path = ""


def update_progress():
    global current_position
    while True:
        if pygame.mixer.music.get_busy() and not paused:
            current_position = pygame.mixer.music.get_pos() / 1000
            pbar['value'] = current_position
            
            # Check if the current song has reached its maximum duration
            if current_position >= pbar['maximum']:
                stop_music()
                pbar['value'] = 0
            
            window.update()
        
        time.sleep(0.1)


# Create a thread to update the progress bar
pt = threading.Thread(target=update_progress)
pt.daemon = True
pt.start()


def select_music_folder():
    global selected_folder_path
    selected_folder_path = filedialog.askdirectory()
    if selected_folder_path:
        lbox.delete(0, tk.END)
        for file_name in os.listdir(selected_folder_path):
            if file_name.endswith(".mp3"):
                lbox.insert(tk.END, file_name)
                

def previous_song():
    if len(lbox.curselection()) > 0:
        current_index = lbox.curselection()[0]
        if current_index > 0:
            lbox.selection_clear(0, tk.END)
            lbox.selection_set(current_index - 1)
            play_selected_song()
            
            
def next_song():
    if len(lbox.curselection()) > 0:
        current_index = lbox.curselection()[0]
        if current_index < lbox.size() - 1:
            lbox.selection_clear(0, tk.END)
            lbox.selection_set(current_index + 1)
            play_selected_song()
            
            
def play_music():
    global paused
    if paused:
        pygame.mixer.music.unpause()
        paused = False
    else:
        play_selected_song()


def play_selected_song():
    global current_position, paused
    
    if len(lbox.curselection()) > 0:
        current_index = lbox.curselection()[0]
        selected_song = lbox.get(current_index)
        full_path = os.path.join(selected_folder_path, selected_song)
        pygame.mixer.music.load(full_path)
        pygame.mixer.music.play(start=current_position)
        paused = False
        audio = MP3(full_path)
        song_duration = audio.info.length
        pbar['maximum'] = song_duration
        

def pause_music():
    global paused
    pygame.mixer.music.pause()
    paused = True
    

def stop_music():
    global paused
    pygame.mixer.music.stop()
    paused = False


# Create the main window   
window = tk.Tk()
window.title("Music Player")
window.geometry("600x500")

# Create a label for the music player title
l_music_player = tk.Label(window, text="Music Player", font=("TkDefaultFont", 30, "bold"))
l_music_player.pack(pady=10)

# Create a button to select the music folder
btn_select_folder = ctk.CTkButton(window, text="Select Music Folder",
                                  command=select_music_folder,
                                  font=("TkDefaultFont", 18))

btn_select_folder.pack(pady=20)

# Create a listbox to display the available songs
lbox = tk.Listbox(window, width=50, font=("TkDefaultFont", 16))
lbox.pack(pady=10)

# Create a frame to hold the control buttons
btn_frame = tk.Frame(window)
btn_frame.pack(pady=20)

# Create a button to go to the previous song
btn_previous = ctk.CTkButton(btn_frame, text="<", command=previous_song,
                            width=50, font=("TkDefaultFont", 18))
btn_previous.pack(side=tk.LEFT, padx=5)

# Create a button to play the music
btn_play = ctk.CTkButton(btn_frame, text="Play", command=play_music, width=50,
                         font=("TkDefaultFont", 18))
btn_play.pack(side=tk.LEFT, padx=5)

# Create a button to pause the music
btn_pause = ctk.CTkButton(btn_frame, text="Pause", command=pause_music, width=50,
                          font=("TkDefaultFont", 18))
btn_pause.pack(side=tk.LEFT, padx=5)

# Create a button to go to the next song
btn_next = ctk.CTkButton(btn_frame, text=">", command=next_song, width=50,
                         font=("TkDefaultFont", 18))
btn_next.pack(side=tk.LEFT, padx=5)

# Create a progress bar to indicate the current song's progress
pbar = Progressbar(window, length=300, mode="determinate")
pbar.pack(pady=10)

window.mainloop()
