import tkinter as tk
from tkinter import filedialog
from tkinter.ttk import Progressbar
import customtkinter as ctk
from mutagen.mp3 import MP3
import threading
import pygame
import time
import os

class MusicPlayer:
    def __init__(self, master):
        self.master = master
        self.current_position = 0
        self.paused = False
        self.selected_folder_path = ""

        pygame.mixer.init()

        self.create_widgets()


    def create_widgets(self):
        self.l_music_player = ctk.CTkLabel(self.master, text="Music Player", font=("TkDefaultFont", 30, "bold"))
        self.l_music_player.pack(pady=10)

        self.btn_select_folder = ctk.CTkButton(self.master, text="Select Music Folder",
                                               command=self.select_music_folder,
                                               font=("TkDefaultFont", 18))
        self.btn_select_folder.pack(pady=20)

        self.lbox = tk.Listbox(self.master, width=50, font=("TkDefaultFont", 16))
        self.lbox.pack(pady=10)

        self.btn_frame = ctk.CTkFrame(self.master)
        self.btn_frame.pack(pady=20)

        self.btn_previous = ctk.CTkButton(self.btn_frame, text="<", command=self.previous_song,
                                          width=50, font=("TkDefaultFont", 18))
        self.btn_previous.pack(side=tk.LEFT, padx=5)

        self.btn_play = ctk.CTkButton(self.btn_frame, text="Play", command=self.play_music, width=50,
                                      font=("TkDefaultFont", 18))
        self.btn_play.pack(side=tk.LEFT, padx=5)

        self.btn_pause = ctk.CTkButton(self.btn_frame, text="Pause", command=self.pause_music, width=50,
                                       font=("TkDefaultFont", 18))
        self.btn_pause.pack(side=tk.LEFT, padx=5)

        self.btn_next = ctk.CTkButton(self.btn_frame, text=">", command=self.next_song, width=50,
                                      font=("TkDefaultFont", 18))
        self.btn_next.pack(side=tk.LEFT, padx=5)
        
        self.progress_frame = ctk.CTkFrame(self.master)
        self.progress_frame.pack(pady=10)

        self.lbl_current_time = ctk.CTkLabel(self.progress_frame, text="0:00", font=("TkDefaultFont", 12))
        self.lbl_current_time.pack(side=tk.LEFT, padx=10)

        self.pbar = Progressbar(self.progress_frame, length=300, mode="determinate", maximum=100)
        self.pbar.pack(side=tk.LEFT, padx=10)

        self.lbl_total_time = ctk.CTkLabel(self.progress_frame, text="0:00", font=("TkDefaultFont", 12))
        self.lbl_total_time.pack(side=tk.LEFT, padx=10)


    def update_progress(self):
        while True:
            if pygame.mixer.music.get_busy() and not self.paused:
                self.current_position = pygame.mixer.music.get_pos() / 1000
                self.pbar['value'] = self.current_position

                current_time_str = time.strftime('%M:%S', time.gmtime(self.current_position))
                self.lbl_current_time.configure(text=current_time_str)

                if self.current_position >= self.pbar['maximum']:
                    self.next_song()
                    continue

                audio = MP3(os.path.join(self.selected_folder_path, self.lbox.get(tk.ACTIVE)))

                self.master.update()

        time.sleep(0.1)


    def select_music_folder(self):
        self.selected_folder_path = filedialog.askdirectory()
        if self.selected_folder_path:
            self.lbox.delete(0, tk.END)
            for file_name in os.listdir(self.selected_folder_path):
                if file_name.endswith(".mp3"):
                    self.lbox.insert(tk.END, file_name)


    def next_song(self):
        if len(self.lbox.curselection()) > 0:
            current_index = self.lbox.curselection()[0]
            if current_index < self.lbox.size() - 1:
                self.lbox.selection_clear(0, tk.END)
                self.lbox.selection_set(current_index + 1)
                self.play_selected_song()
                self.update_labels()  # Добавлен вызов для обновления меток


    def previous_song(self):
        if len(self.lbox.curselection()) > 0:
            current_index = self.lbox.curselection()[0]
            if current_index > 0:
                self.lbox.selection_clear(0, tk.END)
                self.lbox.selection_set(current_index - 1)
                self.play_selected_song()
                self.update_labels()  # Добавлен вызов для обновления меток
                
                
    def update_labels(self):
        if len(self.lbox.curselection()) > 0:
            current_index = self.lbox.curselection()[0]
            selected_song = self.lbox.get(current_index)
            full_path = os.path.join(self.selected_folder_path, selected_song)

            audio = MP3(full_path)
            song_duration = audio.info.length

            # Обновление меток
            current_time_str = time.strftime('%M:%S', time.gmtime(self.current_position))
            total_time_str = time.strftime('%M:%S', time.gmtime(song_duration))

            self.lbl_current_time.configure(text=current_time_str)
            self.lbl_total_time.configure(text=total_time_str)


    def play_music(self):
        if self.paused:
            pygame.mixer.music.unpause()
            self.paused = False
        else:
            self.play_selected_song()


    def play_selected_song(self):
        if len(self.lbox.curselection()) > 0:
            current_index = self.lbox.curselection()[0]
            selected_song = self.lbox.get(current_index)
            full_path = os.path.join(self.selected_folder_path, selected_song)

            self.current_position = 0

            pygame.mixer.music.load(full_path)
            pygame.mixer.music.play(start=self.current_position)
            self.paused = False
            audio = MP3(full_path)
            song_duration = audio.info.length
            self.pbar['maximum'] = song_duration
        
            total_time_str = time.strftime('%M:%S', time.gmtime(song_duration))
            self.lbl_total_time.configure(text=total_time_str)


    def pause_music(self):
        pygame.mixer.music.pause()
        self.paused = True


    def stop_music(self):
        pygame.mixer.music.stop()
        self.paused = False


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("green")
    root = ctk.CTk()
    root.title("Music Player")
    root.geometry("600x550")
    root.resizable(False, False)

    player = MusicPlayer(root)

    progress_thread = threading.Thread(target=player.update_progress)
    progress_thread.daemon = True
    progress_thread.start()

    root.mainloop()
