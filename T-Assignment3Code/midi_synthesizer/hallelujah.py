from midi_synthesizer import Song, SourceGenerator, Vowel


if __name__ == "__main__":

    sample_rate = 44100
    partials = 30
    volume = 0.3

    sg = SourceGenerator(partials, sample_rate)
    a = Vowel(sg, [680, 1120, 2760, 3360, 4200], 10, 0.8)
    u = Vowel(sg, [300, 800, 2480, 3000, 5400], 10)
    i = Vowel(sg, [280, 2120, 2840, 3560, 4280], 10)
    ae = Vowel(sg, [800, 1640, 2760, 3560, 4560], 10, 0.3)
    e = Vowel(sg, [360, 2240, 2880, 3460, 4500], 10)


    song = Song("midis/hallelujah.mid", sample_rate, volume)
    song.assign_vowel(1, ae)
    song.assign_vowel(2, a)
    song.assign_vowel(3, e)
    song.assign_vowel(4, u)
    song.assign_vowel(5, i)

    song.save("hallelujah.wav")
    song.play()
