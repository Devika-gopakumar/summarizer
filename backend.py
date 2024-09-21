from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from transformers import pipeline
import re

app = Flask(__name__)

# Initialize a more powerful summarization pipeline (you can choose a different model as per performance)
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Function to chunk the transcript into smaller pieces
def chunk_transcript(transcript, chunk_size=500):
    words = transcript.split()
    for i in range(0, len(words), chunk_size):
        yield " ".join(words[i:i + chunk_size])

# Function to intelligently summarize the transcript with a word limit
def summarize_transcript_intelligently(transcript, max_words=None):
    summaries = []
    for chunk in chunk_transcript(transcript):
        # Dynamically set a shorter summary length if max_words is provided
        summary = summarizer(chunk, max_length=100, min_length=30, do_sample=False)
        summaries.append(summary[0]['summary_text'])

    # Combine all chunks to get a full summary
    full_summary = " ".join(summaries)
    words = full_summary.split()

    # If a word limit is specified, intelligently trim and return key sentences within limit
    if max_words:
        summarized_output = []
        word_count = 0
        for sentence in full_summary.split('.'):
            sentence_words = sentence.split()
            if word_count + len(sentence_words) <= max_words:
                summarized_output.append(sentence)
                word_count += len(sentence_words)
            else:
                break  # Stop once we've hit the word limit

        return ". ".join(summarized_output).strip() + '.' if summarized_output else full_summary

    # Return the full summary if no word limit is specified
    return full_summary

# Function to extract video ID from a YouTube URL
def extract_video_id(url):
    video_id_match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    if video_id_match:
        return video_id_match.group(1)
    raise ValueError("Invalid YouTube URL")

# Route to summarize a YouTube video transcript
@app.route('/summarize', methods=['POST'])
def summarize_video():
    try:
        data = request.get_json()
        video_url = data['url']
        max_words = data.get('max_words')  # Get the word limit from the user, if any

        # Extract the video ID from the URL
        video_id = extract_video_id(video_url)
        
        # Retrieve the transcript
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        
        # Combine all transcript parts into a single string
        transcript = " ".join([item['text'] for item in transcript_list])

        # Generate the summary with the optional word limit, ensuring key points are prioritized
        summary = summarize_transcript_intelligently(transcript, max_words=max_words)
        
        return jsonify({"summary": summary})

    except Exception as e:
        return jsonify({"error": "Summarization failed", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
