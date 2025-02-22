from midi_synthesizer import Song, SourceGenerator, Vowel


if __name__ == "__main__":

    sample_rate = 44100
    partials = 50
    volume = 0.1

    sg = SourceGenerator(partials, sample_rate)
    a = Vowel(sg, [680, 1120, 2760, 3360, 4200], 10)
    u = Vowel(sg, [240, 800, 2480, 3000, 5400], 10)
    ae = Vowel(sg, [800, 1640, 2760, 3560, 4560], 10)

    song = Song("midis/simple melody.mid", sample_rate, volume)
    song.assign_vowel(1, u)
    song.assign_vowel(2, a)
    song.assign_vowel(3, ae)

    song.save("Simple.wav")
    song.play()