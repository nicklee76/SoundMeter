import pyaudio
import time
from math import log10
import audioop
from statistics import *
import logging
from logging.handlers import RotatingFileHandler


# Global variable declarations (not the best way to code.  Temporary)
WIDTH = 2
RMS = 1


def callback(in_data, frame_count, time_info, status):
    global RMS
    RMS = audioop.rms(in_data, WIDTH) / 32767
    if RMS == 0:  # to prevent log10(0) issue
        RMS = 1
    return in_data, pyaudio.paContinue


def cleanup(stream, py_audio):
    stream.stop_stream()
    stream.close()

    py_audio.terminate()
    print("Clean Up Done.")


def main():
    log_file = "audio_sampling.log"

    p = pyaudio.PyAudio()
    print(p.get_default_input_device_info())

    rate = int(p.get_default_input_device_info()['defaultSampleRate'])
    device = p.get_default_input_device_info()['index']

    min_sound_level = 90

    stream = p.open(format=p.get_format_from_width(WIDTH),
                    input_device_index=device,
                    channels=1,
                    rate=rate,
                    input=True,
                    output=False,
                    stream_callback=callback)

    stream.start_stream()

    try:
        sound_sample_list = list()

        while stream.is_active():
            for number in range(10):
                db = 20 * log10(RMS)
                sound_level = min_sound_level + int(db)

                sound_sample_list.append(sound_level)

                if db != 0:
                    print(f"\tRMS: {RMS} DB: {db} SoundLevel: {sound_level}")

                # sleep before the next sampling
                time.sleep(0.1)

            mean_sound_level = mean(sound_sample_list)
            print(f"SoundSampleList: {sound_sample_list}")
            print(f"AVG-SoundLevel: {mean_sound_level}")

            sound_sample_list.clear()   # reset the list

    except KeyboardInterrupt:   # exit when CTRL-c is pressed
        pass

    finally:
        cleanup(stream=stream, py_audio=p)


if __name__ == "__main__":
    main()
