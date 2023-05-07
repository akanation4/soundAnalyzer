import wave
import os
import pyaudio
import questionary
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from pydub import AudioSegment, effects


CHUNK = 1024 # バッファサイズ
FORMAT = pyaudio.paInt16 # 量子化ビット数
CHANNELS = 1
RATE = 44100 # サンプリング周波数
RECORD_SECONDS = 5
RECORD_WAIT = 3
WAVE_PATH = './wav/'
STARTUP_SOUND = 'startup'
# ORIGINAL_FILE = 'original'
# RECORDED_FILE = 'recorded'
N_SAMPLES = 512
PNG_PATH = './png/'
SOUND_EXTENSION = '.wav'
IMAGE_EXTENSION = '.png'

target = 'output'

def main():
    # matplotlibの設定
    mpl.use('Agg')

    # 起動音の再生(サウンドデバイスが正常に接続されているか確認)
    print('SOUD ANALYZER')
    play(STARTUP_SOUND)

    while True:
        mode = questionary.select('Choose a mode?', choices=['Record', 'Play', 'Spectrogram', 'Quit']).ask()

        match mode:
            case 'Record':
                print(f'Start recording for {RECORD_SECONDS} seconds.')
                file_name = questionary.text('Enter a file name (without extension):').ask()
                change_target(file_name)
                print('Press Enter to start recording.')
                input()
                print('Recording...')
                record(target)
                print('Done')

            case 'Play':
                file_name = questionary.text('Enter a file name (without extension):').ask()
                change_target(file_name)
                if is_exist_file(WAVE_PATH + target + SOUND_EXTENSION):
                    print('Playing...')
                    play(target)
                    print('Done')
                else:
                    print('Not found')

            case 'Spectrogram':
                file_name = questionary.text('Enter a file name (without extension):').ask()
                change_target(file_name)
                if is_exist_file(WAVE_PATH + target + SOUND_EXTENSION):
                    draw_spectrogram(target)
                    print('Saved images')
                else:
                    print('Not found')

            case 'Quit':
                print('Bye')
                break

def play(file_name):
    wf = wave.open(WAVE_PATH + file_name + SOUND_EXTENSION, 'rb')
    # ストリームの開始
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    # チャンク単位でストリームに出力し音声を再生
    data = wf.readframes(CHUNK)
    while len(data) > 0:
        stream.write(data)
        data = wf.readframes(CHUNK)

    # ストリームの終了
    stream.stop_stream()
    stream.close()
    p.terminate()

def record(file_name):
    # ストリームの開始
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    # チャンク単位でストリームから音声を録音
    frames = []
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    # ストリームの終了
    stream.stop_stream()
    stream.close()
    p.terminate()

    # 録音した音声をファイルに保存
    wf = wave.open(WAVE_PATH + file_name + SOUND_EXTENSION, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    # 正規化
    sound = AudioSegment.from_file(WAVE_PATH + file_name + SOUND_EXTENSION, SOUND_EXTENSION[1:])
    normalized_sound = effects.normalize(sound)
    normalized_sound.export(WAVE_PATH + file_name + SOUND_EXTENSION, format=SOUND_EXTENSION[1:])

def draw_spectrogram(file_name):
    # 波形データの取得
    wf = wave.open(WAVE_PATH + file_name + SOUND_EXTENSION, 'rb')
    data = wf.readframes(wf.getnframes())
    data = np.frombuffer(data, dtype='int16')
    length = float(wf.getnframes()) / wf.getframerate()

    hammingWindow = np.hamming(N_SAMPLES)

    # スペクトログラムの描画
    pxx, freqs, bins, im = plt.specgram(data, NFFT=N_SAMPLES, Fs=wf.getframerate(), window=hammingWindow, noverlap=0)
    axis = [0, length, 0, wf.getframerate() / 2]
    Xlabel = 'Time [sec]'
    Ylabel = 'Frequency [Hz]'
    plt.ylim(50, 2000)
    plt.savefig(PNG_PATH + file_name + IMAGE_EXTENSION)

def change_target(file_name):
    global target
    if file_name != '':
        target = file_name

def is_exist_file(file_name):
    return os.path.exists(file_name)

# def countdown(num_of_seconds):
#     while num_of_seconds > 0:
#         print(num_of_seconds)
#         time.sleep(1)
#         num_of_seconds -= 1

if __name__ == '__main__':
    main()
