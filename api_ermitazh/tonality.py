from transformers import pipeline
from edit import out_txt
classifier = pipeline("sentiment-analysis", model="blanchefort/rubert-base-cased-sentiment")


texts = out_txt

results = classifier(texts)
for result_tn in results: 
    print(f"Тональность: {result_tn}\n")
    sentiment_value = result_tn["label"]
