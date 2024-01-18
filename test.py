import speech_recognition as sr

def transcribe_audio(audio_file_path):
    try:
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_file_path) as source:
            audio = recognizer.record(source)
        transcription = recognizer.recognize_google(audio)
        return transcription
    except Exception as e:
        return f"An error occurred: {str(e)}"

audio_file_path = 'pipa/kilka3.wav'
transcription = transcribe_audio(audio_file_path)
print("Transcription:", transcription)
