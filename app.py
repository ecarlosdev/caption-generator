from flask import Flask, Response, request, send_file, stream_with_context
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import SRTFormatter
from urllib.parse import urlparse, parse_qs
import io
import re

app = Flask(__name__)
CORS(app)

def remove_tags(transcript):
    new_transcript = []
    for i in range(len(transcript)):
        if re.search(r'\[.*?\]', transcript[i]['text']):
            continue
        new_transcript.append(transcript[i])
    return new_transcript

def write_to_srt_file(strFormatedString):
    srt_file = io.BytesIO()
    srt_file.write(strFormatedString.encode('utf-8'))
    srt_file.seek(0)
    return srt_file

@app.route('/', methods=['GET'])
def get_subtitles():
    video_id = request.args.get('video_id')
    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
    try:
        transcript = transcript_list.find_generated_transcript(['en', 'es']).fetch()
        if not transcript:
            return 'No transcript found', 404
        formatter = SRTFormatter()
        strFormatedString = formatter.format_transcript(remove_tags(transcript))
        srt_file = write_to_srt_file(strFormatedString)
        return Response(stream_with_context(srt_file), content_type='text/plain', direct_passthrough=True)
    except Exception as e:
        print(e)
        return 'Internal Server Error', 500
        
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)