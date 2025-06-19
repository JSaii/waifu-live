import openai_api
import tts_engine

# Initial prompt
initial_prompt_path = "resources/initialprompt.txt"
with open(initial_prompt_path, "r", encoding="utf-8") as f:
    initial_prompt = f.read()

voice_output_path = "resources/output.wav"

messages = [{
    "role" : "system",
    "content" : initial_prompt
}]

while True:
    user_input = openai_api.get_user_input()
    if user_input == "exitt":break
    user_message = openai_api.build_message(text=user_input)

    messages.append(user_message)

    response = openai_api.get_response(messages)
    response_message = openai_api.build_message(role="assistant", text=response)

    messages.append(response_message)

    print(response)

    tts_engine.generate_voice(response, voice_output_path)
    tts_engine.play_voice(voice_output_path)

print(messages)
