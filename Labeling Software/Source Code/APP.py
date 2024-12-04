import sys
import os
import csv
import random
import pandas as pd
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QUrl, Qt, QTimer, QRegExp
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QFileDialog, QGridLayout, QGroupBox, QDialog, QMessageBox, QLineEdit, QHBoxLayout
from PyQt5.QtGui import QRegExpValidator
from pathlib import Path
from functools import partial


class NewUserDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Neuen Benutzer erstellen")
        self.setGeometry(100, 100, 500, 250)

        self.layout = QVBoxLayout(self)

        self.instructions_label = QLabel("Bitte gebe nun deinen gewünschten Nutzernamen ein, welcher nur aus Buchstaben bestehen darf. Schreibe Ihn Dir unbedingt auf.", self)
        self.instructions_label.setWordWrap(True)
        self.layout.addWidget(self.instructions_label)

        self.username_input = QLineEdit(self)
        regex = QRegExp("[a-zA-Z]+")
        validator = QRegExpValidator(regex)
        self.username_input.setValidator(validator)
        self.layout.addWidget(self.username_input)

        self.back_button = QPushButton("Zurück", self)
        self.back_button.clicked.connect(self.reject)
        self.layout.addWidget(self.back_button)

        self.done_button = QPushButton("Fertig", self)
        self.done_button.clicked.connect(self.on_done_click)
        self.layout.addWidget(self.done_button)

        self.warning_label = QLabel("Der eingegebene Benutzername existiert bereits. Bitte geben Sie einen anderen ein.", self)
        self.warning_label.setWordWrap(True)
        self.warning_label.hide()
        self.layout.addWidget(self.warning_label)

    def on_done_click(self):
        username = self.username_input.text().lower()
        if os.path.exists(username):
            self.warning_label.show()
        else:
            self.create_user_folder(username)
            self.main_app.start_program(username)
            self.accept()

    def create_user_folder(self, username):
        if not os.path.exists(username):
            os.makedirs(username)

        clip_filenames = os.listdir("Clips")
        random.shuffle(clip_filenames)

        with open(f"{username}/clips.csv", "w", newline="") as f:
            writer = csv.writer(f)
            for filename in clip_filenames:
                writer.writerow([filename, "False", "None", "None", "None"])

        self.instructions_label.setText("Warte...")


class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Anmelden oder Neu")
        self.setGeometry(100, 100, 500, 250)

        self.layout = QVBoxLayout(self)

        self.login_button = QPushButton("Anmelden", self)
        self.login_button.clicked.connect(self.on_login_click)
        self.layout.addWidget(self.login_button)

        self.new_button = QPushButton("Neu", self)
        self.new_button.clicked.connect(self.on_new_click)
        self.layout.addWidget(self.new_button)

        self.username_input = QLineEdit(self)
        self.username_input.hide()
        self.layout.addWidget(self.username_input)

        self.done_button = QPushButton("Fertig", self)
        self.done_button.clicked.connect(self.on_done_click)
        self.done_button.hide()
        self.layout.addWidget(self.done_button)

        self.warning_label = QLabel("Der eingegebene Benutzername existiert nicht. Bitte versuche es erneut.", self)
        self.warning_label.setWordWrap(True)
        self.warning_label.hide()
        self.layout.addWidget(self.warning_label)

    def on_done_click(self):
        username = self.username_input.text().lower()
        if os.path.exists(username):
            self.main_app = EmotionalRecognitionApp()
            self.main_app.start_program(username)
            self.main_app.show()
            self.accept()
        else:
            self.warning_label.show()


    def on_login_click(self):
        self.new_button.hide()
        self.login_button.hide()
        if self.username_input.isHidden():
            self.username_input.show()
            self.done_button.show()
            self.layout.addWidget(QLabel("Bitte gebe hier deinen Benutzernamen ein", self))
        else:
            self.on_done_click()


    def on_new_click(self):
        self.main_app = EmotionalRecognitionApp()
        new_user_dialog = NewUserDialog(self)
        new_user_dialog.main_app = self.main_app
        if new_user_dialog.exec() == QDialog.Accepted:
            self.main_app.show()
            self.accept()




class EmotionalRecognitionApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.username = None

        self.setWindowTitle("Emotional Recognition Testing via video")
        self.setGeometry(100, 100, 1280, 720)

        self.video_list = []  # List of video file paths
        self.answers = []  # List to store answers
        self.correct_answers = {}
        
        self.current_video = None
        self.current_video_index = -1
        self.total_videos = 720
        self.videos_done = 0
        self.autosave_count = 0

        self.selected_button1 = None
        self.selected_button2 = None
        self.selected_button3 = None

        self.selected_emotion1 = None
        self.selected_emotion2 = None
        self.selected_emotion3 = None

        self.init_ui()

    def enable_next_button(self):
        self.next_button.setEnabled(True)


    def init_ui(self):

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.video_widget = QVideoWidget(self)
        self.layout.addWidget(self.video_widget, alignment=Qt.AlignCenter)  # Add alignment option to center the video widget
        self.video_widget.setFixedSize(640, 480)

        self.media_player = QMediaPlayer(self, QMediaPlayer.VideoSurface)
        self.media_player.setVideoOutput(self.video_widget)
        self.media_player.setMuted(True)
        self.media_player.stateChanged.connect(self.media_state_changed)

        # Create group box 1 for dominant emotion
        self.group_box1 = QGroupBox("Dominante Emotion", self)
        grid_layout1 = QGridLayout()
        self.group_box1.setLayout(grid_layout1)

        # Create group box 2 for co-dominant emotion
        self.group_box2 = QGroupBox("Co-Dominante Emotion", self)
        grid_layout2 = QGridLayout()
        self.group_box2.setLayout(grid_layout2)

        # Create group box 3 for secondary emotions
        self.group_box3 = QGroupBox("Sekundär Emotionen", self)
        grid_layout3 = QGridLayout()
        self.group_box3.setLayout(grid_layout3)

        # Create lists for emotion buttons for each group box
        self.emotion_buttons1 = []
        self.emotion_buttons2 = []
        self.emotion_buttons3 = []
        
        # Create separate variables for the selected button in each group box
        self.selected_button1 = None
        self.selected_button2 = None
        self.selected_button3 = None

        emotions = [
            ("Angst"),
            ("Freude"),
            ("Trauer"),
            ("Wut"),
            ("Ekel"),
            ("Neutral")
        ]
        coemotions=[
            ("Angst"),
            ("Freude"),
            ("Trauer"),
            ("Wut"),
            ("Ekel"),
            ("None")
        ]
        secondaryemotions=[
            ("Scham"),
            ("Schuld"),
            ("Frustration"),
            ("Verwirrung"),
            ("Enttaeuschung"),
            ("None")
        ]

        for index, (emotion) in enumerate(emotions):
            button1 = QPushButton(emotion, self)
            button1.setStyleSheet(f"color: black")
            button1.clicked.connect(partial(self.on_emotion_click1, button1))
            button1.setEnabled(False)

            row, col = divmod(index, 3)  # Aufteilung in 2 Zeilen und 3 Spalten
            grid_layout1.addWidget(button1, row, col)
            self.emotion_buttons1.append(button1)

        for index, (emotion) in enumerate(coemotions):
            button2 = QPushButton(emotion, self)
            button2.setStyleSheet(f"color: black")
            button2.clicked.connect(partial(self.on_emotion_click2, button2))  
            button2.setEnabled(False)
            row, col = divmod(index, 3)
            grid_layout2.addWidget(button2, row, col)
            self.emotion_buttons2.append(button2)

        for index, (emotion) in enumerate(secondaryemotions):
            button3 = QPushButton(emotion, self)
            button3.setStyleSheet(f"color: black")
            button3.clicked.connect(partial(self.on_emotion_click3, button3))
            button3.setEnabled(False)

            row, col = divmod(index, 3)  # Aufteilung in 2 Zeilen und 3 Spalten
            grid_layout3.addWidget(button3, row, col)
            self.emotion_buttons3.append(button3)

        hbox_layout = QHBoxLayout()
        hbox_layout.addWidget(self.group_box1)
        hbox_layout.addWidget(self.group_box2)
        hbox_layout.addWidget(self.group_box3)
        self.layout.addLayout(hbox_layout)

        hbox_layout2 = QHBoxLayout()
        self.repeat_button = QPushButton("Wiederholen", self)
        self.repeat_button.setStyleSheet("color: black")
        self.repeat_button.clicked.connect(self.on_repeat_click) # Verbindung zur neuen on_repeat_click Funktion
        hbox_layout2.addWidget(self.repeat_button)

        self.next_button = QPushButton("Weiter", self)

        self.next_button.setStyleSheet("color: black")
        self.next_button.setEnabled(False)
        self.next_button.clicked.connect(self.play_next_video)
        hbox_layout2.addWidget(self.next_button)

        self.layout.addLayout(hbox_layout2)

        self.export_button = QPushButton("Finish!", self)
        self.export_button.setStyleSheet("color: black")
        self.export_button.clicked.connect(self.on_export_click)
        self.layout.addWidget(self.export_button)
        self.export_button.hide()

    def load_video_list(self, username):
        script_folder = Path(sys.argv[0]).parent
        video_folder = 'Clips'
        video_folder_path = os.path.join(script_folder, video_folder)
        csv_file_path = os.path.join(script_folder, username, 'clips.csv')
        
        try:
            with open(csv_file_path, 'r') as f:
                reader = csv.reader(f)
                for row in reader:
                    if row[1] == 'False':
                        file_path = os.path.join(video_folder_path, row[0])
                        self.video_list.append(file_path)
        except FileNotFoundError:
            print(f"File {csv_file_path} not found.")
        except PermissionError:
            print(f"No permission to read the file {csv_file_path}.")

    def on_repeat_click(self):
        """Diese Funktion spielt das aktuelle Video erneut ab."""
        self.media_player.setPosition(0) # Setzt die Position des Media Players auf den Anfang des Videos
        self.media_player.play() # Spielt das Video erneut ab

    def start_program(self, username):
        self.username = username
        self.load_video_list(username)
        self.play_next_video()

    def play_next_video(self):
        for button in self.emotion_buttons1:
            button.setStyleSheet(None)
            button.setStyleSheet(f"background-color: {button.palette().button().color().name()}; color: black")
        for button in self.emotion_buttons2:
            button.setStyleSheet(None)
            button.setStyleSheet(f"background-color: {button.palette().button().color().name()}; color: black")
        for button in self.emotion_buttons3:
            button.setStyleSheet(None)
            button.setStyleSheet(f"background-color: {button.palette().button().color().name()}; color: black")

        # Write selected emotions to CSV
        if self.selected_emotion1 is not None or self.selected_emotion3 is not None:
            script_folder = Path(sys.argv[0]).parent
            csv_file_path = os.path.join(script_folder, self.username, 'clips.csv')

            # Temporäre Liste für die aktualisierten Zeilen
            updated_rows = []
            
            with open(csv_file_path, 'r', newline='') as csvfile:
                reader = csv.reader(csvfile)
                # Durchlaufen der Zeilen der CSV-Datei
                for row in reader:
                    # Überprüfen, ob die aktuelle Zeile das aktuelle Video enthält
                    if row[0] == os.path.basename(self.current_video):
                        # Aktualisieren der Werte in den Spalten 2, 3 und 4
                        row[1] = 'True'
                        row[2] = self.selected_emotion1 if self.selected_emotion1 is not None else 'None'
                        row[3] = self.selected_emotion2 if self.selected_emotion2 is not None else 'None'
                        row[4] = self.selected_emotion3 if self.selected_emotion3 is not None else 'None'

                    # Hinzufügen der aktualisierten Zeile zur Liste
                    updated_rows.append(row)

            # Überschreiben der CSV-Datei mit den aktualisierten Daten
            with open(csv_file_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(updated_rows)

        self.selected_emotion1 = None
        self.selected_emotion2 = None
        self.selected_emotion3 = None
        self.next_button.setEnabled(False)

        self.current_video_index += 1
        if self.current_video_index < len(self.video_list):
            self.current_video = self.video_list[self.current_video_index]
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(os.path.abspath(self.current_video))))
            self.media_player.play()
        else:
            self.show_export_button()

    def on_emotion_click1(self, emotion):
        if self.selected_button1:
            self.selected_button1.setStyleSheet(f"background-color: {self.selected_button_color}; color: black")
        self.selected_button1 = self.sender()
        self.selected_button_color = self.selected_button1.palette().button().color().name()
        self.selected_button1.setStyleSheet(f"background-color: #A9A9A9; color: black")

        self.selected_emotion1 = emotion.text()
        self.enable_next_button()



    def on_emotion_click2(self, emotion):
        if self.selected_button2:
            self.selected_button2.setStyleSheet(f"background-color: {self.selected_button_color}; color: black")
        self.selected_button2 = self.sender()
        self.selected_button_color = self.selected_button2.palette().button().color().name()
        self.selected_button2.setStyleSheet(f"background-color: #A9A9A9; color: black")
        self.selected_emotion2 = emotion.text()
        # self.enable_next_button()



    def on_emotion_click3(self, emotion):
        if self.selected_button3:
            self.selected_button3.setStyleSheet(f"background-color: {self.selected_button_color}; color: black")
        self.selected_button3 = self.sender()
        self.selected_button_color = self.selected_button3.palette().button().color().name()
        self.selected_button3.setStyleSheet(f"background-color: #A9A9A9; color: black")
        self.selected_emotion3 = emotion.text()
        self.enable_next_button()


    def on_back_click(self):
        if self.videos_done > 0:
            self.videos_done -= 1
            self.autosave_count -= 1
            self.current_video_index -= 2
            self.answers.pop()
            self.play_next_video()

    def media_state_changed(self, state):
        QTimer.singleShot(1000, self.enable_emotion_buttons)

    def enable_emotion_buttons(self):
        for button in self.emotion_buttons1:
            button.setEnabled(True) 
        for button in self.emotion_buttons2:
            button.setEnabled(True) 
        for button in self.emotion_buttons3:
            button.setEnabled(True)      

    def on_export_click(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getSaveFileName(self, "Save results", "", "CSV Files (*.csv);;All Files (*)",
                                                options=options)
        if file_name:
            self.export_results(file_name)
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("Die Ergebnisse wurden erfolgreich exportiert. Sie können das Programm jetzt beenden.")
            msg.setWindowTitle("Information")
            msg.exec_()


    def export_results(self, file_name):
        data = {"Video": self.video_list[:len(self.answers)], "Answer": self.answers}
        df = pd.DataFrame(data)
        df.to_csv(file_name, index=False)

    def save_progress(self):
        data = {"Video": self.video_list[:len(self.answers)], "Answer": self.answers}
        df = pd.DataFrame(data)
        df.to_csv("Video-test-progress"+str(self.autosave_count)+".csv", index=False)

    def show_export_button(self):
        self.export_button.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    login_dialog = LoginDialog()
    if login_dialog.exec() == QDialog.Accepted:
        sys.exit(app.exec())


