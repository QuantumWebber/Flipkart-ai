import sys
import os
import spacy


nlp = spacy.load("en_core_web_sm")

#path adjust avoid import issue
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from sentiment import sentiment_model
except ImportError:
    from nlp.sentiment import sentiment_model

GENERIC_NOUNS = {
    "product", "item", "one", "thing", "seller", "flipkart", 
    "delivery", "packaging", "box", "time", "day", "app", "experience"
}


SPAM_PHRASES = [
    "must buy", "best product", "five star", "perfect product", 
    "unbelievable", "amazing quality", "five stars", "highly recommend"
]

def extract_concrete_nouns(review_text: str) -> list:
    """
    use of spacy to extract concrete nouns and proper nouns from the review text, excluding generic terms.
    """
    doc = nlp(review_text.lower())
    
    #filteration: token in doc must be noun or pronoun not in generic nouns and length>2
    concrete_nouns = [
        token.text for token in doc 
        if token.pos_ in ["NOUN", "PROPN"] 
        and token.lemma_ not in GENERIC_NOUNS
        and len(token.text) > 2
    ]
    return concrete_nouns

def detect_fake_reviews(reviews: list, ratings: list = None) -> dict:
    """
    Input: list of review strings, optional list of ratings
    Output: dict with fake%, real%, and flagged list using zero-shot syntactic analysis
        Rules:
        A. Excessive capitalization (shouting pattern)
        B. Generic positive praise with zero concrete product aspects/details (THE AI MAGIC)
        C. Contains promotional or spam hype keywords
        D. Rating-Sentiment Mismatch (Only if ratings are provided)
    """
    if not reviews:
        return {"fake": 0, "real": 0, "fake_percent": 0.0, "real_percent": 0.0, "flagged_reviews": []}

    results = {"fake": 0, "real": 0, "flagged_reviews": []}

    for i, review in enumerate(reviews):
        if not isinstance(review, str) or len(review.strip()) == 0:
            continue

        review_lower = review.lower()
        word_count = len(review.split())
        
        # 1. RoBERTa Sentiment Analysis
        try:
            res = sentiment_model(review[:512])[0]
            sentiment = res['label'].lower()  
            confidence = round(res['score'] * 100, 2)
        except Exception as e:
            print(f"Sentiment analysis failed in fake detector: {e}")
            sentiment = "neutral"
            confidence = 50.0

        is_fake = False
        reasons = []

        # Rule A: Excessive Capitalization (Shouting Pattern)
        caps_ratio = sum(1 for c in review if c.isupper()) / max(len(review), 1)
        if caps_ratio > 0.4 and len(review) > 10:
            is_fake = True
            reasons.append("Excessive capitalization (shouting pattern)")

        # Rule B  Dynamic Aspect Density Check
        # Small positive review but no no concrete nounsn
        concrete_nouns = extract_concrete_nouns(review)
        if sentiment == "positive" and word_count < 6 and len(concrete_nouns) == 0:
            is_fake = True
            reasons.append("Generic positive praise with zero concrete product aspects/details")

        # Rule C: Hype Promotional phrases
        if any(phrase in review_lower for phrase in SPAM_PHRASES):
            is_fake = True
            reasons.append("Contains promotional or spam hype keywords")

        """ # Rule D: Rating-Sentiment Mismatch (Only if ratings are provided)
        if ratings and i < len(ratings):
            rating = ratings[i]
            if rating <= 2 and sentiment == 'positive' and confidence > 75:
                is_fake = True
                reasons.append("Low rating but strongly positive sentiment")
            elif rating >= 4 and sentiment == 'negative' and confidence > 75:
                is_fake = True
                reasons.append("High rating but strongly negative sentiment") """

        
        if is_fake:
            results['fake'] += 1
            results['flagged_reviews'].append({
                "review": review,
                "reasons": reasons,
                "sentiment": sentiment,
                "confidence": confidence,
                "extracted_aspects": concrete_nouns
            })
        else:
            results['real'] += 1

    total = results['fake'] + results['real']
    if total > 0:
        results['fake_percent'] = round((results['fake'] / total) * 100, 2)
        results['real_percent'] = round((results['real'] / total) * 100, 2)
    else:
        results['fake_percent'] = 0.0
        results['real_percent'] = 0.0

    return results
