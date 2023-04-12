import sys
from youtube_transcript_api import YouTubeTranscriptApi


def main(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        transcript = transcript_list.find_transcript(['en'])
        transcript_data = transcript.fetch()
        full_transcript = " ".join([entry['text']
                                    for entry in transcript_data])
        return full_transcript
    except Exception as e:
        return None


if __name__ == '__main__':
    print(main(sys.argv[1]))
