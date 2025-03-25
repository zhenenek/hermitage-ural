from openai import OpenAI
from tonality import TonalityAnalyzer
from bd import save_to_db
from prompt import prompt, text
from key import api_key

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key
)

def process_dialog():
    analyzer = TonalityAnalyzer()
    sentiment = analyzer.analyze(text)

    completion = client.chat.completions.create(
        extra_body={},
        model="deepseek/deepseek-chat:free",
        messages=[{"role": "user", "content": prompt}]
    )

    response = completion.choices[0].message.content
    save_to_db(response, sentiment)

if __name__ == "__main__":
    process_dialog()
    