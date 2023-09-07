#!/usr/bin/env python3
import pyaudio
import time
from math import log10
import audioop
from statistics import *
import logging
import logging.handlers as handlers
import os


######################################################################
# Global variable declarations (not the best way to code.  Temporary)
#
WIDTH = 2
RMS = 1

# sound_sample_option
# 1 - sample every 1 second
# 2 - get the mean value of 10 samples and then sleep for 0.1 sec
SOUND_SAMPLE_OPTION = 1

######################################################################


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
    logging.info("cleanup() called and finished the cleanup")


def check_log_dir_file(log_file):
    current_dir = os.getcwd()
    log_dir_file = current_dir + '/logs/' + log_file

    # check if the log directory and log files already exist
    os.makedirs(os.path.dirname(log_dir_file), exist_ok=True)
    with open(log_dir_file, "w") as f:
        f.close()

    return log_dir_file


def main():
    log_dir_file = check_log_dir_file("audio_sampling.log")

    logger = logging.getLogger('sound_level.py')
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    log_handler = handlers.RotatingFileHandler(log_dir_file, maxBytes=5*1024*1024, backupCount=2)
    log_handler.setLevel(logging.INFO)
    log_handler.setFormatter(formatter)

    logger.addHandler(log_handler)

    p = pyaudio.PyAudio()
    print(p.get_default_input_device_info())
    logger.info(p.get_default_input_device_info())

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
        print(f"Sound Sample Option - {SOUND_SAMPLE_OPTION}")
        logger.info(f"sound sample option - {SOUND_SAMPLE_OPTION}")

        while stream.is_active():
            if SOUND_SAMPLE_OPTION == 1:
                db = 20 * log10(RMS)
                sound_level = min_sound_level + int(db)

                print(f"\tRMS={RMS}, DB={db}, SoundLevel={sound_level}")
                logger.info(f"RMS={RMS}, DB={db}, SoundLevel={sound_level}")

                time.sleep(1)

            elif SOUND_SAMPLE_OPTION == 2:
                sound_sample_list = list()

                for number in range(10):
                    db = 20 * log10(RMS)
                    sound_level = min_sound_level + int(db)

                    sound_sample_list.append(sound_level)

                    if db != 0:
                        print(f"\tRMS: {RMS} DB: {db} SoundLevel: {sound_level}")
                        logger.info(f"RMS: {RMS} DB: {db} SoundLevel: {sound_level}")

                    # sleep before the next sampling
                    time.sleep(0.1)

                mean_sound_level = mean(sound_sample_list)
                print(f"SoundSampleList: {sound_sample_list}")
                logger.debug(f"SoundSampleList: {sound_sample_list}")

                print(f"AVG-SoundLevel: {mean_sound_level}")
                logger.info(f"AVG-SoundLevel: {mean_sound_level}")

                sound_sample_list.clear()  # reset the list

            else:
                print("Wrong sound sample option")
                logger.critical(f"Wrong sound sample option ({SOUND_SAMPLE_OPTION}) chosen.")

                break

    except KeyboardInterrupt:  # exit when CTRL-c is pressed
        pass

    finally:
        cleanup(stream=stream, py_audio=p)


if __name__ == "__main__":
    main()
