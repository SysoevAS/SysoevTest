import os
import whisper

path = "pipa/kilka2.wav"

if os.path.exists(path):
    print(f"Файл или директория по пути {path} существует.")
else:
    print(f"Файл или директория по пути {path} не существует.")

model = whisper.load_model("base")
result = model.transcribe("pipa/kilka2.wav")
print(result["text"])