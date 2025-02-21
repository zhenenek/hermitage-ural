import ollama 
from edit import  out_txt
from prompt import prompt
client = ollama.Client()


model = "deepseek-r1:14b"

model_reply = client.generate(model = model,prompt = prompt)
result = model_reply.response
print('Response:')
print(model_reply.response)
