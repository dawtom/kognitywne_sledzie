import random
import winsound

import numpy as np
import sounddevice
import time
import pygame

fs = 8000 # Hz
T = 0.8 # second, arbitrary length of tone
sleeptime = 0.2
def create_wave(frequency):
    t = np.arange(0, T, 1 / fs)
    x = 2 * np.sin(2 * np.pi * frequency * t)  # 0.5 is arbitrary to avoid clipping sound card DAC
    x = (x * 32768).astype(np.int16)  # scale to int16 for sound card
    return x
    # sounddevice.play(x, fs)  # releases GIL

def get_pygame_sound(x):
    pygame.mixer.pre_init(fs, size=-16, channels=1)
    pygame.mixer.init()
    sound = pygame.sndarray.make_sound(x)
    return sound
# play(440)

frequency = 220
while(True):
    if random.random() > 0.99:
        frequency *= 1.5
    wave = create_wave(frequency)
    snd = get_pygame_sound(wave)
    sounddevice.play(wave,fs)
    time.sleep(sleeptime)
    snd.play()
    time.sleep(sleeptime)
    # snd.play()
    # time.sleep(sleeptime)





# time.sleep(1)  # NOTE: Since sound playback is async, allow sound playback to finish before Python exits