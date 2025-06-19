import pyautogui
import openai_api
import tts_engine

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

while True:
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

    print(response)

    tts_engine.generate_voice(response, voice_output_path)
    tts_engine.play_voice(voice_output_path)

    print(messages)