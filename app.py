from flask import Flask, request, send_file
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import SRTFormatter
from urllib.parse import urlparse, parse_qs
import io

app = Flask(__name__)
CORS(app)

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
        transcript = transcript_list.find_generated_transcript(['en']).fetch()
        if not transcript:
            return 'No transcript found', 404
        formatter = SRTFormatter()
        strFormatedString = formatter.format_transcript(transcript)
        srt_file = write_to_srt_file(strFormatedString)
        return send_file(srt_file, download_name=f'{video_id}_subtitles.srt')
    except Exception as e:
        return 'Internal Server Error', 500
        
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)