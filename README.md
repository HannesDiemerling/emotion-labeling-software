# Emotional Recognition Training, Testing, and Labeling Software

This repository contains software designed to train and test emotional recognition skills using video and/or audio clips, as well as software for labeling new videos. It was developed as part of a research study to evaluate participants' ability to recognize emotions. The repository includes:

1. **Training and Testing Software**: Available for both macOS and Windows, with separate programs for:
   - Video-only
   - Audio-only
   - Combined video and audio

2. **Labeling Software**: Available for Windows only.

---

## How to Use the Training and Testing Software

1. **Download the Program**:  
   Choose the appropriate `.exe` (Windows) or `.app` (macOS) file from the `Train and Test Software` folder and save it locally.

2. **Prepare the Clips Folder**:  
   Depending on the chosen program, create a new folder in the same location as the program:
   - For the Training Software, name the folder `Trainingsset`.
   - For the Testing Software, name the folder `Testset`.

   Add video/audio clips to this folder. In our study, we used the [RAVDESS dataset](https://paperswithcode.com/dataset/ravdess).

3. **Run the Program**:  
   Launch the downloaded program and follow the on-screen instructions to complete the training or testing process. The results will be saved in the same location as the program.

---

## How to Use the Labeling Software

1. **Download the Program**:  
   Choose the `.exe` file for Windows from the repository's releases.

2. **Prepare the Clips Folder**:  
   Create a folder named `Clips` in the same directory as the program. Add the video/audio clips you want to label into this folder. The program will randomly order them and display them to the labelers.

3. **Run the Program**:  
   Launch the program and follow the on-screen instructions:
   - **Login or Create a New User**: You can either log in with an existing username or create a new one. Each user will have their own folder to save progress and results.
   - **Label Emotions**: For each clip, you can label:
     - **Dominant Emotion**: The primary emotion expressed in the clip.
     - **Co-Dominant Emotion**: A secondary emotion, if applicable.
     - **Secondary Emotions**: Additional emotions that may be present.

4. **Save Results**:  
   Once all clips are labeled, you can export the results as a CSV file. The file will include the video name and the selected emotions for each category.

---

## Source Code

The source code for all programs is included in this repository for transparency and further development. Developers can modify or extend the functionality as needed, following the MIT License.