import os
from flask import Flask, request, send_file
from twilio.twiml.messaging_response import MessagingResponse
from ChatGPT_FAQ import answer_query_with_context
import pandas as pd
from datetime import datetime
os.chdir('/home/cvenencia/mysite/ChatGPT-Twilio-Chatbot')

app = Flask(__name__)
try:
    chat_data = pd.read_csv(os.path.abspath('chat_data.csv'))
except FileNotFoundError:
    chat_data = pd.DataFrame(
        columns=['phone_number', 'message', 'response', 'timestamp']
    )

chat_data.head()


@app.route('/csv-data', methods=['GET'])
def send_json_data():
    return send_file(os.path.abspath('chat_data.csv'))


@app.route("/sms", methods=['GET', 'POST'])
def incoming_sms():
    """Send a response to a FAQ sent by the user"""
    prompt = request.values.get('Body', None)
    phone_number = request.values.get('From', None)
    answer = answer_query_with_context(prompt)

    global chat_data
    chat_data = pd.concat([pd.DataFrame.from_dict({
        'phone_number': [phone_number],
        'message': [prompt],
        'response': [answer],
        'timestamp': [datetime.now()],
    }), chat_data])
    chat_data.to_csv(os.path.abspath('chat_data.csv'), index=False)
    print(f"Q: {prompt}\nA: {answer}\n")

    resp = MessagingResponse()
    resp.message(answer)
    return str(resp)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
