import pyautogui
import openai_api
import overlay
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThread
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import QMetaObject, Qt
import tts_engine
import utils
import keyboard
import sys
import time
import threading

running = True
def stop_loop():
    global running
    print("Ctrl + Alt + Q pressed. Exiting loop.")
    running = False

keyboard.add_hotkey("ctrl+alt+q", stop_loop)

def captureScreen(path):
    screenshot = pyautogui.screenshot()
    resized = screenshot.resize((854, 480))
    resized.save(path, format="JPEG", quality=85)

screenshot_save_path = "resources/screenshot.jpg"

# Initial prompt
initial_prompt_path = "resources/monitor_initialprompt.txt"
with open(initial_prompt_path, "r", encoding="utf-8") as f:
    initial_prompt = f.read()

voice_output_path = "resources/output.wav"

messages = [{
    "role" : "system",
    "content" : initial_prompt
}]

class LoopThread(QThread):
    def run(self):
        global running
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

            def speak_and_animate():
                QMetaObject.invokeMethod(character, "set_state", Qt.QueuedConnection, args=("speaking",))
                tts_engine.play_voice(voice_output_path)
                QMetaObject.invokeMethod(character, "set_state", Qt.QueuedConnection, args=("idle",))

            # 🚀 Launch it in a separate thread
            threading.Thread(target=speak_and_animate).start()


            time.sleep(1)  # Optional: small delay to avoid hammering API

        print("Loop exited.")
        character.close()
        app.quit()  # Clean Qt exit

# PyQt app setup
app = QApplication(sys.argv)
character = overlay.Overlay()
character.show()
character.set_state("idle")

# Start threaded loop
thread = LoopThread()
thread.start()

# Start GUI event loop
sys.exit(app.exec())