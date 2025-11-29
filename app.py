from flask import Flask, jsonify, request, render_template
import yt_dlp
import urllib.parse
import os

app = Flask(__name__, template_folder='templates')

@app.route('/')
def index():
    """Main page with instructions"""
    return render_template('index.html')

@app.route('/download', methods=['GET'])
def download_video():
    """
    Extract video information from a YouTube URL.
    
    Query Parameters:
        url (str): YouTube video URL
        
    Returns:
        JSON: Video information including available formats
    """
    # Get the URL from the query parameters
    video_url = request.args.get('url')
    
    if not video_url:
        return jsonify({'error': 'No URL provided. Use /download?url=[youtube-url]'}), 400
    
    # Decode URL in case it's encoded
    try:
        video_url = urllib.parse.unquote(video_url)
    except:
        pass  # If decoding fails, use the original URL
    
    try:
        # Options for yt_dlp
        ydl_opts = {
            'quiet': True,                     # No console noise
            'skip_download': True,             # Don't actually download
            'forceurl': True,                  # Show final video URLs
            'forcejson': True,                 # Return info as JSON
            'noplaylist': True,                # Don't auto-download playlists
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            
            # Prepare the response
            response = {
                'title': info['title'],
                'channel': info.get('uploader', 'Unknown'),
                'duration': info['duration'],
                'thumbnail': info.get('thumbnail', ''),
                'description': info.get('description', ''),
                'upload_date': info.get('upload_date', ''),
                'view_count': info.get('view_count', 0),
                'like_count': info.get('like_count', 0),
                'formats': []
            }
            
            # Add available formats
            for fmt in info['formats']:
                url = fmt.get('url')
                if url:  # skip entries without direct URL
                    format_info = {
                        'format_id': fmt['format_id'],
                        'format_note': fmt.get('format_note', ''),
                        'resolution': fmt.get('resolution', 'N/A'),
                        'extension': fmt.get('ext', 'N/A'),
                        'filesize_approx': fmt.get('filesize_approx', 'N/A'),
                        'url': url,
                        'vcodec': fmt.get('vcodec', 'N/A'),
                        'acodec': fmt.get('acodec', 'N/A'),
                        'fps': fmt.get('fps', 'N/A'),
                    }
                    response['formats'].append(format_info)
            
            return jsonify(response)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # For local development
    app.run(debug=True)
else:
    # For production deployment
    app.run(host='127.0.0.1', port=int(os.environ.get('PORT', 5000)))