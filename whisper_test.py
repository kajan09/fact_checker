import whisper

# video = sys.argv[1]        # to call like python transcribe.py test.mp4
video = "\test.mp4"

model = whisper.load_model("tiny.en")   # <tiny> multi language


# Whisper will call ffmpeg internally – no tmp files needed
result = model.transcribe(video, fp16=True)  # fp16 ⇒ GPU
print(result["text"])
