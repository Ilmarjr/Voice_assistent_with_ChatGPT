from pathlib import Path
import sys
import textwrap
import speech_recognition as sr
from openai import OpenAI
import keyboard
import pygame

API_KEY = "SUA CHAVE DA OPENAI"
client = OpenAI(api_key=API_KEY)
language = 'pt-BR'
rec = sr.Recognizer()
AUDIO_FILE_PATH = Path(__file__).parent / "audios" / "output.mp3"


def play_audio(file_path):
    pygame.init()
    pygame.mixer.init()

    try:
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            if keyboard.is_pressed("space"):
                pygame.mixer.music.stop()
                print("\n##### Reprodução interrompida. #####")
                return
    except pygame.error as e:
        print(f"Erro ao reproduzir o áudio: {str(e)}")
    finally:
        pygame.quit()


def speech_to_text(audio):
    try:
        text = rec.recognize_google(audio, language=language)
        print(text)
        return text
    except:
        return ""


def text_to_speech(text, speed=1.0):
    response = client.audio.speech.create(
        model="tts-1",
        voice="echo",
        input=text,
        speed=speed
    )
    print(text)
    response.stream_to_file(AUDIO_FILE_PATH)
    play_audio(AUDIO_FILE_PATH)


def consult_chatGPT(query):
    query = f'Responda de maneira objetiva e com poucas palavras: {query}'
    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[
            {"role": "system", "content": "Você é um assistente pessoal de voz chamado Cleiton, extremamente "
                                          "habilidoso e inteligente em diversas áreas do conhecimento"},
            {"role": "system", "content": "Você é um assistente que está interessado em conversar sobre o tema das "
                                          "perguntas. Por isso sempre pergunte o que mais a pessoa gostaria de saber"
                                          " ou estimule ela a falar mais sobre..."},
            {"role": "user", "content": query}
        ]
    )
    print("Pensando...")
    chat_answer = response.choices[0].message.content
    return chat_answer


def make_a_question(text):
    response = consult_chatGPT(text)
    text_to_speech(response, 1.0)
    with sr.Microphone() as mic:
        rec.adjust_for_ambient_noise(mic)
        while True:
            try:
                    print("Ouvindo...")
                    audio = rec.listen(mic, timeout=5 , phrase_time_limit=10)
                    print("Processando")
                    text = speech_to_text(audio)
                    if "cleiton sair" in text.lower():
                        text_to_speech("Saindo...")
                        sys.exit()
                    elif "tchau cleiton" in text.lower():
                        text_to_speech("Tchau, estarei por aqui se precisar...")
                        break
                    if not text:
                        response = consult_chatGPT(text)
                        text_to_speech(response, 1.0)
                        print("Ouvindo...")
                        audio = rec.listen(mic)
                        print("Processando")
                        text = speech_to_text(audio)
                        if "cleiton sair" in text.lower():
                            text_to_speech("Saindo...")
                            sys.exit()
                        elif "tchau cleiton" in text.lower():
                            text_to_speech("Tchau, estarei por aqui se precisar...")
                            break
                    response = consult_chatGPT(text)
                    text_to_speech(response, 1.0)
            except sr.WaitTimeoutError:
                pass


# def menu():
#     menu = """\n
#     ================ MENU ================
#     [1]\tPerguntar
#     [2]\tSair
#     => """
#     return input(textwrap.dedent(menu))


def main():
    with sr.Microphone() as mic:
        rec.adjust_for_ambient_noise(mic)
        print("Cleiton Online")
        while True:
            try:
                    audio = rec.listen(mic, timeout=5, phrase_time_limit=10)
                    text = speech_to_text(audio)
                    if "e aí cleiton" in text.lower():
                        try:
                            make_a_question(text)
                        except Exception:
                            pass
                    elif "cleiton sair" in text.lower():
                        text_to_speech("Saindo...")
                        sys.exit()
            except sr.WaitTimeoutError:
                pass


# while True:
#     text_to_speech("Digite 1 para perguntar e digite 2 para sair.")
#     option = menu()
#
#     match option:
#         case "1":
#             try:
#                 make_a_question()
#             except Exception:
#                 pass
#         case "2":
#             text_to_speech("Saindo...")
#             break
#         case _:
#             print("")
#             text_to_speech("Opção inválida, tente novamente...")


main()
