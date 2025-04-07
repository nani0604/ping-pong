import os
import wave
import struct
import math

# make sure we have a sounds directory
os.makedirs('sounds', exist_ok=True)

def make_sound(path, freq=440.0, duration=0.1, volume=0.5, sample_rate=44100):
    """
    Generate a sine‑wave .wav at given freq (Hz), duration (s), volume (0.0–1.0).
    """
    n_samples = int(sample_rate * duration)
    wav = wave.open(path, 'w')
    wav.setparams((1, 2, sample_rate, n_samples, 'NONE', 'not compressed'))
    for i in range(n_samples):
        t = i / sample_rate
        # simple sine wave
        sample = volume * math.sin(2 * math.pi * freq * t)
        # pack as signed 16‑bit little endian
        wav.writeframes(struct.pack('<h', int(sample * 32767)))
    wav.close()

# define your four effects with different pitches/durations
effects = {
    'hit.wav':      {'freq': 400.0, 'duration': 0.05, 'volume': 0.8},
    'score.wav':    {'freq': 600.0, 'duration': 0.2,  'volume': 0.6},
    'powerup.wav':  {'freq': 800.0, 'duration': 0.15, 'volume': 0.7},
    'wall.wav':     {'freq': 300.0, 'duration': 0.05, 'volume': 0.5},
}

for filename, params in effects.items():
    path = os.path.join('sounds', filename)
    print(f"Generating {path} …")
    make_sound(path, **params)


