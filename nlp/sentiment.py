from transformers import pipeline

# Model loadfrom from hugging face transformers library 
sentiment_model = pipeline(
    "sentiment-analysis",
    model="cardiffnlp/twitter-roberta-base-sentiment-latest",
    truncation=True,
    max_length=512
)

def analyze_sentiment(reviews: list) -> dict:
   
    if not reviews:
        return {"positive": 0, "negative": 0, "neutral": 0}

    results = {"positive": 0, "negative": 0, "neutral": 0}

    for review in reviews:
        if not isinstance(review, str) or len(review.strip()) == 0:
            continue
        try:
            result = sentiment_model(review[:512])[0]
            label = result['label'].lower()

            if 'positive' in label:
                results['positive'] += 1
            elif 'negative' in label:
                results['negative'] += 1
            else:
                results['neutral'] += 1

        except Exception as e:
            print(f"Error: {e}")
            continue

    # Percentage conversion
    total = sum(results.values())
    if total > 0:
        results = {k: round((v/total)*100, 2) for k, v in results.items()}

    return results

