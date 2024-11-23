from textwrap import dedent

import openai
from dotenv import load_dotenv

system_prompt = dedent(
    """
You are a form validation assistant. You are helping a user fill out a form.
Make sure the data is valid, point out inconsistencies and suggest corrections. 
    """
).strip()


class Chatbot:
    def __init__(self):
        load_dotenv()
        self.openai_client = openai.OpenAI()

    def get_completion(self, user_message: str):
        completion = self.openai_client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            model="gpt-4o-mini",
            temperature=0.0,  # for reproducibility
        )
        return completion.choices[0].message.content


if __name__ == "__main__":
    chatbot = Chatbot()
    print(chatbot.get_completion("Hello!, can you provide me with information I need to fill to get a loan?"))
