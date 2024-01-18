from flask import Flask, jsonify, request
import pyaudio
import threading
import os
import wave

app = Flask(__name__)

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024

RECORDING = False
frames = []
recording_thread = None
last_index = 0

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

    if not os.path.exists('uploads'):
        os.makedirs('uploads')

    last_index += 1
    filename = f"uploads/recorded_{last_index}.wav"

    local_audio = pyaudio.PyAudio()
    with wave.open(filename, 'wb') as waveFile:
        waveFile.setnchannels(CHANNELS)
        waveFile.setsampwidth(local_audio.get_sample_size(FORMAT))
        waveFile.setframerate(RATE)
        waveFile.writeframes(b''.join(frames))
    local_audio.terminate()

    return jsonify({"message": f"Recording stopped and saved as {filename}"})

if __name__ == '__main__':
    app.run(debug=True, port=8080)
