import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
)

completion = client.chat.completions.create(
    model="qwen3.7-plus",
    messages=[
        {
            "role": "system",
            "content": "You are an intake assistant for a mental health group therapy program called Anxiety Unplugged. Extract the following from the user's message: name (if given), presenting concern, urgency level (low/medium/high), and suggested next question to ask. Respond in JSON."
        },
        {
            "role": "user",
            "content": "Hi, I've been struggling with anxiety for months now and I can't sleep at night. My name is Tunde."
        }
    ]
)

print(completion.choices[0].message.content)
