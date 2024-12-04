import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import random
import pandas as pd
import os
from PIL import ImageTk, Image
from moviepy.editor import VideoFileClip, concatenate_videoclips

class EmotionalRecognitionApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Emotional Recognition Testing")
        self.master.geometry("1280x720")

        # Initialize variables
        self.video_list = []  # List of video file paths
        self.video_playing = False
        self.answers = []  # List to store answers
        self.current_video = None  # Currently displayed video
        self.current_video_index = -1  # Index of the current video in the list
        self.total_videos = 720
        self.videos_done = 0
        self.progress = 0
        self.autosave_count = 0

        # Add widgets
        self.create_widgets()

        # Load video list
        self.load_video_list()

        # Disable emotion buttons initially
        self.disable_emotion_buttons()

    def disable_emotion_buttons(self):
        # Helper function to disable all emotion buttons
        for widget in self.emotion_frame.winfo_children():
            widget.config(state="disabled")

    def enable_emotion_buttons(self):
        # Helper function to enable all emotion buttons
        for widget in self.emotion_frame.winfo_children():
            widget.config(state="normal")

    def create_widgets(self):
        # Create description label and start button
        description_text = (
            "This program is designed to help train your emotional recognition "
            "skills by watching videos of people expressing different emotions. "
            "Click the 'Start' button to begin."
        )
        self.description_label = tk.Label(self.master, text=description_text, wraplength=600, justify="left")
        self.description_label.pack(pady=10)
        self.start_button = tk.Button(self.master, text="Start", command=self.start_program)
        self.start_button.pack(pady=10)

        # Create video player widget (requires video playback implementation)
        self.video_canvas = tk.Canvas(self.master, bg="black", width=1275, height=715)
        self.video_canvas.pack(pady=10)

        # Create emotion buttons (fear, happy, sad, angry, disgust, neutral)
        self.emotion_frame = tk.Frame(self.master)
        self.emotion_frame.pack(pady=10)
        emotions = [
            ("Angst", "#FF5733"), 
            ("Freude", "#FFFF66"), 
            ("Trauer", "#4DA6FF"), 
            ("Wut", "#B22222"), 
            ("Ekel", "#3CB371"), 
            ("Neutral", "#C0C0C0")
        ]
        for emotion, color in emotions:
            button = ttk.Button(
                self.emotion_frame,
                text=emotion,
                command=lambda e=emotion: self.on_emotion_click(e),
                style=f"{emotion}Button.TButton"
            )
            style = ttk.Style()
            style.configure(f"{emotion}Button.TButton", background=color, activebackground=color)

            button.pack(side="left", padx=5)

        # Create back button
        self.back_button = tk.Button(self.master, text="Zurück", command=self.on_back_click)
        self.back_button.pack(pady=10)

        # Create progress bar
        self.progress_bar = ttk.Progressbar(
            self.master, orient="horizontal", length=self.total_videos, mode="determinate"
        )
        self.progress_bar.pack(pady=10)

        # Create export button in the final window (requires implementation of final window)
        self.export_button = tk.Button(self.master, text="Export", command=self.on_export_click)

    def load_video_list(self):
        # Load the list of video file paths from the 'videos' folder
        video_folder = 'Testset'
        self.video_list = [
            os.path.join(video_folder, f) for f in os.listdir(video_folder)
            if os.path.isfile(os.path.join(video_folder, f))
        ]
        random.shuffle(self.video_list)
        self.total_videos = len(self.video_list)

    def start_program(self):
        self.start_button.config(state='disabled')
        self.export_button.pack_forget()
        self.play_next_video()

    def play_next_video(self):
        if self.videos_done < self.total_videos:
            self.current_video_index = (self.current_video_index + 1) % len(self.video_list)
            self.current_video = self.video_list[self.current_video_index]
            self.play_video(self.current_video)
        else:
            self.show_final_window()

    def play_video(self, video_path):
        self.video_clip = VideoFileClip(video_path)
        self.video_playing = True
        self.current_time = 0
        self.master.after(1, self.update_video_frame)

    def update_video_frame(self):
        if not self.video_playing:
            return

        if self.current_time < self.video_clip.duration:
            frame = self.video_clip.get_frame(self.current_time)
            image = Image.fromarray(frame)
            self.photo = ImageTk.PhotoImage(image=image)
            self.video_canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
            self.current_time += 1 / self.video_clip.fps
            self.master.after(int(1000 // self.video_clip.fps), self.update_video_frame)
        else:
            self.pause_video()

    def on_emotion_click(self, emotion):
        self.answers.append((self.current_video, emotion))
        self.videos_done += 1
        self.update_progress()

        # Check if 5 videos have been completed
        if self.videos_done % 5 == 0:
            self.autosave_answers()

        self.play_next_video()

        # Disable emotion buttons after click
        self.disable_emotion_buttons()
    
    def autosave_answers(self):
        self.autosave_count += 1
        if self.autosave_count == 1:
            # Create a new file for autosaving
            self.autosave_file_path = f"autosave_{self.autosave_count}.csv"
        else:
            # Overwrite the existing autosave file
            self.autosave_file_path = f"autosave_{self.autosave_count}.csv"

        df = pd.DataFrame(self.answers, columns=["Video", "Emotion"])
        df.to_csv(self.autosave_file_path, index=False)

    def pause_video(self):
        self.video_playing = False
        # Enable emotion buttons when video stops playing
        self.enable_emotion_buttons()

    def on_back_click(self):
        if self.videos_done > 0:
            self.disable_emotion_buttons()
            self.answers.pop()
            self.videos_done -= 1
            self.update_progress()
            self.current_video_index = (self.current_video_index - 2) % len(self.video_list)
            self.play_next_video()

    def update_progress(self):
        self.progress = (self.videos_done / self.total_videos) * 100
        self.progress_bar['value'] = self.progress

    def show_final_window(self):
        self.start_button.config(state='normal')
        self.export_button.pack(pady=10)

    def on_export_click(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                 filetypes=[("CSV files", "*.csv")],
                                                 initialfile="Emotional Tratrining NAME.csv")
        if file_path:
            df = pd.DataFrame(self.answers, columns=["Video", "Emotion"])
            df.to_csv(file_path, index=False)
            self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = EmotionalRecognitionApp(root)
    root.mainloop()