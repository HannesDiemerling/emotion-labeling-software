import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import cv2
import random
import pandas as pd
import os
from PIL import Image, ImageTk

class EmotionalRecognitionApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Emotional Recognition Training")
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

        # Initialize correct answers dictionary
        self.correct_answers = {}
        self.load_correct_answers()

        # Add widgets
        self.create_widgets()

        # Load video list
        self.load_video_list()

        # Disable emotion buttons initially
        self.disable_emotion_buttons()

    def load_correct_answers(self):
        # Load correct answers from 'selected_videos.csv'
        df = pd.read_csv('selected_videos.csv')
        for _, row in df.iterrows():
            self.correct_answers["Trainingsset/"+row['File Name']] = row['Emotion']

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

        # Create progress bar
        self.progress_bar = ttk.Progressbar(
            self.master, orient="horizontal", length=self.total_videos, mode="determinate"
        )
        self.progress_bar.pack(pady=10)

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
            button = tk.Button(
                self.emotion_frame,
                text=emotion,
                bg=color,
                activebackground=color,
                command=lambda e=emotion: self.on_emotion_click(e),
            )
            button.pack(side="left", padx=10)

    def load_video_list(self):
        # Load video list from a directory
        video_directory = 'Trainingsset'
        for root, _, files in os.walk(video_directory):
            for file in files:
                if file.endswith('.mp4'):
                    self.video_list.append(os.path.join(root, file))

    def play_next_video(self):
        # Play the next video in the list
        self.current_video_index += 1
        if self.current_video_index < len(self.video_list):
            self.current_video = self.video_list[self.current_video_index]
            self.play_video(self.current_video) 
        else:
            self.end_program()

    def play_video(self, video_path):
        # Play the video using OpenCV and display it in the video_canvas
        cap = cv2.VideoCapture(video_path)

        # Helper function to update the video frame in the canvas
        def update_frame():
            ret, frame = cap.read()
            if ret:
                cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
                img = Image.fromarray(cv2image)
                imgtk = ImageTk.PhotoImage(image=img)
                self.video_canvas.create_image(0, 0, anchor="nw", image=imgtk)
                self.video_canvas.imgtk = imgtk  # Keep a reference to the image to avoid garbage collection
                self.video_canvas.after(20, update_frame)
            else:
                cap.release()
                self.enable_emotion_buttons()  # Enable emotion buttons after video ends

        # Update the first frame and start the video playback loop
        update_frame()

    def on_emotion_click(self, emotion):
        # Handle emotion button click
        self.answers.append((self.current_video, emotion))
        self.disable_emotion_buttons()
        self.videos_done += 1
        self.progress_bar["value"] = self.videos_done
        self.progress = (self.videos_done / self.total_videos) * 100
        self.progress_bar.update()

        if self.videos_done < self.total_videos:
            self.play_next_video()
            self.enable_emotion_buttons()
        else:
            self.end_program()

    def start_program(self):
        # Start the program by playing the first video
        self.start_button.config(state="disabled")
        self.play_next_video()
        self.enable_emotion_buttons()

    def end_program(self):
        # End the program and show results
        self.disable_emotion_buttons()
        self.start_button.config(text="Restart", command=self.restart_program, state="normal")

        # Calculate and display results
        correct_answers_count = 0
        for answer in self.answers:
            video, emotion = answer
            if self.correct_answers[video] == emotion:
                correct_answers_count += 1

        accuracy = (correct_answers_count / len(self.answers)) * 100
        result_text = f"Accuracy: {accuracy:.2f}%"
        self.result_label = tk.Label(self.master, text=result_text)
        self.result_label.pack(pady=10)

    def restart_program(self):
        # Restart the program
        self.answers = []
        self.current_video_index = -1
        self.videos_done = 0
        self.progress = 0
        self.progress_bar["value"] = 0
        self.start_program()

def main():
    root = tk.Tk()
    app = EmotionalRecognitionApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

