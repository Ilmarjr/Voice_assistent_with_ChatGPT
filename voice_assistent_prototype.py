from pathlib import Path
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
        print("Processando...")
        text = rec.recognize_google(audio, language=language)
        print(text)
        return text
    except:
        print('Falha no reconhecimento de voz')
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
            {"role": "system", "content": "Você é um assistente pessoal chamado Cleiton extremamente habilidoso e "
                                          "inteligente em diversas áreas do conhecimento"},
            {"role": "user", "content": query}
        ]
    )

    print("Pensando...")
    chat_answer = response.choices[0].message.content
    return chat_answer


def make_a_question():
    with sr.Microphone() as mic:
        try:
            rec.adjust_for_ambient_noise(mic)
            print("Ouvindo...")
            audio = rec.listen(mic, timeout=5, phrase_time_limit=10)
            text = speech_to_text(audio)
            if not text:
                response = consult_chatGPT(text)
                text_to_speech(response, 1.0)
                print("Ouvindo...")
                audio = rec.listen(mic)
                text = speech_to_text(audio)
            response = consult_chatGPT(text)
            text_to_speech(response, 1.0)
        except sr.WaitTimeoutError:
            pass


def menu():
    menu = """\n
    ================ MENU ================
    [1]\tPerguntar
    [2]\tSair
    => """
    return input(textwrap.dedent(menu))


def main():
    text_to_speech("\nComo posso ajudar?")
    while True:
        text_to_speech("Digite 1 para perguntar e digite 2 para sair.")
        option = menu()

        match option:
            case "1":
                try:
                    make_a_question()
                except Exception:
                    pass
            case "2":
                text_to_speech("Saindo...")
                break
            case _:
                print("")
                text_to_speech("Opção inválida, tente novamente...")


main()
