import os
import threading
from flask import Flask, render_template, request, jsonify
import pyaudio
import wave
import speech_recognition as sr
from textblob import TextBlob  # Добавлен импорт

app = Flask(__name__)
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
RECORDING = False

last_index = 0
frames = []
recording_thread = None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/start_recording', methods=['POST'])
def start_recording():
    global RECORDING, frames, recording_thread
    if RECORDING:
        return jsonify({"message": "Already recording"})

    RECORDING = True
    frames = []

    def record():
        local_audio = pyaudio.PyAudio()
        stream = local_audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
        while RECORDING:
            frames.append(stream.read(CHUNK, exception_on_overflow=False))
        stream.stop_stream()
        stream.close()
        local_audio.terminate()

    recording_thread = threading.Thread(target=record)
    recording_thread.start()

    return jsonify({"message": "Recording started"})


@app.route('/stop_recording', methods=['POST'])
def stop_recording():
    global RECORDING, frames, last_index, recording_thread
    RECORDING = False
    if recording_thread:
        recording_thread.join()

    if not os.path.exists('pipa'):
        os.makedirs('pipa')

    last_index += 1
    filename = f"pipa/kilka{last_index}.wav"

    local_audio = pyaudio.PyAudio()
    with wave.open(filename, 'wb') as waveFile:
        waveFile.setnchannels(CHANNELS)
        waveFile.setsampwidth(local_audio.get_sample_size(FORMAT))
        waveFile.setframerate(RATE)
        waveFile.writeframes(b''.join(frames))
    local_audio.terminate()

    return jsonify({"message": f"Recording stopped and saved as {filename}"})


def transcribe_audio(audio_file_path):
    try:
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_file_path) as source:
            audio = recognizer.record(source)
        transcription = recognizer.recognize_google(audio)

        # Анализ тональности с использованием TextBlob
        blob = TextBlob(transcription)
        sentiment_score = blob.sentiment.polarity

        # Определение тональности
        if sentiment_score > 0:
            sentiment = "Positive"
        elif sentiment_score < 0:
            sentiment = "Negative"
        else:
            sentiment = "Neutral"

        return transcription, sentiment

    except Exception as e:
        return f"An error occurred: {str(e)}", None


@app.route('/transcription')
def transcription_page():
    files = os.listdir('pipa')
    return render_template('transcription.html', files=files)


@app.route('/transcribe', methods=['POST'])
def transcribe():
    audio_file = request.form.get('audio_file')
    audio_file_path = os.path.join('pipa', audio_file)
    transcription, sentiment = transcribe_audio(audio_file_path)
    files = os.listdir('pipa')
    return render_template('transcription.html', transcription=transcription, sentiment=sentiment, files=files)


if __name__ == '__main__':
    app.run(debug=True, port=5001)
