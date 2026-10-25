"""JARVIS - a voice assistant built with Python.

Speech in -> command routing / LLM (Groq) -> speech out.
Secrets are read from a .env file (see .env.example), never hardcoded.
"""
import datetime
import os
import random
import re
import smtplib
import webbrowser

import pyautogui
import pyjokes
import pyttsx3
import pywhatkit as pwk
import speech_recognition as sr
import wikipedia
from dotenv import load_dotenv
from groq import Groq
from plyer import notification

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found. Add it to your .env file (see .env.example).")

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
EMAIL_DEFAULT_RECIPIENT = os.getenv("EMAIL_DEFAULT_RECIPIENT")
WHATSAPP_NUMBER = os.getenv("WHATSAPP_NUMBER")  # format: +91XXXXXXXXXX

TODO_FILE = "todo.txt"
EXIT_PATTERN = re.compile(r"\b(bye|goodbye|exit|quit|go away|take rest)\b")

client = Groq(api_key=GROQ_API_KEY)
conversation_history = [
    {
        "role": "system",
        "content": "You are JARVIS, a helpful voice assistant. "
        "Keep answers concise and conversational since they will be spoken aloud.",
    }
]

engine = pyttsx3.init()  # picks the right speech driver for the OS
voices = engine.getProperty("voices")
if voices:
    engine.setProperty("voice", voices[0].id)


def speak(text):
    print(f"JARVIS: {text}")
    engine.say(text)
    engine.runAndWait()


def wish_me():
    hour = datetime.datetime.now().hour
    if hour < 12:
        speak("Good Morning!")
    elif hour < 18:
        speak("Good Afternoon!")
    else:
        speak("Good Evening!")
    speak("I am JARVIS. Please tell me how may I help you")


def take_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.pause_threshold = 1
        audio = recognizer.listen(source)
    try:
        print("Recognizing...")
        query = recognizer.recognize_google(audio, language="en-in")
        print(f"User said: {query}\n")
        return query.lower()
    except sr.UnknownValueError:
        speak("Sorry, I didn't catch that.")
    except sr.RequestError:
        speak("Speech service is unavailable.")
    return ""


def ask_groq(question):
    """Send the question to the LLM, keeping multi-turn conversation memory."""
    conversation_history.append({"role": "user", "content": question})
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=conversation_history,
            temperature=0.7,
            max_tokens=512,
        )
        reply = response.choices[0].message.content
        conversation_history.append({"role": "assistant", "content": reply})
        return reply
    except Exception as e:
        print(f"Groq error: {e}")
        conversation_history.pop()  # don't keep a question that got no answer
        return "Sorry, I had trouble answering that."


def send_email(to, content):
    if not (EMAIL_ADDRESS and EMAIL_APP_PASSWORD):
        raise RuntimeError("Email credentials missing in .env")
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_APP_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, to, content)


def search_wikipedia(query):
    topic = query.replace("search wikipedia", "").strip()
    if not topic:
        speak("What should I search for?")
        return
    speak("Searching Wikipedia...")
    try:
        result = wikipedia.summary(topic, sentences=2)
        speak("According to Wikipedia")
        speak(result)
    except wikipedia.exceptions.DisambiguationError:
        speak("That topic is ambiguous. Please be more specific.")
    except wikipedia.exceptions.PageError:
        speak("I couldn't find a page for that.")


def play_music():
    speak("Playing music")
    tracks = [
        "https://www.youtube.com/watch?v=yJg-Y5byMMw",
        "https://www.youtube.com/watch?v=TW9d8vYrVFQ",
        "https://www.youtube.com/watch?v=U6cPjurCOmQ",
    ]
    webbrowser.open(random.choice(tracks))


def add_task(query):
    task = query.replace("new task", "").strip()
    if task:
        speak(f"Adding task: {task}")
        with open(TODO_FILE, "a") as f:
            f.write(task + "\n")


def read_tasks():
    if not os.path.exists(TODO_FILE):
        return ""
    with open(TODO_FILE) as f:
        return f.read().strip()


def handle_email():
    if not EMAIL_DEFAULT_RECIPIENT:
        speak("No default recipient is set in the environment file.")
        return
    try:
        speak("What should I say?")
        content = take_command()
        if content:
            send_email(EMAIL_DEFAULT_RECIPIENT, content)
            speak("Email has been sent!")
    except Exception as e:
        print(f"Email error: {e}")
        speak("Sorry, I couldn't send the email.")


def handle_whatsapp():
    if not WHATSAPP_NUMBER:
        speak("No WhatsApp number is set in the environment file.")
        return
    speak("What should I say?")
    message = take_command()
    if message:
        pwk.sendwhatmsg_instantly(WHATSAPP_NUMBER, message)
        speak("Message sent")


def open_app(query):
    name = query.replace("jarvis", "").replace("open", "").strip()
    if not name:
        return
    pyautogui.press("super")  # Windows start menu search
    pyautogui.typewrite(name)
    pyautogui.sleep(2)
    pyautogui.press("enter")


def process(query):
    """Route a command. Returns False when the user wants to quit."""
    if EXIT_PATTERN.search(query):
        speak("Thank you Sir, please let me know if you need anything")
        return False

    if "who are you" in query:
        speak("I am a Virtual Assistant created by Aryan")
    elif "search wikipedia" in query:
        search_wikipedia(query)
    elif "open youtube" in query:
        webbrowser.open("https://youtube.com")
    elif "open google" in query:
        webbrowser.open("https://google.com")
    elif "open stackoverflow" in query:
        webbrowser.open("https://stackoverflow.com")
    elif "open" in query:
        open_app(query)
    elif "search google" in query:
        term = query.replace("jarvis", "").replace("search google", "").strip()
        webbrowser.open("https://www.google.com/search?q=" + term)
    elif "play music" in query:
        play_music()
    elif "stop music" in query:
        pyautogui.press("playpause")
    elif "the time" in query:
        speak(f"Sir, the time is {datetime.datetime.now().strftime('%H:%M:%S')}")
    elif "send email" in query:
        handle_email()
    elif "send whatsapp" in query:
        handle_whatsapp()
    elif "new task" in query:
        add_task(query)
    elif "speak task" in query:
        tasks = read_tasks()
        speak("Work we have to do today is: " + tasks if tasks else "You have no tasks.")
    elif "show work" in query:
        tasks = read_tasks()
        notification.notify(title="Today's work", message=tasks or "No tasks yet.")
    elif "joke" in query:
        speak(pyjokes.get_joke(language="en", category="neutral"))
    elif query.strip():
        speak(ask_groq(query))  # anything else goes to the LLM
    return True


if __name__ == "__main__":
    wish_me()
    while process(take_command()):
        pass
