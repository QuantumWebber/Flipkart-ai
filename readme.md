---
title: Flipkart-ai
emoji: 🛍️
colorFrom: indigo
colorTo: pink
sdk: docker
pinned: false
---

# AI-Powered E-Commerce Intelligence Platform for Flipkart

A production-grade, decoupled web application that scrapes live product listings and customer reviews from Flipkart, runs multi-modal AI evaluations across NLP, Computer Vision, and Time Series pipelines, and delivers comprehensive analytics on an interactive dashboard.

The architecture is fully containerized using Docker and designed to run asynchronous deep learning pipelines alongside headless web automation in isolated environments.

---

## System Architecture

The platform follows a modern, decoupled microservices pattern:
[ REACT.JS FRONTEND ]
  (Tailwind CSS v4 + Lucide + SVG Charts)
           |                        |
   (User Query / URL)       (JSON Analytics)
           |                        |
           v                        v
    [ FASTAPI BACKEND ]  <---->  [ HUGGING FACE SECRETS ]
           |                        |
   (Launches Scraper)        (API Keys & Configs)
           |                        |
           v                        v
  [ HEADLESS SELENIUM CHROME WORKER ]
    (JSON-LD Parser + Paginated Review Scraper)
           |              |              |
           v              v              v
   [ NLP PIPELINE ]  [ CV PIPELINE ]  [ TIME SERIES ]
   (RoBERTa, spaCy,  (OpenCV + CLIP)  (Meta Prophet)
    Llama 3.1)
---

## Core Machine Learning Pipelines

### 1. Natural Language Processing (NLP)

- **Sentiment Analysis** — Uses a fine-tuned `cardiffnlp/twitter-roberta-base-sentiment-latest` Transformer model to classify review sentiment with confidence probabilities.
- **Spam & Fraud Detection** — Implements an unsupervised, domain-agnostic spam filter using spaCy Part-of-Speech (POS) tagging to extract noun chunks and evaluate detail specificity, bypassing fragile keyword rules.
- **Generative Review Summarization** — Compiles up to 30 customer reviews and uses the Groq Llama 3.1 API to generate structured consumer insights with pros and cons.

### 2. Computer Vision (CV)

- **Technical Quality Assessment** — Uses OpenCV to check image resolution and calculate focus sharpness via Laplacian Variance to flag blurry listings.
- **Aesthetic Evaluation** — Uses OpenAI's CLIP model (`openai/clip-vit-base-patch32`) for zero-shot image classification, grading the professional composition of merchant-uploaded images.
- **Listing Integrity Verification** — Leverages CLIP's multi-modal alignment to cross-reference product descriptions with image embeddings, detecting potential seller fraud or wrong-listing errors.

### 3. Time Series Price Forecasting

- **Trend Analysis** — Generates historical pricing charts and trains Meta's Prophet model to forecast product prices for the next 14 days.
- **Technical Financial Indicators** — Calculates Support (Floor) and Resistance (Ceiling) levels alongside a 14-day RSI to generate dynamic buy, hold, or wait signals.

### 4. Recommendation System

Implements a hybrid recommendation algorithm scoring alternative products based on title similarity (SequenceMatcher syntactic overlap) and price advantage metrics.

---

## Resilient Web Scraping Strategies

To handle dynamic layouts and anti-bot measures:

- **JSON-LD SEO Schema Parsing** — Extracts product metadata from background `application/ld+json` script tags, which Flipkart maintains for Google Search indexing and cannot easily modify without impacting SEO rankings.
- **Universal Link Selection** — Evaluates whether elements are standalone anchor tags or wrappers to seamlessly parse both Grid and List page layouts.
- **Auto-Clicking Expander** — Uses Selenium to locate and expand collapsed specification blocks before reading page content.
- **Fast Pagination** — Uses a single, continuous Selenium session with automated scrolling to scrape up to 30 reviews across multiple pages efficiently.

---

## Project Structure
ecom-ai/
├── nlp/
│ ├── init.py
│ ├── sentiment.py # RoBERTa Sentiment Analysis
│ ├── summarizer.py # spaCy & Groq Llama 3.1 Summaries
│ └── fake_detector.py # spaCy Syntactic Spam Analyzer
├── scraper/
│ ├── init.py
│ ├── search_scraper.py # Selenium Search Scraper
│ └── review_scraper.py # Selenium Review Scraper
├── cv/
│ ├── init.py
│ └── image_quality.py # OpenCV & CLIP Aesthetic/Integrity Analysis
├── timeseries/
│ ├── init.py
│ └── price_forecast.py # Meta Prophet & Financial Metrics
├── recsys/
│ ├── init.py
│ └── recommender.py # Value-based Recommendation Engine
├── main.py # FastAPI Backend Server & Endpoints
├── Dockerfile # Unified Multi-Stage Dockerfile (React + FastAPI)
├── requirements.txt # Unified dependencies
├── .env # Local Environment Variables
└── .gitignore
code
Code
---

## Local Installation & Deployment

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) for containerized deployment
- Python 3.11+ and Node.js 20+ for manual local execution

### Option A: Containerized Deployment (Recommended)

**1. Clone the repository:**

```bash
git clone https://github.com/your-username/ecom-ai.git
cd ecom-ai
2. Configure environment variables:
Create a .env file in the project root:
code
Code
GROQ_API_KEY=your_groq_api_key_here
3. Launch the stack:
Ensure Docker Desktop is running, then execute:
code
Bash
docker-compose up --build
Service	URL
React Frontend	http://localhost:80
FastAPI Backend	http://localhost:8000
Swagger API Docs	http://localhost:8000/docs
code
Code
---

### Step 3: Run These Git Commands in Your Terminal

Now, run these three commands in your terminal at the project root (`ecom-ai/`) to push the clean configuration to Hugging Face [2]:

```bash
git add .
git commit -m "Configure correct Hugging Face Space metadata"
git push hf main:main