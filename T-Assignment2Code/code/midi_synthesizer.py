import mido
from scipy.io import wavfile
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import sounddevice

AMT_PARTIALS = 15
SOUND_DURATION = 3


def locate_partials(mags, freqs):
    peaks = find_peaks(mags)
    peak_f = []
    peak_m = []
    for peak in peaks[0]:
        if freqs[peak] <= 15000:
            peak_f.append(freqs[peak])
            peak_m.append(mags[peak])

    peak_f = [x for _,x in sorted(zip(peak_m, peak_f))]  # sort by magnitude, https://stackoverflow.com/questions/6618515/sorting-list-according-to-corresponding-values-from-a-parallel-list
    peak_f.reverse()
    peak_m = sorted(peak_m)
    peak_m.reverse()

    peak_f = peak_f[:AMT_PARTIALS]  # highest partials
    peak_m = peak_m[:AMT_PARTIALS]

    peak_m = [x for _,x in sorted(zip(peak_f, peak_m))]  # Restore to frequency order
    peak_f = sorted(peak_f)

    return peak_m, peak_f


def compute_envelope_params(amp1, amp2, t_diff):
    return (np.log(amp1) - np.log(amp2)) / t_diff


class Instrument:

    def __init__(self, filename: str, start: float, pitch: int, volume: float = 1):
        self.p_amps = None
        self.p_freqs = None
        self.env_freqs = []
        self.env_params = []
        self.generated_notes = {}
        self.rate = 0
        self.base_pitch = pitch
        self.volume = volume

        self.generate_base(filename, start)

    def generate_base(self, filename, start):
        self.rate, data = wavfile.read(filename)

        data = data[:, 0]

        window = int(self.rate * 0.1)

        start = int(self.rate * start)  # From zooming in in Audacity

        time_diff = 0.7 - 0.0014

        rect_window_1 = data[start:start + window]
        rect_window_2 = data[
                        window * 7:window * 8]  # Still between 0.5-1s from the first window even if we ignore onset.

        s1, f1, _ = plt.magnitude_spectrum(rect_window_1, Fs=self.rate, scale="dB")
        ps1, pf1 = locate_partials(abs(s1), f1)

        self.p_amps = ps1
        self.p_freqs = pf1

        s2, f2, _ = plt.magnitude_spectrum(rect_window_2, Fs=self.rate, scale="dB")
        ps2, pf2 = locate_partials(abs(s2), f2)

        for i in range(AMT_PARTIALS):
            if pf1[i] in pf2:
                self.env_freqs.append(pf1[i])
                j = pf2.index(pf1[i])
                self.env_params.append(compute_envelope_params(ps1[i], ps2[j], time_diff))

    def create_tone(self, time_size: float, semitones: int = 0):
        time = np.linspace(0, time_size, int(self.rate * time_size))
        additive_base = np.zeros_like(time)
        for i in range(len(self.env_freqs)):
            freq = self.env_freqs[i]
            if freq * pow(2, semitones / 12) > (len(time) / SOUND_DURATION) / 2:  # nyquist limit
                continue
            envelope = self.p_amps[self.p_freqs.index(freq)] * np.exp(-self.env_params[i] * time)
            partial = envelope * np.sin(2 * np.pi * freq * pow(2, semitones / 12) * time)
            additive_base += partial

        additive_base = self.volume * additive_base / np.max(np.abs(additive_base))
        return additive_base

    def tone(self, pitch, time=SOUND_DURATION):
        note_pitch = pitch - self.base_pitch
        if (time, note_pitch) in self.generated_notes:
            return self.generated_notes[(time, note_pitch)]
        else:
            generated_tone = self.create_tone(time, note_pitch)
            self.generated_notes[(time, note_pitch)] = generated_tone
            return generated_tone


class Song:

    def __init__(self, filename, info_track=0):
        self.song = None
        self.rate = -1

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

        self.song_length = total_ticks * self.tick_length + SOUND_DURATION

        self.instruments = [(None, None)] * len(self.midi.tracks)

    def assign_instrument(self, instrument, track, offset=0):
        self.instruments[track] = (instrument, offset)
        if self.rate == -1:
            self.rate = instrument.rate

    def generate(self):

        self.song = np.zeros(int(self.rate * self.song_length))

        for (ins, off), track in zip(self.instruments, self.midi.tracks):
            tick = 0
            if ins is not None:
                for msg in track:
                    tick += msg.time
                    if msg.type == "note_on":
                        start_ind = int(tick * self.tick_length * self.rate)
                        sound = ins.tone(msg.note + off)
                        self.song[start_ind:start_ind + len(sound)] += sound

        self.song = self.song / np.max(np.abs(self.song))

    def play(self):
        if self.song is None:
            self.generate()
        print("playing!")
        sounddevice.play(self.song)
        sounddevice.wait()

    def save(self, filename):
        if self.song is None:
            self.generate()
        wavfile.write(filename, self.rate, (self.song * 32767).astype(np.int16))


if __name__ == "__main__":
    glock_f = Instrument("A2-Glockenspiel-samples/A2-Glockenspiel-samples/Gsp_ME_f_L-sus_F#5.wav", 0.0014, 78)
    glock_p = Instrument("A2-Glockenspiel-samples/A2-Glockenspiel-samples/Gsp_ME_p_L-sus_F#5.wav", 0.00127, 78, 0.5)

    song = Song("midis/nyan cat good.mid")
    song.assign_instrument(glock_f, 1)
    song.assign_instrument(glock_p, 2, 24)

    song.save("song_fun.wav")
    song.play()