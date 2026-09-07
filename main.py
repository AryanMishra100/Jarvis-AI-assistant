import pyttsx3
import speech_recognition as sr
import random
import datetime
import pyautogui
import wikipedia
import webbrowser
from plyer import notification
import pywhatkit as pwk
import smtplib
import pyjokes
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    raise ValueError("GROQ_API_KEY not found. Make sure it's in your .env file.")

client = Groq(api_key=groq_api_key)

conversation_history = [
    {"role": "system", "content": "You are JARVIS, a helpful voice assistant. Keep answers concise and conversational since they will be spoken aloud."}
]

engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)


def speak(audio):
    engine.say(audio)
    engine.runAndWait()


def wishMe():
    hour = int(datetime.datetime.now().hour)
    if hour>=0 and hour<12:
        speak("Good Morning!")

    elif hour>=12 and hour<18:
        speak("Good Afternoon!")

    else:
        speak("Good Evening!")

    speak("I am JARVIS. Please tell me how may I help you")

def takeCommand():

    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-in')
        print(f"User said: {query}\n")


    except sr.UnknownValueError:

        speak("Sorry, I didn't catch that.")

        return ""


    except sr.RequestError:

        speak("Speech service is unavailable.")

        return ""
    return query

def sendEmail(to, content):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login('user@gmail.com', 'password')
    server.sendmail('user@gmail.com', to, content)
    server.close()

def ask_groq(question):
    global conversation_history
    try:
        conversation_history.append({"role": "user", "content": question})

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
        print(e)
        return "Sorry, I had trouble answering that."

if __name__ == "__main__":
    wishMe()
    while True:
        query = takeCommand().lower()

        if "who are you" in query:
            speak("I am a Virtual Assistant created by Aaryan ")

        elif 'search wikipedia' in query:
            speak('Searching Wikipedia...')
            query = query.replace("search wikipedia", "")
            results = wikipedia.summary(query, sentences=2)
            speak("According to Wikipedia")
            print(results)
            speak(results)

        elif 'open youtube' in query:
             webbrowser.open("youtube.com")

        elif 'open google' in query:
             webbrowser.open("google.com")

        elif 'open stackoverflow' in query:
            webbrowser.open("stackoverflow.com")

        elif "open" in query:
            query = query.replace("jarvis ", "")
            query = query.replace("open", "")
            pyautogui.press("super")
            pyautogui.typewrite(query)
            pyautogui.sleep(2)
            pyautogui.press("enter")

        elif "search google" in query:
            query = query.replace("jarvis ", "")
            query = query.replace("search google ", "")
            webbrowser.open("https://www.google.com/search?q=" + query)

        elif 'play music' in query:
            speak("Playing music")
            song = random.randint(1, 3)
            if song == 1:
                webbrowser.open("https://www.youtube.com/watch?v=yJg-Y5byMMw&pp=ygUUY29weXJpZ2h0IGZyZWUgbXVzaWM%3D")
            elif song == 2:
                webbrowser.open("https://www.youtube.com/watch?v=TW9d8vYrVFQ&pp=ygUUY29weXJpZ2h0IGZyZWUgbXVzaWM%3D")
            elif song == 3:
                webbrowser.open("https://www.youtube.com/watch?v=U6cPjurCOmQ&pp=ygUUY29weXJpZ2h0IGZyZWUgbXVzaWM%3D")

        elif 'stop music' in query:
            pyautogui.click()

        elif 'the time' in query:
            strTime = datetime.datetime.now().strftime("%H:%M:%S")
            speak(f"Sir, the time is {strTime}")

        elif 'send email' in query:
            try:
                speak("What should I say?")
                content = takeCommand()
                to = "xyz@gmail.com"
                sendEmail(to, content)
                speak("Email has been sent!")

            except Exception as e:
                print(e)
                speak("")

        elif "send whatsapp" in query:
            pwk.sendwhatmsg_instantly("+91xxxxxxxxxx","hi, how are you")
            speak('message sent')

        elif "new task" in query:
            task = query.replace("new task", "")
            task = task.strip()
            if task != "":
                speak("Adding task : "+ task)
                with open ("todo.txt", "a") as file:
                    file.write(task + "\n")

        elif "speak task" in query:
            with open("todo.txt", "r") as file:
                speak("Work we have to do today is : " + file.read())

        elif "show work" in query:
            with open("todo.txt", "r") as file:
                tasks = file.read()
            notification.notify(
                title="Today's work",
                message=tasks
            )

        elif "joke" in query:
            content = pyjokes.get_joke(language="en", category="neutral")
            speak (content)

        elif 'rest' or 'bye' or 'go away' in query:
            speak("Thankyou Sir, please let me know if you need anything")
            break

        else:
            if query.strip() != "":
                answer = ask_groq(query)
                print(answer)
                speak(answer)