import sys
import os
import random
import pandas as pd
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QProgressBar, QFileDialog
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QUrl, Qt, QTimer
from PyQt5.QtGui import QFont
from pathlib import Path
from functools import partial

class EmotionalRecognitionApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Emotional Recognition Test via audio")
        self.setGeometry(100, 100, 1280, 720)

        self.video_list = []  # List of video file paths
        self.answers = []  # List to store answers
        self.correct_answers = {}
        
        self.load_video_list()

        self.current_video = None
        self.current_video_index = -1
        self.total_videos = 720
        self.videos_done = 0
        self.autosave_count = 0

        self.init_ui()

    def init_ui(self):
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.correct_answer_label = QLabel(self)
        self.correct_answer_label.setWordWrap(True)
        self.layout.addWidget(self.correct_answer_label)
        self.correct_answer_label.hide()

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, self.total_videos)
        self.layout.addWidget(self.progress_bar)

        self.description_label = QLabel("This program is designed to help test your emotional recognition "
                                        "skills by watching videos an hearing audios of people expressing different emotions. "
                                        "Click the 'Start' button to begin.", self)
        self.description_label.setWordWrap(True)
        self.layout.addWidget(self.description_label)

        self.start_button = QPushButton("Start", self)
        self.start_button.setStyleSheet("color: black")
        self.start_button.clicked.connect(self.start_program)
        self.layout.addWidget(self.start_button)

        
        self.audio_label = QLabel("This program is audio only, you will not see any video.", self)
        self.audio_label.setWordWrap(True)
        self.layout.addWidget(self.audio_label)
        self.audio_label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(2 * font.pointSize())
        self.audio_label.setFont(font)
        self.audio_label.hide()
        
        # only Audio version
        # self.video_widget = QVideoWidget(self)
        # self.layout.addWidget(self.video_widget)

        self.media_player = QMediaPlayer(self, QMediaPlayer.LowLatency)
        # only Audio version
        # self.media_player.setVideoOutput(self.video_widget)
        self.media_player.stateChanged.connect(self.media_state_changed)

        emotions = [
            ("Angst", "#FF5733"),
            ("Freude", "#FFFF66"),
            ("Trauer", "#4DA6FF"),
            ("Wut", "#B22222"),
            ("Ekel", "#3CB371"),
            ("Neutral", "#C0C0C0")
        ]

        self.emotion_buttons = []
        for emotion, color in emotions:
            button = QPushButton(emotion, self)
            button.setStyleSheet(f"background-color: {color}; color: black")
            button.clicked.connect(partial(self.on_emotion_click, emotion))
            button.setEnabled(False)
            self.layout.addWidget(button)
            self.emotion_buttons.append(button)

        self.back_button = QPushButton("Zurück", self)
        self.back_button.setStyleSheet("color: black")
        self.back_button.clicked.connect(self.on_back_click)
        self.layout.addWidget(self.back_button)

        self.export_button = QPushButton("Export", self)
        self.export_button.setStyleSheet("color: black")
        self.export_button.clicked.connect(self.on_export_click)
        self.layout.addWidget(self.export_button)
        self.export_button.hide()

    def load_video_list(self):
        script_folder = Path(sys.argv[0]).parent
        video_folder = 'Testset'
        video_folder_path = os.path.join(script_folder, video_folder)
        for root, _, files in os.walk(video_folder_path):
            for file in files:
                if file.lower().endswith(('.mp4', '.mkv', '.avi', '.flv', '.wmv', '.mov')):
                    self.video_list.append(os.path.join(root, file))

        random.shuffle(self.video_list)

    def start_program(self):
        self.start_button.hide()
        self.description_label.hide()
        self.play_next_video()
        self.audio_label.show()

    def play_next_video(self):
        self.current_video_index += 1
        if self.current_video_index < len(self.video_list):
            self.current_video = self.video_list[self.current_video_index]
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(os.path.abspath(self.current_video))))
            self.media_player.play()
        else:
            self.show_export_button()

    def on_emotion_click(self, emotion):
        self.answers.append(emotion)
        self.videos_done += 1
        self.progress_bar.setValue(self.videos_done)
        self.autosave_count += 1

        if self.autosave_count % 10 == 0:
            self.save_progress()

        for button in self.emotion_buttons:
            button.setEnabled(False)
        self.play_next_video()

    def on_back_click(self):
        if self.videos_done > 0:
            self.autosave_count -= 1
            self.videos_done -= 1
            self.progress_bar.setValue(self.videos_done)
            self.current_video_index -= 2
            self.answers.pop()
            self.play_next_video()

    def media_state_changed(self, state):
        QTimer.singleShot(1000, self.enable_emotion_buttons)

    def on_export_click(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getSaveFileName(self, "Save results", "", "CSV Files (*.csv);;All Files (*)",
                                                   options=options)
        if file_name:
            self.export_results(file_name)

    def export_results(self, file_name):
        data = {"Video": self.video_list[:len(self.answers)], "Answer": self.answers}
        df = pd.DataFrame(data)
        df.to_csv(file_name, index=False)

    def save_progress(self):
        data = {"Video": self.video_list[:len(self.answers)], "Answer": self.answers}
        df = pd.DataFrame(data)
        df.to_csv("Audio-test-progress"+str(self.autosave_count)+".csv", index=False)

    def enable_emotion_buttons(self):
        for button in self.emotion_buttons:
            button.setEnabled(True) 

    def show_export_button(self):
        self.export_button.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EmotionalRecognitionApp()
    window.show()
    sys.exit(app.exec_())
