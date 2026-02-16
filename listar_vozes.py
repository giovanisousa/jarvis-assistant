import pyttsx3

engine = pyttsx3.init()
voices = engine.getProperty('voices')

print("--- VOZES INSTALADAS NO SEU WINDOWS ---")
for voice in voices:
    print(f"ID: {voice.id}")
    print(f"Nome: {voice.name}")
    print("-" * 30)