import os
import requests
from datetime import datetime, timedelta
import google.generativeai as genai
import json
import re

def is_turkish(text):
    """Check if text contains Turkish characters."""
    turkish_chars = 'ğüşıöçĞÜŞİÖÇ'
    return any(char in text for char in turkish_chars)

def get_news(keyword, api_key):
    """Fetch news articles from NewsAPI."""
    base_url = "https://newsapi.org/v2/everything"

    # Calculate date 30 days ago
    thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

    # If keyword contains Turkish characters, prioritize Turkish results
    if is_turkish(keyword):
        language = 'tr'
    else:
        language = 'tr,en'

    params = {
        'q': keyword,
        'from': thirty_days_ago,
        'sortBy': 'relevancy',
        'language': language,
        'apiKey': api_key
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise Exception(f"Failed to fetch news: {str(e)}")

def generate_linkedin_content(articles, keyword, gemini_client):
    """Generate LinkedIn content using Google's Gemini."""

    # Prepare the articles summary
    articles_summary = "\n\n".join([
        f"Title: {article['title']}\nDescription: {article['description']}"
        for article in articles[:5]  # Use top 5 articles
    ])

    # Determine language based on keyword and articles
    is_turkish_content = is_turkish(keyword) or any(is_turkish(article['title']) for article in articles[:5])

    system_instruction = "Sen profesyonel bir LinkedIn içerik üreticisisin." if is_turkish_content else "You are a professional LinkedIn content creator."

    prompt = f"""{system_instruction}

Şu konudaki güncel haberler hakkında bir LinkedIn gönderisi oluştur: {keyword}

Haberler:
{articles_summary}

Lütfen şu kriterlere göre bir gönderi oluştur:
1. Dikkat çekici bir giriş cümlesi
2. Haberlerden önemli içgörüler
3. Profesyonel bir bakış açısı
4. Düşündürücü bir soru veya çağrı ile bitiş
5. İlgili hashtagler

Yanıtı şu JSON formatında ver:
{{
    "post": "LinkedIn gönderisi metni",
    "hashtags": ["ilgili", "hashtagler"]
}}

Not: Gönderi uzunluğu LinkedIn için uygun olmalı (1300 karakterden az).""" if is_turkish_content else f"""Based on these recent news articles about {keyword}:

{articles_summary}

Create a professional LinkedIn post that:
1. Starts with a compelling hook
2. Includes key insights from the news
3. Adds professional perspective
4. Ends with a thought-provoking question or call to action
5. Includes relevant hashtags

Format the response as a JSON string with these fields:
- post: The main LinkedIn post content
- hashtags: Array of relevant hashtags

Keep the tone professional yet engaging, and the length appropriate for LinkedIn (under 1300 characters)."""

    try:
        response = gemini_client.generate_content(prompt)

        # Parse the response text as JSON
        try:
            result = json.loads(response.text)
            return result
        except json.JSONDecodeError:
            # If JSON parsing fails, try to extract content in a more forgiving way
            content = response.text
            # Simple fallback format
            return {
                "post": content.split("#")[0].strip(),
                "hashtags": [tag.strip() for tag in content.split("#")[1:] if tag.strip()]
            }

    except Exception as e:
        raise Exception(f"Failed to generate content: {str(e)}")