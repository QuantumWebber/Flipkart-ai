import os
from dotenv import load_dotenv
from groq import Groq


current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, "../.env")


load_dotenv(dotenv_path=env_path)

groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    raise ValueError("GROQ_API_KEY not found in system environment or .env file.")

client = Groq(api_key=groq_api_key)

def summarize_reviews(reviews: list) -> dict:
    if not reviews:
        return {"summary": "No reviews found."}

    try:
        reviews_text = " ".join(reviews[:10])
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "user",
                    "content": f"Summarize these product reviews in 2-3 sentences: {reviews_text}"
                }
            ]
        )
        summary = response.choices[0].message.content
    except Exception as e:
        print(f"Groq error: {e}")
        summary = "Error generating summary using the LLM."

    return {
        "summary": summary
    }


