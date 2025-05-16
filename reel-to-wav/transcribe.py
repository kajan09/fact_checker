import instaloader
import moviepy.editor as mp
import os

def download_reel(url):
    try:
        loader = instaloader.Instaloader()
        loader.download_post(instaloader.Post.from_shortcode(loader.context, url.split('/')[-2]), target='reel')
        video_file = [f for f in os.listdir('reel') if f.endswith('.mp4')][0]
        return os.path.join('reel', video_file)
    except Exception as e:
        print(f"Error downloading reel: {e}")
        return None

# Function to convert video to audio
def convert_video_to_audio(video_file):
    clip = mp.VideoFileClip(video_file)
    clip.audio.write_audiofile("audio.wav")
    return "audio.wav"

url = input("Enter Reel URL:")

if url:
    print("Downloading Reel...")
    video_file = download_reel(url)
        
    if video_file:
        print("Converting video to audio...")
        audio_file = convert_video_to_audio(video_file)
            # Clean up files
            # os.remove(video_file)
            # os.remove(audio_file)
    else:
        print("Failed to download the reel.")
else:
    print("Please enter a valid Reel URL.")
