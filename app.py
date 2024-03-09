from flask import Flask, request, send_file
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
import io

app = Flask(__name__)
CORS(app)

# Función para obtener el ID del video de YouTube a partir de la URL
def get_video_id(url):
    parsed_url = urlparse(url)
    if parsed_url.netloc == 'www.youtube.com' or parsed_url.netloc == 'youtube.com':
        if parsed_url.path.startswith('/watch'):
            video_id = parse_qs(parsed_url.query)['v'][0]
            return video_id
    else:
        raise ValueError('La URL proporcionada no es una URL válida de YouTube.')

# Función para generar subtítulos en formato .srt
def generate_srt(video_id):
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    srt_data = io.BytesIO()
    srt_lines = []
    for count, caption in enumerate(transcript, start=1):
        start_time = format_timestamp(caption['start'])
        end_time = format_timestamp(caption['start'] + caption['duration'])
        text = caption['text'].replace('\n', ' ')
        srt_lines.append(f"{count}\n{start_time} --> {end_time}\n{text}\n\n")
    srt_data.write(''.join(srt_lines).encode('utf-8'))
    srt_data.seek(0)
    return srt_data

# Función para formatear el tiempo en formato hh:mm:ss,ms
def format_timestamp(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    milliseconds = (seconds - int(seconds)) * 1000
    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d},{int(milliseconds):03d}"

@app.route('/', methods=['GET'])
def get_subtitles():
    video_url = request.args.get('url')
    if not video_url:
        return 'Debe proporcionar una URL de video de YouTube', 400

    try:
        video_id = get_video_id(video_url)
        srt_data = generate_srt(video_id)
        return send_file(srt_data, download_name='subtitulos.srt', as_attachment=True)
    except Exception as e:
        return str(e), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)