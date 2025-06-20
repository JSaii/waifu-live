from pykakasi import kakasi
import numpy as np
import soundfile as sf
import simpleaudio as sa
import time

def convert_to_hiragana(text: str) -> str:
    kks = kakasi()
    result = kks.convert(text)
    return "".join(item["hira"] for item in result)

def play_voice_with_feedback(wav_path, queue, threshold=0.0025, chunk_duration=0.075):
    data, samplerate = sf.read(wav_path)

    if len(data.shape) == 2:
        data = data.mean(axis=1)  # convert to mono

    # Normalize
    data = data / np.max(np.abs(data))

    frame_samples = int(samplerate * chunk_duration)
    total_chunks = len(data) // frame_samples

    # Play audio
    wave_obj = sa.WaveObject.from_wave_file(wav_path)
    play_obj = wave_obj.play()

    for i in range(total_chunks):
        chunk = data[i * frame_samples:(i + 1) * frame_samples]
        rms = np.sqrt(np.mean(chunk ** 2))
        state = 'speaking' if rms > threshold else 'idle'
        queue.put(state)
        time.sleep(chunk_duration)

    # Ensure it ends in idle
    queue.put('idle')

if __name__ =="__main__":
    from multiprocessing import Process, Queue
    from overlay import run_overlay
    print(f"Initializing overlay...")
    queue = Queue()
    overlay_proc = Process(target=run_overlay, args=(queue,))
    overlay_proc.start()
    play_voice_with_feedback("resources/output.wav", queue, 0.0025, 0.075)
    overlay_proc.terminate()
    overlay_proc.join()
