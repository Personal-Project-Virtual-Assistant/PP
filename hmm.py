# these are all of my imports, they're modules which help with executing certain function and specific things you can't-
# - do with normal code

from __future__ import print_function
import os.path
import os
import datetime
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pyttsx3
import speech_recognition as sr
import pytz
import subprocess
import tkinter as tk

# the following strings and variables are at the top for formatting and easy access, they're used later in the program

API = ['https://www.googleapis.com/auth/calendar.readonly']
MONTHS = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november",
          "december"]
DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
DAY_EXTENTIONS = ["th", "nd", "rd", "st"]

HIGH = 300
WIDE = 400

# the speech and listen functions I've created are the building blocks of the program, basically they use some of the
# imported modules above to produce speech and process what the user is saying


def speech(texxt):
    engine = pyttsx3.init()
    engine.say(texxt)
    engine.runAndWait()


def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
        said = ""

        try:
            said = r.recognize_google(audio)
            print(said)
        except Exception as e:
            print("Exception: " + str(e))

    return said.lower()

# the function below authenticates the user's google account to access their calender through the API
# this function also uses other files in the program such as credentials.json which accesses the API and
# token.pickle which stores the user's information, so there is no need to constantly use this function


def authenticate_google():

    credentials = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            credentials = pickle.load(token)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', API)
            credentials = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(credentials, token)

    service = build('calendar', 'v3', credentials=credentials)

    return service

# This function tells the program how to find a date through the API and what it should speak when it finds it


def eventts(day, service):

    # Call the Calendar API

    datte = datetime.datetime.combine(day, datetime.datetime.min.time())
    end_date = datetime.datetime.combine(day, datetime.datetime.max.time())
    utc = pytz.UTC
    datte = datte.astimezone(utc)
    end_date = end_date.astimezone(utc)

    events_result = service.events().list(calendarId='primary', timeMin=datte.isoformat(), timeMax=end_date.isoformat(),
                                          singleEvents=True, orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        speech('No upcoming events found.')
    else:
        speech("You have {len(events)} events on this day.")

        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])
            start_time = str(start.split("T")[1].split("-")[0])
            if int(start_time.split(":")[0]) < 12:
                start_time = start_time + "am"
            else:
                start_time = str(int(start_time.split(":")[0]) - 12) + start_time.split(":")[1]
                start_time = start_time + "pm"

            speech(event["summary"] + " at " + start_time)

# this function also tries to find the specific day etc. Very complicated.


def datttte(texxxt):
    texxxt = texxxt.lower()
    today = datetime.date.today()

    if texxxt.count("today") > 0:
        return today

    day = -1
    day_of_week = -1
    month = -1
    year = today.year

    for word in texxxt.split():
        if word in MONTHS:
            month = MONTHS.index(word) + 1
        elif word in DAYS:
            day_of_week = DAYS.index(word)
        elif word.isdigit():
            day = int(word)
        else:
            for ext in DAY_EXTENTIONS:
                found = word.find(ext)
                if found > 0:
                    try:
                        day = int(word[:found])
                    except:
                        pass

    if month < today.month and month != -1:
        year = year + 1

    if month == -1 and day != -1:  # There's a day if no month
        if day < today.day:
            month = today.month + 1
        else:
            month = today.month

    if month == -1 and day == -1 and day_of_week != -1:
        current_day_of_week = today.weekday()
        dif = day_of_week - current_day_of_week

        if dif < 0:
            dif += 7
            if texxxt.count("next") >= 1:
                dif += 7

        return today + datetime.timedelta(dif)

    if day != -1:
        return datetime.date(month=month, day=day, year=year)


def note(texxxxt):
    dattte = datetime.datetime.now()
    file_name = str(dattte).replace(":", "-") + "-note.txt"
    with open(file_name, "w") as f:
        f.write(texxxxt)

    subprocess.Popen(["notepad.txt", file_name])

# the openn function I created was to open a tkinter tab where the user would have an interface, I really wanted to inc-
# -lude an interface with the assistant, however it's not possible, I really tried to make it work and to make the
# output of the assistant a visual output as well in the lower frame however I couldn't make it work, so I haven't -
# used the function


def openn():
    root = tk.Tk()

    canvas = tk.Canvas(root, height=HIGH, width=WIDE)
    canvas.pack()

    background_image = tk.PhotoImage(file='external-content.duckduckgo-1.png')
    background_label = tk.Label(root, image=background_image)
    background_label.place(x=0, y=0, relheight=1, relwidth=1)

    frame = tk.Frame(root, bg='#80c1ff', bd=5)
    frame.place(relx=0.5, rely=0.1, relwidth=0.75, relheight=0.1, anchor='n')

    button = tk.Button(frame, text="Wake assistant")
    button.place(relx=0.4, relheight=1, relwidth=0.3)

    lower_frame = tk.Frame(root, bg='#80c1ff', bd=10)
    lower_frame.place(relx=0.5, rely=0.25, relwidth=0.75, relheight=0.6, anchor='n')

    label = tk.Label(lower_frame)
    label.place(relwidth=1, relheight=1)

    root.mainloop()

# The wake word is to notify the assistant you want to speak, then it will respond and you can ask it something


WAKE_WORD = "assistant"
SERVICE = authenticate_google()
print("Start")

while True:
    print("Listening, speak please")
    text = listen()

    if text.count(WAKE_WORD) > 0:
        speech("Hello, how can I help you")
        text = listen()
# The Calendar strings and Note strings are just for if you say those phrases when you speak then the computer will res-
# -pond with something appropriate
        CALENDAR_STRINGS = ["do i have plans", "am i busy", "what do i have"]
        for phrase in CALENDAR_STRINGS:
            if phrase in text:
                date = datttte(text)
                if date:
                    eventts(date, SERVICE)
                else:
                    speech("I don't see any events")

        NOTE_STRINGS = ["take a note", "make a note", "remember this", "write this down"]
        for phrase in NOTE_STRINGS:
            if phrase in text:
                speech("What would you like me to write down?")
                note_text = listen()
                note(note_text)
                speech("I've made a note of that.")
