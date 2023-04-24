import pyaudio
import questionary
import wave
import os

CHUNK = 1024 # バッファサイズ
FORMAT = pyaudio.paInt16 # 量子化ビット数
CHANNELS = 1
RATE = 44100 # サンプリング周波数
RECORD_SECONDS = 3
RECORD_WAIT = 3
WAVE_PATH = "./wav/"
STARTUP_SOUND = "startup.wav"
OUTPUT_FILE = "output.wav"

def main():
    print("SOUD ANALYZER")
    play(STARTUP_SOUND)

    while True:
        mode = questionary.select("Choose a mode?", choices=["Record", "Play", "Compare", "Quit"]).ask()

        match mode:
            case "Record":
                print("Start a new recording")
                record_with_message()

            case "Play":
                if isExistFile(WAVE_PATH + OUTPUT_FILE):
                    print("Playing...")
                    play(OUTPUT_FILE)
                    print("Done")

            case "Compare":
                print("Start recording for comparison")
                record_with_message()


            case "Quit":
                print("Bye")
                break

def record_with_message():
        print("Recording...")
        record()
        print("Done")

def play(file_name):
    wf = wave.open(WAVE_PATH + file_name, 'rb')
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    data = wf.readframes(CHUNK)
    while len(data) > 0:
        stream.write(data)
        data = wf.readframes(CHUNK)

    stream.stop_stream()
    stream.close()
    p.terminate()

def record():
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    frames = []
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(WAVE_PATH + OUTPUT_FILE, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

def isExistFile(file_name):
    return os.path.exists(file_name)

# def countdown(num_of_seconds):
#     while num_of_seconds > 0:
#         print(num_of_seconds)
#         time.sleep(1)
#         num_of_seconds -= 1

if __name__ == "__main__":
    main()
