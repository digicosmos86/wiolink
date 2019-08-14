tones = {
    'c': 262,
    'd': 294,
    'e': 330,
    'f': 349,
    'g': 392,
    'a': 440,
    'b': 494,
    'C': 523,
    ' ': 0,
}

class Buzzer(GroveOutputDevice):
    def __init__(self, port=None):
        GroveOutputDevice.__init__(self, port)
        self.buzzer = PWM(self.pin)

    def play_note(self, note, duration=0.5):
        if len(note) != 1:
            raise ValueError("This method only plays one note!")
        if note not in tones:
            raise ValueError("Note not supported!")
        try:
            self.buzzer.freq(tones[note])
            self.buzzer.duty(256)
            time.sleep(duration)
        finally:
            self.buzzer.deinit()

    def play_music(self, notes, rhythms=None, tempo=1):
        if rhythms is None:
            rhythms = [1]*len(notes)
        if len(notes) != len(rhythms):
            raise ValueError("Rhythms must have same length as notes!")
        if any(x <= 0 for x in rhythms):
            raise ValueError("Rhythms cannot have zero or negative values!")
        if any(note not in tones for note in notes):
            raise ValueError("Some notes are not supported!")
        try:
            for note, rhythm in zip(notes, rhythms):
                self.buzzer.freq(tones[note])
                self.buzzer.duty(256)
                time.sleep(tempo/rhythm)
        finally:
            self.buzzer.deinit()