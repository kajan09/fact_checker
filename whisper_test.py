import whisper
import sys
import time
# pip install -U openai-whisper

# video = sys.argv[1]        # to call like python transcribe.py test.mp4
video = "reel-to-wav/audio.wav"

model = whisper.load_model("tiny")   # <tiny> multi language

# Whisper will call ffmpeg internally – no tmp files needed
result = model.transcribe(video, fp16=True)  # fp16 ⇒ GPU
print(result["text"])
