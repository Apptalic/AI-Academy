from dotenv import load_dotenv
import os
from spitch import Spitch
import zipfile
import io

load_dotenv()

# Spitch config
key = os.getenv("SPICTH_API_KEY")

os.environ['SPITCH_API_KEY'] = key
client = Spitch()

def generate_podcast_audio(script_text, language="en", voice="favour", fmt="mp3"):
  response = client.speech.generate(
    text=script_text,
    language=language,
    voice=voice,
    format=fmt
  )

  if hasattr(response, "read"):
    audio = response.read()
  elif hasattr(response, "content"):
    audio = response.content
  else:
    audio = response

  return audio


def create_zip(script, audio):
  zip_buffer = io.BytesIO()
  with zipfile.ZipFile(zip_buffer, "w") as zf:
    zf.writestr("podcast script.txt", script)
    zf.writestr("podcast_audio.mp3", audio)
  zip_buffer.seek(0)
  return zip_buffer
