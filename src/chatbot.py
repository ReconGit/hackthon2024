from enum import Enum
from textwrap import dedent
from typing import Optional

import openai
from dotenv import load_dotenv
from pydantic import BaseModel


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
    issues: list[Improvement]
    rating: int


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
            Based on the instructions that were provided in template file evaluate my request in filled document. Make sure to structure your evaluation in a way that conforms to this JSON design:
            
            [
                {
                    "type": level,
                    "message": message,
                    "occurrence": occurrence,
                    "suggestion": suggestion,
                }
            ]
            
            Instructions:
            Types can fall under these categories (each determining what the message, occurrence and suggestion will contain):
            "missing" - things that are expected to be included but were not found in the document
                - message: items that are missing (should be at most 80 characters long)
                - occurrence: ""
                - suggestion: ""
            "incorrect" - things that should not be present, or are written incorrectly but cannot be repaired using available context (like incorrect formatting of the phone number, email address...)
                - message: what is incorrect and the reason why it is incorrect (should be at most 80 characters long)
                - occurrence: the exact citation of the occurrence in text
                - suggestion: ""
            "improvable" - things that could be improved, worded differently, adjusted to fit the standard etc.
                - message: what is improvable and the reason why it is improvable (should be at most 80 characters long)
                - occurrence: the exact citation of the occurrence in text
                - suggestion: an example/suggestion with what the instance could be replaced with
            
            rating: percentual rating of the quality of the data provided by user in the filled document 
            in respect to the template document
            Notice important information such as timetables, names, dates, goals, finances. 
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

    def get_summary(self, message_history):
        system_prompt = dedent(
            """
            Summarize what this filled document is about in no more than 300 characters (around 3 sentences) 
            as if it was a description of the file in a document viewing application
            """
        ).strip()
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(message_history)

        structure = self.openai_client.beta.chat.completions.parse(
            messages=messages,  # type: ignore
            model="gpt-4o-mini",
            temperature=0.0,
        )
        return structure.choices[0].message.parsed


if __name__ == "__main__":
    chatbot = Chatbot()
    print(chatbot.get_chat_completion("Hello!, can you provide me with information I need to fill to get a loan?"))
