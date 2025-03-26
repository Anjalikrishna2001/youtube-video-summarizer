from urllib.parse import parse_qs, urlparse
from flask import Flask, request, jsonify, render_template
from pytube import YouTube
import whisper
from transformers import pipeline
import os

app = Flask(__name__)

# Load Whisper Model
whisper_model = whisper.load_model("base")

# Load distilBART Summarizer
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

# Function to extract and transcribe audio
def extract_audio_transcribe(youtube_url):
    try:
        yt = YouTube(youtube_url)
        video = yt.streams.filter(only_audio=True).first()
        audio_file = "audio.mp4"
        
        # Download audio
        video.download(filename=audio_file)
        
        # Transcribe
        result = whisper_model.transcribe(audio_file)

        # Cleanup
        os.remove(audio_file)

        return result["text"]
    except Exception as e:
        return f"Error: {str(e)}"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/summarize", methods=["POST"])
def summarize():
    try:
        data = request.get_json(force=True)  
        youtube_url = data.get("youtube_url", "").strip()

        if not youtube_url:
            return jsonify({"error": "No YouTube URL provided"}), 400

        # ✅ Extract video ID from URL
        parsed_url = urlparse(youtube_url)
        if "youtube.com" in parsed_url.netloc or "youtu.be" in parsed_url.netloc:
            video_id = parse_qs(parsed_url.query).get("v", [None])[0] or parsed_url.path.split("/")[-1]
            clean_url = f"https://www.youtube.com/watch?v={video_id}"
        else:
            return jsonify({"error": "Invalid YouTube URL"}), 400

        print("🎥 Processing YouTube URL:", clean_url)

        # Extract transcript
        transcript = extract_audio_transcribe(youtube_url)
        print("✅ Transcript:", transcript[:200])  # Print first 200 characters

        if "Error" in transcript:
            print("❌ Transcription failed!")
            return jsonify({"error": transcript}), 500

        # Summarize
        print("⏳ Summarizing...")
        summary = summarizer(transcript, max_length=150, min_length=50, do_sample=False)
        print("✅ Summary:", summary[0]["summary_text"])

        return jsonify({"summary": summary[0]["summary_text"]})

    except Exception as e:
        print("🔥 SERVER ERROR:", str(e))  # Debugging
        return jsonify({"error": f"Server error: {str(e)}"}), 500
        

if __name__ == "__main__":
    app.run(debug=True)


