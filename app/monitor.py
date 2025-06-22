import pyautogui
import openai_api
import utils
from overlay import run_overlay
from send_chat import run_chatbox
import keyboard
from multiprocessing import Process, Queue, Event
import time
import resources_paths
import time_date_weather
import mss
from PIL import Image
from camera_monitor import run_camera

running = True
switch_to_camera = False

def stop_loop():
    global running
    print("Ctrl+Alt+Q pressed — stopping loop.")
    running = False

keyboard.add_hotkey("ctrl+alt+q", stop_loop)

def get_image(path, camera_event = None, monitor_index=2):
    if camera_event:
        print("Snapping camera...")
        camera_event.set()
    else:
        print("Taking a screenshot...")
        with mss.mss() as sct:
            # Get information about all monitors
            monitors = sct.monitors  # [0] is all, [1] is first, etc.

            if monitor_index >= len(monitors):
                raise ValueError(f"Monitor index {monitor_index} out of range.")

            monitor = monitors[monitor_index]
            screenshot = sct.grab(monitor)
            img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
            resized = img.resize((1280, 720))
            resized.save(path, format="JPEG", quality=85)

screenshot_save_path = "resources/screenshot.jpg"

# Initial prompt
initial_prompt_path = resources_paths.MONITOR_INITIAL_PROMPT_PATH
with open(initial_prompt_path, "r", encoding="utf-8") as f:
    initial_prompt = f.read()

voice_output_path = "resources/output.wav"

# Get time and date, location, and today's weather.
date_time = time_date_weather.get_datetime_with_day()
weather = time_date_weather.get_weather()
today_info = f"Currently it is {date_time}, {weather}"
print(today_info)

messages = [{
    "role" : "system",
    "content" : initial_prompt
},
{
    "role":"system",
    "content":"返答はみじかくしてください。「（てれて）」「（どきどき）」みたいな表現は使っちゃダメ。ふつうにしゃべってね。「〜」と「！」は、へんじのなかでぜったいに使わないでね。ローマ字はぜったいに使わないでください。"
},
{
    "role":"system",
    "content":today_info
}]

def monitor(queue: Queue, send_chat_queue: Queue, camera_event = None):
     while running:
        is_chatting = False
        if not send_chat_queue.empty():
            is_chatting = True
            text = send_chat_queue.get()
            print(f"Sending: {text}")
            message = openai_api.build_message(text=text)
            messages.append(message)
        else:
            print("Empty queue")
        
        if not is_chatting:
            get_image(screenshot_save_path, camera_event)
            print("Screenshot captured...")
            img_message = openai_api.build_message(text="...", role="user", image_path=screenshot_save_path)
            messages.append(img_message)

        print("Generating response...")
        response = openai_api.get_response(messages)
        response_message = openai_api.build_message(role="assistant", text=response)

        if not is_chatting:
            messages.pop()
            messages.append(openai_api.build_message(text="..., image:[Image removed to save api credits. Continue with available context.]"))

        messages.append(response_message)

        print(f"Response: {response}")

        response = utils.convert_to_hiragana(response)

        tts_engine.generate_voice(response, voice_output_path)

        utils.play_voice_with_feedback(voice_output_path, queue)


if __name__ == "__main__":
    import tts_engine
    use_camera=True
    if use_camera:
        print(f"Initializing camera...")
        ready_event = Event()
        camera_event = Event()
        camera_proc = Process(target=run_camera, args=(camera_event, ready_event))
        camera_proc.start()
        ready_event.wait()
        print(f"Initializing camera...[Complete]")
    else:
        camera_event = None
    
    print(camera_event)
    print(f"Initializing overlay...")
    queue = Queue()
    overlay_proc = Process(target=run_overlay, args=(queue,))
    overlay_proc.start()
    print(f"Initializing overlay...[Complete]")
    print(f"Initializing send chatbox...")
    send_chat_queue = Queue()
    send_chat_proc = Process(target=run_chatbox, args=(send_chat_queue,))
    send_chat_proc.start()
    print(f"Initializing send chatbox...[Complete]")

    print(f"Initializing tts...")
    tts_engine.init_tts()
    print(f"Initializing tts...[Complete]")
    print(f"Starting monitor...")
    monitor(queue, send_chat_queue, camera_event)

    overlay_proc.terminate()
    send_chat_proc.terminate()
    overlay_proc.join()
    send_chat_proc.join()