from dotenv import load_dotenv
import os
import openai
import io
import zipfile


load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_podcast_audio(script_text, voice="coral", model="tts-1"):
  response = openai.audio.speech.create(
    model=model,
    voice=voice,
    input=script_text
  )

  return response.content

def create_zip(script, audio):
  zip_buffer = io.BytesIO()
  with zipfile.ZipFile(zip_buffer, "w") as zf:
    zf.writestr("podcast script.txt", script)
    zf.writestr("podcast_audio.mp3", audio)
  zip_buffer.seek(0)
  return zip_buffer