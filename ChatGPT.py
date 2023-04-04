import os
import openai
from dotenv import load_dotenv
load_dotenv()


openai.api_key = os.getenv('CHATGPT_API_KEY')
print(os.getenv('CHATGPT_API_KEY'))

max_messages = 10

for i in range(max_messages):
    prompt = input("- ")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": prompt},
        ]
    )
    result = ''
    for choice in response.choices:
        result += choice.message.content
    print(f"+ {result}")
