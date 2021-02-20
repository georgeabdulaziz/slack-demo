import slack
import os
from pathlib import Path
from dotenv import load_dotenv
# Import Flask
from flask import Flask
# Handles events from Slack
from slackeventsapi import SlackEventAdapter




import requests
import spacy


apiKey = "31f28184961a3704dd2121975932b40b"
nlp = spacy.load('en_core_web_sm')




# Load the Token from .env file
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
# Configure your flask application
app = Flask(__name__)

# Configure SlackEventAdapter to handle events
slack_event_adapter = SlackEventAdapter(os.environ['SIGNING_SECRET'],'/slack/events',app)

# Using WebClient in slack, there are other clients built-in as well !!
client = slack.WebClient(token=os.environ['SLACK_TOKEN'])

# connect the bot to the channel in Slack Channel
#client.chat_postMessage(channel='#general', text='Send Message Demo')

# Get Bot ID
BOT_ID = client.api_call("auth.test")['user_id']

@app.route('/')
def hello():
    return 'up'



# handling Message Events
@slack_event_adapter.on('message')
def message(payload):
    print(payload)


    event = payload.get('event',{})
    channel_id = event.get('channel')
    user_id = event.get('user')
    text2 = event.get('text')

    #this is related to spacy library
    #spaCy is a free, open-source library for advanced Natural Language Processing (NLP) in Python.
    doc = nlp(text2)

    for ent in doc.ents:
        if ent.label_=="GPE":
            url = f"https://api.openweathermap.org/data/2.5/weather?q={ent.text}&appid={apiKey}"
            response = requests.request("GET", url)
            # print(type(response.text))
            # print(type(response.json()))
            tempInKelvin = int(response.json().get('main').get('temp'))
            tempInCelsius = round((tempInKelvin - 273.15),2)
            #print(tempInCelsius)
            statement = f'The temperature in {ent.text} is {tempInCelsius}'
            if BOT_ID != user_id:
                client.chat_postMessage(channel=channel_id, text=statement)

# Run the webserver micro-service
if __name__ == "__main__":
    app.run(debug=True)








#https://openweathermap.org/current