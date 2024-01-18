import whisper


def transcribe_audio(audio_file_path):
    try:
        model = whisper.load_model("base")
        result = model.transcribe(audio_file_path)
        return result['text']
    except Exception as e:
        return f"An error occurred: {str(e)}"


audio_file_path = 'uploads/recorded1.wav'
transcription = transcribe_audio(audio_file_path)
print("Transcription:", transcription)
