# Use F5 TTS Engine
'''
For the Japanese checkpoint, 
you need to create the config in ...\site-packages\f5_tts\configs:
    1. Copy one of the configs inside the folder, 
    2. and modify the fields to match the provided config, and name it "F5TTS_JA".
'''

from importlib.resources import files
from f5_tts.api import F5TTS
from cached_path import cached_path
import pykakasi
import re
import simpleaudio as sa
import resources_paths

f5tts = None
speaker_path = ""
ref_text = ""

def init_tts():
    global f5tts, speaker_path, ref_text, output_path
    vocab_local_path = str(cached_path("hf://Jmica/F5TTS/JA_21999120/vocab_japanese.txt"))
    ckpt_local_path = str(cached_path("hf://Jmica/F5TTS/JA_21999120/model_21999120.pt"))
    ref_text_path = resources_paths.REF_TEXT_PATH
    speaker_path = resources_paths.SPEAKER_PATH
    output_path = r"resources/output.wav"

    with open(ref_text_path, "r", encoding="utf-8") as f:
        ref_text = f.read()

    print(ref_text)

    f5tts = F5TTS(model="F5TTS_JA",
                ckpt_file=ckpt_local_path,
                vocab_file=vocab_local_path)


def contains_romaji(text: str) -> bool:
    return bool(re.search(r"[A-Za-z]", text))

def generate_voice(text: str, voice_output_path: str):
    f5tts.infer(
        ref_file=speaker_path,
        ref_text=ref_text,
        gen_text=text,
        file_wave=voice_output_path,
        remove_silence=True,
        speed=0.75,
        seed=None,
        show_info=lambda *args, **kwargs: None,
        progress=None
    )

def play_voice(path: str):
    wave_obj = sa.WaveObject.from_wave_file(path)
    play_obj = wave_obj.play()
    play_obj.wait_done()

#TTS
if __name__ == "__main__":
    init_tts()
    while(True):
        text = input("Your text : ")
        #if contains_romaji(text) : continue

        generate_voice(text, "resources/output.wav")
        play_voice(output_path)
