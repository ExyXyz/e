from flask import Flask, request, send_file, jsonify, send_from_directory
from hentai import Hentai, Format
from PIL import Image
from io import BytesIO
import requests
from concurrent.futures import ThreadPoolExecutor
from pytubefix import YouTube
from pytubefix.cli import on_progress

app = Flask(__name__)

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/api/nhentai', methods=['GET'])
def get_hentai_info():
    doujin_id = request.args.get('id', type=int)
    
    if doujin_id is None:
        return jsonify({"error": "No doujin ID provided | Mana doujin ID nya?"}), 400
    
    try:
        doujin = Hentai(doujin_id)

        if not Hentai.exists(doujin.id):
            return jsonify({"error": "Doujin not found | Gak nemu doujin nya"}), 404
        
        doujin_info = {
            "1_author": "Exy",
            "2_title": doujin.title(Format.Pretty),
            "3_artist": [{"id": artist.id, "name": artist.name, "url": artist.url} for artist in doujin.artist],
            "4_tags": [tag.name for tag in doujin.tag],
            "5_upload_date": doujin.upload_date.isoformat(),
            "6_image_urls": doujin.image_urls
        }
        
        return jsonify(doujin_info)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def download_image(url):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    return img.convert('RGB')

@app.route('/api/nhentaipdf', methods=['GET'])
def get_hentai_pdf():
    doujin_id = request.args.get('id', type=int)
    
    if doujin_id is None:
        return jsonify({"error": "No doujin ID provided | Mana doujin ID nya?"}), 400
    
    try:
        doujin = Hentai(doujin_id)

        if not Hentai.exists(doujin.id):
            return jsonify({"error": "Doujin not found | Gak nemu doujin nya"}), 404
        
        with ThreadPoolExecutor() as executor:
            images = list(executor.map(download_image, doujin.image_urls))
        
        pdf_buffer = BytesIO()
        images[0].save(pdf_buffer, format="PDF", save_all=True, append_images=images[1:])
        pdf_buffer.seek(0)
        
        pdf_filename = f"{doujin.title(Format.Pretty)}.pdf"
        return send_file(pdf_buffer, as_attachment=True, download_name=pdf_filename, mimetype='application/pdf')
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/tiktok', methods=['GET'])
def get_tiktok_info():
    url = request.args.get('url')
    
    if not url:
        return jsonify({"error": "No TikTok URL provided | Link TikTok nya mana njir"}), 400

    try:
        encoded_url = requests.utils.quote(url)
        response = requests.get(f"https://api.agatz.xyz/api/tiktok?url={encoded_url}")

        if response.status_code != 200:
            return jsonify({"error": f"API request failed with status code {response.status_code}"}), 500

        data = response.json()
        
        if data.get('status') != 200:
            error_message = data.get('error', 'Unknown API error')
            return jsonify({"error": f"Failed to fetch TikTok data | Gagal saat memproses TikTok data"}), 500
        
        required_fields = ["title", "taken_at", "region", "id", "duration", "cover", "data", "music_info", "stats", "author"]
        if not all(field in data["data"] for field in required_fields):
            return jsonify({"error": "Something is missing | Ada yang hilang"}), 500
        
        tiktok_info = {
            "3_title": data["data"]["title"],
            "4_taken_at": data["data"]["taken_at"],
            "5_region": data["data"]["region"],
            "6_id": data["data"]["id"],
            "7_duration": data["data"]["duration"],
            "8_cover": data["data"]["cover"],
            "9_sizes": {
                "watermark": data["data"].get("size_wm", "N/A"),
                "nowatermark": data["data"].get("size_nowm", "N/A"),
                "nowatermark_hd": data["data"].get("size_nowm_hd", "N/A")
            },
            "10_video_urls": {
                "watermark": next((item["url"] for item in data["data"]["data"] if item["type"] == "watermark"), "N/A"),
                "nowatermark": next((item["url"] for item in data["data"]["data"] if item["type"] == "nowatermark"), "N/A"),
                "nowatermark_hd": next((item["url"] for item in data["data"]["data"] if item["type"] == "nowatermark_hd"), "N/A")
            },
            "11_music_info": data["data"].get("music_info", {}),
            "12_stats": data["data"].get("stats", {}),
            "2_author": data["data"].get("author", {}),
            "1_author": "Exy"
        }

        return jsonify(tiktok_info)

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Request exception occurred: {str(e)}"}), 500
    except KeyError as e:
        return jsonify({"error": f"Missing expected data in API response: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error occurred: {str(e)}"}), 500

@app.route('/api/youtube', methods=['GET'])
def get_youtube_info():
    url = request.args.get('url')
    
    if not url:
        return jsonify({"error": "No YouTube URL provided | Link YouTube nya mana?"}), 400

    try:
        yt = YouTube(url, use_oauth=True, allow_oauth_cache=True, on_progress_callback=on_progress)

        video_info = {
            "1_title": yt.title,
            "2_duration": yt.length,  
            "3_author": yt.author,  
            "4_thumbnail": yt.thumbnail_url,  
            "5_streams": [
                {
                    "1_itag": stream.itag,
                    "2_resolution": stream.resolution,
                    "3_type": stream.type,
                    "4_download_url": stream.url
                }
                for stream in yt.streams
            ]
        }
        
        return jsonify(video_info)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/instagram', methods=['GET'])
def get_instagram_info():
    url = request.args.get('url')
    
    if not url:
        return jsonify({"error": "No Instagram URL provided | Link Instagram nya mana?"}), 400

    try:
        api_url = "https://instagram-media-downloader-api-fast-2024.p.rapidapi.com/instagram"
        querystring = {"url": url}
        
        headers = {
            "x-rapidapi-key": "d3e82fd276mshacd2537a6ca419bp1d9d60jsnf5a12747e966",
            "x-rapidapi-host": "instagram-media-downloader-api-fast-2024.p.rapidapi.com"
        }
        
        response = requests.get(api_url, headers=headers, params=querystring)

        if response.status_code != 200:
            return jsonify({"error": f"API request failed with status code {response.status_code}"}), 500

        data = response.json()
        
        if data.get('ok') is not True:
            return jsonify({"error": "Failed to fetch Instagram data | Gagal saat memproses Instagram data"}), 500
        
        instagram_info = {
            "1_author": "Exy",
            "2_download link": data.get("result")
        }

        return jsonify(instagram_info)

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Request exception occurred: {str(e)}"}), 500
    except KeyError as e:
        return jsonify({"error": f"Missing expected data in API response: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=555)
