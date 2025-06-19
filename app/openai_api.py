from openai import OpenAI
from dotenv import load_dotenv
import base64
import mimetypes
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)

def image_to_data_uri(image_path: str) -> str:
    mime_type, _ = mimetypes.guess_type(image_path)
    if mime_type is None:
        raise ValueError(f"Could not determine MIME type for {image_path}")

    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")

    return f"data:{mime_type};base64,{encoded}"
    
def get_user_input():
    return input(f"You: ")

def build_message(text="...", role='user', image_url=None):
    if not image_url:
        return {"role":role, "content":text}
    else:
        return {
            "role":role, 
            "content":[{"type":"text", "text":text},
                       {"type":"image_url", "image_url":{"url":image_to_data_uri(image_url)}}]
            }

def get_response(messages):
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=messages
    )

    return(completion.choices[0].message.content)

#Chat about image.jpg or whatever you have.
if __name__ == "__main__":
    messages = [
        {
            "role":"system",
            "content":"You are a helpful assistant."
        }
    ]
    message_img = build_message(text="What is this image?", image_url="resources\image.jpg")
    messages.append(message_img)
    response = get_response(messages)
    print(response)
    messages.pop()
    message_no_img = build_message(text="what is this image? Image: [Image removed to save api credits. Continue assistance with available context.]")
    messages.append(message_no_img)
    response_message = build_message(role="assistant", text=response)
    messages.append(response_message)

    while True:
        user_input = get_user_input()
        if user_input == "exitt" : break
        message = build_message(text=user_input)
        messages.append(message)
        response = get_response(messages)
        print(response)
        response_message = build_message(role="assistant", text=response)

    print(messages)




