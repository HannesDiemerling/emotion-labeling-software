import os
import random
import shutil

folder_path = "your/path/to/clips"

used_files=[]

for file_name in os.listdir(folder_path):
    if file_name.endswith('.mp4'):
        used_files.append(file_name)

random.seed(7415963)
random.shuffle(used_files)

with open("usedClips.txt", "w") as file:
    for string in used_files[:50000]:
        file.write(string + "\n")

with open("usedClips.txt", 'r') as f:
        lines = [line.strip() for line in f]

# Der Pfad zum Quellordner
source_dir = "your/path/to/source"

# Der Pfad zum Zielordner
target_dir = "your/path/to/destination"

for filename in lines:
    full_path = os.path.join(source_dir, filename)
    
    if os.path.exists(full_path):
        shutil.copy(full_path, target_dir)
        print(f"Die Datei {filename} wurde erfolgreich kopiert.")
    else:
        print(f"Die Datei {filename} existiert nicht im Quellordner.")