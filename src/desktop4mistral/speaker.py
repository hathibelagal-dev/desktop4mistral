from .state import State
from str2speech.speaker import Speaker as S
import tempfile
import scipy.io.wavfile as wav
import sounddevice as sd

class Speaker:
    def __init__(self):
        self.speaker = S(tts_model="kokoro")

    def speak(self, text: str):
        if State.get_talk_mode():
            tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            print(tfile.name)
            self.speaker.text_to_speech(text, tfile.name)
            sample_rate, data = wav.read(tfile.name)
            sd.play(data, sample_rate)
            tfile.close()
        
        