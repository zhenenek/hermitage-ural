import ollama
import sqlite3
from edit import out_txt
from prompt import prompt
from bd import save_to_db  

client = ollama.Client()

model = "deepseek-r1:14b"

model_reply = client.generate(model=model, prompt=prompt)
result = model_reply.response

print('Response:')
print(result)
save_to_db(result)