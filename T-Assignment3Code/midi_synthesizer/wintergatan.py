from midi_synthesizer import Song, SourceGenerator, Vowel


if __name__ == "__main__":

    sample_rate = 44100
    partials = 30
    volume = 0.1

    sg = SourceGenerator(partials, sample_rate)
    a = Vowel(sg, [680, 1120, 2760, 3360, 4200], 10)
    u = Vowel(sg, [240, 800, 2480, 3000, 5400], 10)

    song = Song("midis/Wintergatan - Marble Machine.mid", sample_rate, volume)
    song.assign_vowel(2, a)
    song.assign_vowel(1, u)

    song.save("Wintergatan.wav")
    song.play()