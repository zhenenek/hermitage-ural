from openai import OpenAI
from transformers import pipeline
from prompt import prompt
from key import api_key
from bd import save_to_db


sentiment_classifier = pipeline(
    "sentiment-analysis", 
    model="blanchefort/rubert-base-cased-sentiment"
)

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key
)

def analyze_sentiment(text):
    result = sentiment_classifier(text)[0]
    return result["label"]

if __name__ == "__main__":
    completion = client.chat.completions.create(
        extra_body={},
        model="deepseek/deepseek-chat:free",
        messages=[{"role": "user", "content": prompt}]
    )
    
    response_content = completion.choices[0].message.content
    print(response_content)
    
    sentiment = analyze_sentiment(response_content)
    print(sentiment)
    save_to_db(response_content, sentiment)