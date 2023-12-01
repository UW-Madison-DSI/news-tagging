import ast
import asyncio
import os

import openai
from aiohttp import ClientSession
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("GPT_MODEL")
TEMPERATURE = float(os.getenv("GPT_TEMPERATURE"))


def tag(text: str) -> list[str]:
    """Tag news into one or more category / tags."""

    system_message = {
        "role": "system",
        "content": "You are a journalist who can accurately categorized news into one or more categories / tags. You organize your output like a python list, similar to this ['tag1', 'tag2']",
    }

    user_message = {
        "role": "user",
        "content": f"Please tag the following news into one or more categories: '{text}'",
    }

    response = openai.ChatCompletion.create(
        model=MODEL, messages=[system_message, user_message], temperature=TEMPERATURE
    )

    return ast.literal_eval(response["choices"][0]["message"]["content"])


async def user_tag(text: str, target_tags: list) -> list[str]:
    """Tag news into one or more targeted category / tags."""

    system_message = {
        "role": "system",
        "content": f"You are a journalist who can accurately categorized news into one or more categories / tags. \
            Pick one or more categories / tags from the following list: {target_tags}. \
            You organize your output like a python list, similar to this ['tag1', 'tag2']",
    }

    user_message = {
        "role": "user",
        "content": f"Please tag the following news into one or more categories: '{text}'",
    }

    response = await openai.ChatCompletion.acreate(
        model=MODEL, messages=[system_message, user_message], temperature=TEMPERATURE
    )

    proposed_tags = ast.literal_eval(response["choices"][0]["message"]["content"])
    return list(set(proposed_tags).intersection(target_tags))


async def batch_user_tag(texts: list[str], target_tags: list) -> list[list[str]]:
    """Tag news in batch mode in targeted categories."""

    openai.aiosession.set(ClientSession())
    async_responses = [user_tag(text, target_tags) for text in texts]
    user_tag_results = await asyncio.gather(*async_responses)
    await openai.aiosession.get().close()
    return user_tag_results
