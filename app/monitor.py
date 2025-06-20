import pyautogui
import openai_api
import utils
from overlay import run_overlay
import keyboard
from multiprocessing import Process, Queue
import time
import resources_paths

running = True

def stop_loop():
    global running
    print("Ctrl+Alt+Q pressed — stopping loop.")
    running = False

keyboard.add_hotkey("ctrl+alt+q", stop_loop)

def captureScreen(path):
    screenshot = pyautogui.screenshot()
    resized = screenshot.resize((1280, 720))
    resized.save(path, format="JPEG", quality=85)

screenshot_save_path = "resources/screenshot.jpg"

# Initial prompt
initial_prompt_path = resources_paths.MONITOR_INITIAL_PROMPT_PATH
with open(initial_prompt_path, "r", encoding="utf-8") as f:
    initial_prompt = f.read()

voice_output_path = "resources/output.wav"

messages = [{
    "role" : "system",
    "content" : initial_prompt
}]

def monitor(queue: Queue):
     while running:
        captureScreen(screenshot_save_path)
        print("Screenshot captured...")
        img_message = openai_api.build_message(text="...", role="user", image_path=screenshot_save_path)
        messages.append(img_message)

        print("Generating response...")
        response = openai_api.get_response(messages)
        response_message = openai_api.build_message(role="assistant", text=response)

        messages.pop()
        messages.append(openai_api.build_message(text="..., image:[Image removed to save api credits. Continue with available context.]"))

        messages.append(response_message)

        print(f"Response: {response}")

        response = utils.convert_to_hiragana(response)

        tts_engine.generate_voice(response, voice_output_path)

        queue.put('speaking')
        tts_engine.play_voice(voice_output_path)
        queue.put('idle')


if __name__ == "__main__":
    import tts_engine
    print(f"Initializing overlay...")
    queue = Queue()
    overlay_proc = Process(target=run_overlay, args=(queue,))
    overlay_proc.start()
    print(f"Initializing overlay...[Complete]")

    print(f"Initializing tts...")
    tts_engine.init_tts()
    print(f"Initializing tts...[Complete]")
    print(f"Starting monitor...")
    monitor(queue)

    overlay_proc.terminate()
    overlay_proc.join()