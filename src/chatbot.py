from textwrap import dedent

import openai
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Optional
from enum import Enum


class FormStructure(BaseModel):
    sender_name: str
    sender_physical_address: str
    addressee_name: str
    addressee_physical_address: str
    current_date: str
    # TODO: Add more fields

class ImprovementType(str, Enum):
    improvable = "improvable"
    missing = "missing"
    incorrect = "incorrect"

class Improvement(BaseModel):
    type: ImprovementType
    message: str
    occurrence: str | None
    suggestion: str | None


class Analysis(BaseModel):
    issue: list[Improvement]

class Chatbot:
    def __init__(self):
        load_dotenv()
        self.openai_client = openai.OpenAI()

    def get_chat_completion(self, message_history):
        system_prompt = dedent(
            """
            You are a Form Validation Assistant. You are helping a user fill out a form.
            Make sure the data is valid, point out inconsistencies and suggest corrections.
            """
        ).strip()
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(message_history)

        completion = self.openai_client.chat.completions.create(
            messages=messages,  # type: ignore
            model="gpt-4o-mini",
            temperature=0.0,  # for reproducibility
        )
        return completion.choices[0].message.content

    def get_structured_output(self, message_history):
        system_prompt = dedent(
            """
            Extract the structure from the given text.
            If some information is missing or is ambiguous, please provide an empty placeholder (null).
            """
        ).strip()
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(message_history)

        structure = self.openai_client.beta.chat.completions.parse(
            messages=messages,  # type: ignore
            model="gpt-4o-mini",
            temperature=0.0,
            response_format=FormStructure,
        )
        return structure.choices[0].message.parsed

    def get_analysis(self, message_history):
        system_prompt = dedent(
            """
            Extract the structure from the given text.
            If some information is missing or is ambiguous, please provide an empty placeholder (null).
            """
        ).strip()
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(message_history)

        structure = self.openai_client.beta.chat.completions.parse(
            messages=messages,  # type: ignore
            model="gpt-4o-mini",
            temperature=0.0,
            response_format=Analysis,
        )
        return structure.choices[0].message.parsed


if __name__ == "__main__":
    chatbot = Chatbot()
    print(chatbot.get_chat_completion("Hello!, can you provide me with information I need to fill to get a loan?"))
