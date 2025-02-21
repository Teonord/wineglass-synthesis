from midi_synthesizer import Instrument, Song


if __name__ == "__main__":
    glock_f = Instrument("A2-Glockenspiel-samples/A2-Glockenspiel-samples/Gsp_ME_f_L-sus_F#5.wav", 0.0014, 78)
    glock_p = Instrument("A2-Glockenspiel-samples/A2-Glockenspiel-samples/Gsp_ME_p_L-sus_F#5.wav", 0.00127, 78, 0.5)

    song = Song("midis/Wintergatan - Marble Machine.mid")
    song.assign_instrument(glock_f, 2)
    song.assign_instrument(glock_p, 1)

    song.save("song_wintergatan.wav")
    song.play()