import ollama
from edit import out_txt
from prompt import prompt
from bd import save_to_db  

client = ollama.Client()
model = "deepseek-r1:14b"

model_reply = client.generate(model=model, prompt=prompt)
result = model_reply.response

def extract_answer(result):
    parts = result.split("</think>")
    
    if len(parts) > 1:
        return parts[1].strip()
    
    
    return result.strip()
def extract_answer(result):
    parts = result.split("</think>")
    
    if len(parts) > 1:
        return parts[1].strip()
    
    
    return result.strip()

clean_response = extract_answer(result)
print(clean_response)
save_to_db(clean_response)
