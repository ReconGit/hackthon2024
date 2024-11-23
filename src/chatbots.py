from textwrap import dedent

import openai
from dotenv import load_dotenv
from pydantic import BaseModel


class FormStructure(BaseModel):
    name: str
    # TODO: Add more fields


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

    def get_structure(self, message):
        system_prompt = dedent(
            """
            Extract the structure from the given text.
            If some information is missing or is ambiguous, please provide an empty placeholder (null).
            """
        ).strip()

        structure = self.openai_client.beta.chat.completions.parse(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message},
            ],
            model="gpt-4o-mini",
            temperature=0.0,
            response_format=FormStructure,
        )
        return structure.choices[0].message.parsed


if __name__ == "__main__":
    chatbot = Chatbot()
    print(chatbot.get_chat_completion("Hello!, can you provide me with information I need to fill to get a loan?"))
