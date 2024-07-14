from openai import OpenAI
client = OpenAI()

#File uploads are currently limited to 25 MB.
#The following input file types are supported: mp3, mp4, mpeg, mpga, m4a, wav, and webm.

audio_file= open("./audio/e.mp3", "rb")

response = client.audio.translations.create(
  model="whisper-1", 
  file=audio_file
  )

data=response.text

f = open("./output/text/text.txt", "w",encoding="utf-8")
f.write(data)
f.close()
