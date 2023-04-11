from dotenv import load_dotenv
import os
import openai
import time
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_cors import CORS
import requests
import logging
import re
import html
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.consumer.storage.sqla import SQLAlchemyStorage, OAuthConsumerMixin
from flask_sqlalchemy import SQLAlchemy
from logging.handlers import RotatingFileHandler
from youtube_transcript_api import YouTubeTranscriptApi


def truncate(content, max_length):
    if len(content) > max_length:
        return content[:max_length] + "..."
    return content


load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_handler = RotatingFileHandler(
    '/var/www/tubeask/tubeask.log', maxBytes=100000, backupCount=3)
log_handler.setFormatter(log_formatter)
log_handler.setLevel(logging.DEBUG)

app.logger.addHandler(log_handler)
app.logger.setLevel(logging.DEBUG)

db = SQLAlchemy(app)
login_manager = LoginManager(app)

app.config["GOOGLE_OAUTH_CLIENT_ID"] = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
app.config["GOOGLE_OAUTH_CLIENT_SECRET"] = os.getenv(
    "GOOGLE_OAUTH_CLIENT_SECRET")


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.String, nullable=False, unique=True)
    name = db.Column(db.String, nullable=False)
    oauth = db.relationship("OAuth", uselist=False, back_populates="user")


class OAuth(OAuthConsumerMixin, db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = db.relationship(User, back_populates="oauth")


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


google_bp = make_google_blueprint(
    client_id=app.config["GOOGLE_OAUTH_CLIENT_ID"],
    client_secret=app.config["GOOGLE_OAUTH_CLIENT_SECRET"],
    scope=["https://www.googleapis.com/auth/userinfo.email",
           "https://www.googleapis.com/auth/userinfo.profile", "openid"],
    storage=SQLAlchemyStorage(OAuth, db.session),
)
app.register_blueprint(google_bp, url_prefix="/login")


@app.route('/login')
def login():
    if not google.authorized:
        return redirect(url_for("google.login"))

    if google.token['expires_at'] <= time.time():
        if 'refresh_token' in google.token:
            resp = google.get("/oauth2/v4/token", params={
                'grant_type': 'refresh_token',
                'client_id': app.config["GOOGLE_OAUTH_CLIENT_ID"],
                'client_secret': app.config["GOOGLE_OAUTH_CLIENT_SECRET"],
                'refresh_token': google.token['refresh_token']
            })
            token = resp.json()
            google.token = token
        else:
            return redirect(url_for("google.login"))

    resp = google.get("/oauth2/v2/userinfo")
    if resp.ok:
        user_data = resp.json()
        google_id = user_data['id']
        name = user_data['name']
        user = User.query.filter_by(google_id=google_id).first()
        if not user:
            user = User(google_id=google_id, name=name)
            db.session.add(user)
            db.session.commit()
        login_user(user)
        return redirect(url_for('index'))
    flash("Failed to login with Google.", category="error")
    return redirect(url_for('index'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


openai.api_key = OPENAI_API_KEY


@app.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('index.html', user_name=current_user.name)
    else:
        return render_template('index.html')


def extract_video_id(video_url):
    patterns = [
        r'(?:https?:\/\/)?(?:www\.|m\.)?(?:youtube\.com\/(?:watch\?v=|embed\/)|youtu\.be\/)([\w-]{11})',
        r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/shorts\/)([\w-]{11})(?:\?.*)?'
    ]

    for pattern in patterns:
        match = re.match(pattern, video_url)
        if match:
            return match.group(1)

    return None


def get_video_transcript(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        transcript = transcript_list.find_transcript(['en'])
        transcript_data = transcript.fetch()
        full_transcript = " ".join([entry['text']
                                   for entry in transcript_data])
        return full_transcript
    except Exception as e:
        app.logger.error(f"Error fetching transcript: {str(e)}")
        return None


@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.json
    video_url = data.get('video_url')
    question = data.get('question')

    app.logger.debug(f"Received video_url: {video_url}")

    if not video_url or not question:
        return jsonify({"error": "Missing video URL or question"}), 400

    video_id = extract_video_id(video_url)

    if not video_id:
        return jsonify({"error": "Invalid video URL format"}), 400

    video_info_url = f"https://www.googleapis.com/youtube/v3/videos?id={video_id}&part=snippet,statistics,contentDetails&key={YOUTUBE_API_KEY}"
    response = requests.get(video_info_url)
    video_info = response.json()

    video_info_url = f"https://www.googleapis.com/youtube/v3/videos?id={video_id}&part=snippet,statistics,contentDetails&key={YOUTUBE_API_KEY}"
    response = requests.get(video_info_url)
    video_info = response.json()

    title = video_info['items'][0]['snippet']['title']
    description = video_info['items'][0]['snippet']['description']
    channel_title = video_info['items'][0]['snippet']['channelTitle']
    published_at = video_info['items'][0]['snippet']['publishedAt']

    statistics = video_info['items'][0]['statistics']
    view_count = statistics.get('viewCount', 'N/A')
    like_count = statistics.get('likeCount', 'N/A')
    dislike_count = statistics.get('dislikeCount', 'N/A')
    comment_count = statistics.get('commentCount', 'N/A')

    content_details = video_info['items'][0]['contentDetails']
    duration = content_details.get('duration', 'N/A')

    channel_id = video_info['items'][0]['snippet']['channelId']
    channel_info_url = f"https://www.googleapis.com/youtube/v3/channels?id={channel_id}&part=statistics&key={YOUTUBE_API_KEY}"
    response = requests.get(channel_info_url)
    channel_info = response.json()
    subscriber_count = channel_info['items'][0]['statistics'].get(
        'subscriberCount', 'N/A')

    transcript = get_video_transcript(video_id)

    system_message = f"This is a video titled '{truncate(title, 25)}' by '{channel_title}' with the description: '{truncate(description, 160)}'. The video was published on {published_at} and has {view_count} views, {like_count} likes, {dislike_count} dislikes, and {comment_count} comments. The video duration is {duration} and the channel has {subscriber_count} subscribers."
    if transcript:
        system_message += f" The video has the following transcript: '{truncate(transcript, 16030)}'"

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": question}
        ]
    )

    answer = completion.choices[0].message['content']
    tokens_used = completion['usage']['total_tokens']

    app.logger.info(
        f"YouTube video URL: {video_url} || Question: {question} || AI Response: {answer} || Tokens used: {tokens_used}")

    return jsonify({"answer": answer})


@app.before_first_request
def create_tables():
    db.create_all()


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
