from transformers import pipeline
from prompt import text
classifier = pipeline("sentiment-analysis", model="blanchefort/rubert-base-cased-sentiment")


texts = text

results = classifier(texts)
for result_tn in results: 
    print(f"Тональность: {result_tn}\n")
    sentiment_value = result_tn["label"]