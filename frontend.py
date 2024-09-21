import streamlit as st
import requests
import json

# Title of the Streamlit app
st.title("YouTube Video Summarizer")

# Input for YouTube video URL
video_url = st.text_input("Enter YouTube Video URL")

# Input for setting a word limit (optional)
word_limit = st.number_input("Set a word limit for the summary (optional)", min_value=50, step=50)

# Button to submit and generate the summary
if st.button("Summarize"):
    if not video_url:
        st.error("Please enter a YouTube video URL.")
    else:
        # Prepare the payload with the URL and word limit
        payload = {
            "url": video_url,
            "max_words": int(word_limit) if word_limit else None  # Send word limit only if specified
        }

        # Make a request to the Flask backend
        try:
            response = requests.post("http://127.0.0.1:5000/summarize", json=payload)

            # Handle response from the backend
            if response.status_code == 200:
                result = response.json()
                summary = result.get("summary", "No summary available.")
                st.subheader("Summary")
                st.write(summary)
            else:
                st.error(f"Error: {response.json().get('error', 'Summarization failed')}")

        except requests.exceptions.RequestException as e:
            st.error(f"Error connecting to the backend: {e}")
