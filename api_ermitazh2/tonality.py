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
        detailed_scores = {'negative': 0.0, 'positive': 0.0, 'neutral': 0.0}
        
        for line in dialog:
            result = self.classifier(line)[0]
            sentiment_scores[result['label']] += result['score']
            detailed_scores[result['label']] = result['score']  
        
        dominant = max(sentiment_scores.items(), key=lambda x: x[1])
        return {
            'dominant_label': dominant[0],
            'dominant_score': dominant[1],
            'scores': detailed_scores,
            'full_analysis': dict(sentiment_scores)
        }