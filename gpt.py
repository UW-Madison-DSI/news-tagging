import ast
import os

import openai
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")


def tag(title: str, content: str):
    """Tag news into one or more category / tags."""

    system_message = {
        "role": "system",
        "content": "You are a journalist who can accurately categorized news into one or more categories / tags. You organize your output like a python list, similar to this ['tag1', 'tag2']",
    }

    user_message = {
        "role": "user",
        "content": f"Please tag the following news into one or more categories: '{title} {content}'",
    }

    response = openai.ChatCompletion.create(
        model="gpt-4", messages=[system_message, user_message], temperature=0.9
    )

    assert len(response["choices"]) == 1
    return ast.literal_eval(response["choices"][0]["message"]["content"])
