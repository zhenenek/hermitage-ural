from openai import OpenAI
from prompt import prompt
from key import api_key
from bd import save_to_db
client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key= api_key
)
completion = client.chat.completions.create(
  extra_body={},
  model="deepseek/deepseek-chat:free",
  messages=[
    {
      "role": "user",
      "content": prompt 
    }
  ]
)
print(completion.choices[0].message.content)
save_to_db(completion.choices[0].message.content)