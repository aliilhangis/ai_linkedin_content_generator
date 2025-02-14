import streamlit as st
import os
from utils import get_news, generate_linkedin_content
import google.generativeai as genai

# Page configuration
st.set_page_config(
    page_title="LinkedIn Content Generator",
    page_icon="📝",
    layout="wide"
)

# Load custom CSS
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Initialize Gemini
gemini_api_key = os.getenv("GEMINI_API_KEY")
if gemini_api_key:
    genai.configure(api_key=gemini_api_key)
    # Using the most capable Gemini model
    gemini_model = genai.GenerativeModel('gemini-pro')

def main():
    # Header
    st.title("📝 LinkedIn Content Generator")
    st.markdown("""
    Generate professional LinkedIn posts based on latest news and trends.
    Enter a keyword to get started!
    """)

    # Input section
    keyword = st.text_input("Enter a keyword or topic", 
                           placeholder="e.g., Artificial Intelligence, Sustainability, Remote Work")

    if st.button("Generate Content"):
        if not keyword:
            st.error("Please enter a keyword to generate content.")
            return

        if not gemini_api_key:
            st.error("GEMINI_API_KEY not found in environment variables.")
            return

        try:
            with st.spinner("🔍 Fetching latest news..."):
                news_api_key = os.getenv("NEWS_API_KEY")
                if not news_api_key:
                    st.error("NEWS_API_KEY not found in environment variables.")
                    return

                news_data = get_news(keyword, news_api_key)

                if not news_data.get('articles'):
                    st.warning("No recent news found for this keyword. Try a different term.")
                    return

            with st.spinner("✍️ Crafting your LinkedIn post..."):
                content = generate_linkedin_content(news_data['articles'], keyword, gemini_model)

                # Display the generated content
                st.markdown("### 📱 Your LinkedIn Post")

                # Post container
                with st.container():
                    st.markdown(f"""
                    <div class="linkedin-post">
                        {content['post']}
                        <br><br>
                        {' '.join(['#' + tag for tag in content['hashtags']])}
                    </div>
                    """, unsafe_allow_html=True)

                # Source articles
                st.markdown("### 📰 Source Articles")
                for idx, article in enumerate(news_data['articles'][:5], 1):
                    st.markdown(f"""
                    <div class="linkedin-post">
                        <strong>{idx}. {article['title']}</strong><br>
                        {article['description']}<br>
                        <a href="{article['url']}" target="_blank">Read more</a>
                    </div>
                    """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()