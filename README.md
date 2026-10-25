# JARVIS – Voice AI Assistant

A Python voice assistant that listens to spoken commands, runs built-in actions, and falls back to an LLM (Llama 3.3 70B via Groq) for open-ended questions, with multi-turn conversation memory. Replies are spoken aloud.

## Features
- Speech recognition (Google Speech API) and text-to-speech (pyttsx3)
- Open-ended Q&A through Groq's `llama-3.3-70b-versatile` with conversation history
- Wikipedia summaries, Google search, open websites and desktop apps
- To-do list (add tasks, read them aloud, show desktop notification)
- Send email (Gmail SMTP) and WhatsApp messages
- Jokes, current time, random music playback

## Setup
1. Clone the repo and create a virtual environment:
   ```bash
   git clone https://github.com/AryanMishra100/Jarvis-AI-assistant.git
   cd Jarvis-AI-assistant
   python -m venv venv
   venv\Scripts\activate        # Windows
   # source venv/bin/activate   # macOS / Linux
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   If `PyAudio` fails to install on Windows, try `pip install pipwin` then `pipwin install pyaudio`.
3. Get a free API key from the [Groq Console](https://console.groq.com/).
4. Copy `.env.example` to `.env` and add your key:
   ```
   GROQ_API_KEY=your_key_here
   ```
5. Run:
   ```bash
   python main.py
   ```

## Example commands
| Say | What happens |
|---|---|
| "search wikipedia Python" | Reads a 2-sentence summary |
| "new task buy groceries" | Saves the task to `todo.txt` |
| "play music" | Opens a random track in the browser |
| "explain what an API is" | Answered by the LLM |
| "bye" | Exits |

## Notes
- Desktop-app launching (`open <app>`) uses the Windows Start menu via `pyautogui`.
- Email needs a Gmail **app password**, not your normal password.
- Secrets live in `.env`, which is git-ignored.

## Tech stack
Python, Groq API (Llama 3.3 70B), SpeechRecognition, pyttsx3, pyautogui, Wikipedia API, pywhatkit
