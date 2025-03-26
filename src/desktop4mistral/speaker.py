from .state import State
from str2speech.speaker import Speaker as S
import tempfile
import scipy.io.wavfile as wav
import sounddevice as sd
import os

class Speaker:
    def __init__(self):
        self.speaker = S(tts_model="kokoro")

    def speak(self, text: str):
        if State.get_talk_mode():
            tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            print(tfile.name)
            self.speaker.text_to_speech(text, tfile.name)
            dir_path = os.path.dirname(os.path.realpath(tfile.name))
            file_name = os.path.basename(tfile.name)
            file_name = "0_" + file_name
            sample_rate, data = wav.read(os.path.join(dir_path, file_name))
            sd.play(data, sample_rate)
            tfile.close()
        