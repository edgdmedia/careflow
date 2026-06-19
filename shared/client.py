import os
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


def get_qwen_client() -> OpenAI:
    return OpenAI(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
    )
