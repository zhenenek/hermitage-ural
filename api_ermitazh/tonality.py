from transformers import pipeline
from collections import defaultdict

class TonalityAnalyzer:
    def __init__(self):
        self.classifier = pipeline(
            "text-classification",
            model="seara/rubert-tiny2-russian-sentiment",
            tokenizer="seara/rubert-tiny2-russian-sentiment"
        )

    def analyze(self, dialog):
        sentiment_scores = defaultdict(float)
        
        for line in dialog:
            result = self.classifier(line)[0]
            sentiment_scores[result['label']] += result['score']
        
        dominant = max(sentiment_scores.items(), key=lambda x: x[1])
        return dominant[0]