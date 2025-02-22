from typing import Optional

import mido
from scipy.io import wavfile
import numpy as np
import math
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import sounddevice


def st_to_f(st: float) -> float:
    return 8.18 * pow(2, st / 12)


def f_to_st(f: float) -> float:
    return math.log2(f / 8.18) * 12


def db_to_a(db: float) -> float:
    return pow(10, db / 20)


def a_to_db(a: float) -> float:
    return 20 * math.log10(a)


def compress_audio(audio, factor=0.85):
    return np.sign(audio) * pow(np.abs(audio), factor)


def make_partial(time: np.ndarray, amplitude: float, frequency: float,
                 vib_f: float = 0, vib_st: float = 0) -> np.ndarray:
    if vib_st != 0:
        og_st = f_to_st(frequency)
        vib_a = st_to_f(og_st + vib_st) - frequency
        vib = vib_a * np.sin(2 * np.pi * vib_f * time)
        return amplitude * np.sin(2 * np.pi * frequency * time + vib)
    return amplitude * np.sin(2 * np.pi * frequency * time)


class Filter:
    def __init__(self, formant_f: float, bw_or_q: float, sample_len: float, is_bw=False):
        if is_bw:
            q = formant_f / bw_or_q
        else:
            q = bw_or_q
        b = 2 * np.pi * formant_f
        b0 = b * math.sqrt(1 + 1 / (4 * pow(q, 2)))
        a = b0 / (2 * q)
        self.a1 = -2 * math.exp(-a * sample_len) * np.cos(b * sample_len)
        self.a2 = math.exp(-2 * a * sample_len)
        self.g = 1 + self.a1 + self.a2

    def apply_filter(self, source: np.ndarray) -> np.ndarray:
        n1 = 0
        n2 = 0
        for i in range(len(source)):
            source[i] = self.g * source[i] - self.a1 * n1 - self.a2 * n2
            n2 = n1
            n1 = source[i]
        return source


class SourceGenerator:
    def __init__(self, partials: int, sample_rate: int):
        self.partials = partials
        self.sample_rate = sample_rate
        self.sources = {}

    def gen(self, st: float, duration: float, dynamic: float, vib_f: float = 0, vib_st: float = 0) -> np.ndarray:
        if (st, dynamic) in self.sources:
            s = self.sources[(st, dynamic)]
            samples = int(duration * self.sample_rate)
            if len(s) >= samples:
                return s[:samples]
        db_slope = a_to_db(dynamic)
        f0 = st_to_f(st)
        base_octave = math.log2(f0)
        time = np.linspace(0, duration, int(self.sample_rate * duration))
        source = np.zeros_like(time)

        for i in range(self.partials):
            if i * f0 > self.sample_rate / 2:
                break
            fi = f0 * (i + 1)
            ai = db_to_a(db_slope * (math.log2(fi) - base_octave))
            source += make_partial(time, ai, fi, vib_f, vib_st)

        self.sources[(duration, db_slope, vib_f, vib_st)] = source
        return source


class Vowel:
    def __init__(self, sg: SourceGenerator, formants: list[float], q: float, dynamic: float = 1):
        self.sg = sg
        self.filters = [Filter(formant, q, 1 / sg.sample_rate) for formant in formants]
        self.sings = {}
        self.dynamic = dynamic

    def sing(self, st: float, duration: float, dynamic: float) -> np.ndarray:
        if (st, dynamic) in self.sings:
            s = self.sings[(st, dynamic)]
            samples = int(duration * self.sg.sample_rate)
            if len(s) >= samples:
                return s[:samples]

        sound = self.sg.gen(st, duration, dynamic * self.dynamic)

        for filter_i in self.filters:
            sound = filter_i.apply_filter(sound)

        self.sings[(st, dynamic)] = sound
        return sound


class Song:
    def __init__(self, filename: str, sample_rate: int, volume: float = 1, st_offset: int = 0, info_track: int = 0):
        self.song = None
        self.rate = sample_rate
        self.volume = volume
        self.st_offset = st_offset

        self.midi = mido.MidiFile(filename)

        tpb = self.midi.ticks_per_beat
        tr = self.midi.tracks[info_track]
        rate = 500000
        for msg in tr:
            try:
                if msg.type == "set_tempo":
                    rate = msg.tempo
                    break
            except:
                continue
        self.tick_length = (rate / 1000000) / tpb

        total_ticks = 0
        for track in self.midi.tracks:
            ticks = 0
            for msg in track:
                ticks += msg.time
            if ticks > total_ticks:
                total_ticks = ticks

        self.song_length = total_ticks * self.tick_length

        self.vowels: list[Optional[Vowel]] = [None] * len(self.midi.tracks)

    def assign_vowel(self, track: int, vowel: Vowel):
        self.vowels[track] = vowel


    def generate(self):
        self.song = np.zeros(int(self.rate * self.song_length))

        for vowel, track in zip(self.vowels, self.midi.tracks):
            tick = 0
            notes_on = {}

            if vowel is not None:
                for msg in track:
                    tick += msg.time
                    fake_on = False
                    if msg.type == "note_on":
                        if msg.velocity == 0:
                            fake_on = True
                        else:
                            notes_on[msg.note] = (tick, msg.velocity)
                    if fake_on or (msg.type == "note_off" and msg.note in notes_on):
                        try:
                            s_tick, vel = notes_on.pop(msg.note)
                        except:
                            continue
                        start_ind = int(s_tick * self.tick_length * self.rate)
                        sound = vowel.sing(msg.note + self.st_offset, (tick - s_tick) * self.tick_length, vel / 128)
                        self.song[start_ind:start_ind + len(sound)] += sound

        self.song = compress_audio(self.song)
        self.song = self.song * self.volume / np.max(np.abs(self.song))

    def play(self):
        if self.song is None:
            self.generate()
        print("Playing!")
        sounddevice.play(self.song, self.rate)
        sounddevice.wait()

    def save(self, filename):
        if self.song is None:
            self.generate()
        wavfile.write(filename, self.rate, (self.song * 32767).astype(np.int16))


if __name__ == "__main__":
    sample_rate = 44100
    partials = 30
    volume = 0.1

    sg = SourceGenerator(partials, sample_rate)

    a = Vowel(sg, [680, 1120, 2760, 3360, 4200], 10)
    u = Vowel(sg, [240, 800, 2480, 3000, 5400], 10)

    asing = a.sing(65, 5, 1)

    song = Song("midis/nyan cat good.mid", sample_rate, volume)
    song.assign_vowel(1, a)
    song.assign_vowel(2, u)

    song.save("NyanCat.wav")
    song.play()