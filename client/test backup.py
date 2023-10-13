import asyncio
import uuid
import os
import requests
import json
import time
import sys
import websockets
import concurrent.futures
import re
import io
import queue
from threading import Thread
from simpleaudio import WaveObject
import speech_recognition as sr




import pyaudio
from pydub import AudioSegment
from dotenv import load_dotenv


load_dotenv()

executor = concurrent.futures.ThreadPoolExecutor(max_workers=3)

# global user
user = ""

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

class AudioPlayer:
    def __init__(self):
        self.play_thread = None
        self.stop_flag = False
        self.queue = queue.Queue()

    def play_audio(self):
        while not self.stop_flag or not self.queue.empty():
            try:
                wav_data = self.queue.get_nowait()
            except queue.Empty:
                continue

            wave_obj = WaveObject.from_wave_file(wav_data)
            play_obj = wave_obj.play()

            while play_obj.is_playing() and not self.stop_flag:
                time.sleep(0.1)

            if self.stop_flag:
                play_obj.stop()

    def start_playing(self, wav_data):
        self.stop_flag = False
        self.queue.put(wav_data)

        if self.play_thread is None or not self.play_thread.is_alive():
            self.play_thread = Thread(target=self.play_audio)
            self.play_thread.start()

    def stop_playing(self):
        if self.play_thread and self.play_thread.is_alive():
            self.stop_flag = True
            self.play_thread.join()
            self.play_thread = None

    def add_to_queue(self, wav_data):
        self.queue.put(wav_data)


audio_player = AudioPlayer()

def generateUrl(method, id):
    baseUrl = "https://api.greenapi.com/waInstance7103865679/"
    token = "0acca0d7f38e4a2d82a331cbba76e565132de8d6aff3413faf"
    chatId = "/" + str(id)
    if method == 'receive':
        return baseUrl + "receiveNotification/" + token
    if method == 'send':
        return baseUrl + "SendMessage/" + token
    if method == "clear":
        return baseUrl + "clearMessagesQueue/" + token
    if method == "show":
        return baseUrl + "showMessagesQueue/" + token
    if method == 'delete':
        return baseUrl + "deleteNotification/" + token + chatId
    
def sendMessage(message):
    url = generateUrl("send", 0)
    payload = {
        "chatId": str(user),
        "message": str(message)
    }
    data = json.dumps(payload)

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=data)

def receiveMessage():
    url = generateUrl("receive", 0)
    data = {}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=data)
    data = json.loads(response.text)
    return data

def deleteMessage(receiptId):
    payload = {}
    headers = {}
    url = generateUrl("delete", receiptId)
    response = requests.request("DELETE", url, headers=headers, data=payload)

def cleanMessageQueue():
    while True:
        data = receiveMessage()
        if data == None:
            return
        deleteMessage(data["receiptId"])

def cleanOneMessage():
    while True:
        data = receiveMessage()
        if data == None:
            print("clean finish")
            return
        if data["body"]["typeWebhook"] == "outgoingMessageReceived":
            deleteMessage(data["receiptId"])
            print(f"delete 1 main message ...")
            return
        
        deleteMessage(data["receiptId"])
        print(f"delete 1 message ...")

def wait_one_message():
    # block and wait for one message from user
    while True:
        data = receiveMessage()
        if data == None:
            time.sleep(5)
            continue
        else:
            if data["body"]["typeWebhook"] != "incomingMessageReceived":
                deleteMessage(data["receiptId"])
                print(f"delete 1 message ...")
                continue
            sender = data["body"]["senderData"]["sender"]
            message = data["body"]["messageData"]["textMessageData"]["textMessage"]
            result = [sender, message]
            deleteMessage(data["receiptId"])
            return result

def read_one_message():
    # get one user message from queue
    while True:
        data = receiveMessage()
        if data == None:
            return None
        else:
            if data["body"]["typeWebhook"] != "incomingMessageReceived":
                deleteMessage(data["receiptId"])
                print(f"delete 1 message ...")
                continue
            # sender = data["body"]["senderData"]["sender"]
            result = data["body"]["messageData"]["textMessageData"]["textMessage"]
            deleteMessage(data["receiptId"])
            return result

async def handle_text(websocket):
    # print('You: ', end="", flush=True)

    while True:
        # check the queue every 5 seconds
        await asyncio.sleep(5)
        message = read_one_message()
        if message == None:
            continue
        
        print(f"sent message to server: {message}")
        await websocket.send(message)

async def receive_message(websocket):
    finalResult = ""
    while True:
        try:
            message = await websocket.recv()
        except websockets.exceptions.ConnectionClosedError as e:
            print("Connection closed unexpectedly: ", e)
            break
        except Exception as e:
            print("An error occurred: ", e)
            break

        if isinstance(message, str):
            if message == '[end]\n' or re.search(r'\[end=([a-zA-Z0-9]+)\]', message):
                print('\nYou: ', end="", flush=True)
                # print(finalResult)
                sendMessage(finalResult)
                finalResult = ""
            elif message == '[thinking]\n':
                # skip thinking message
                break
            elif message.startswith('[+]'):
                # stop playing audio
                # audio_player.stop_playing()
                # indicate the transcription is done

                print(f"\n{message}", end="\n", flush=True)
            elif message.startswith('[=]') or re.search(r'\[=([a-zA-Z0-9]+)\]', message):
                # indicate the response is done

                print(f"{message}", end="\n", flush=True)
            else:
                # sendMessage(message)
                finalResult += message

                print(f"{message}", end="", flush=True)
        elif isinstance(message, bytes):
            audio_data = io.BytesIO(message)
            audio = AudioSegment.from_mp3(audio_data)
            wav_data = io.BytesIO()
            audio.export(wav_data, format="wav")
            # Start playing audio
            audio_player.start_playing(wav_data)
        else:
            print("Unexpected message")
            break

async def start_client(session_id, url):
    api_key = os.getenv('AUTH_API_KEY')
    # llm_model = select_model()
    llm_model = "gpt-3.5-turbo-16k"
    uri = f"ws://{url}/ws/{session_id}?api_key={api_key}&llm_model={llm_model}"
    async with websockets.connect(uri) as websocket:
        # send client platform info
        await websocket.send('terminal')
        # sendMessage(f"Client #{session_id} connected to server")
        print(f"Client #{session_id} connected to server")

        welcome_message = await websocket.recv()
        # print(f"{welcome_message}")
        # sendMessage(f"{welcome_message}")

        # character = wait_one_message()
        # character = input('Select character: ')
        # print(f"user {user} selected character: {character[1]}")
        # await websocket.send(character[1])
        
        await websocket.send("1")
        
        send_task = asyncio.create_task(handle_text(websocket))
        receive_task = asyncio.create_task(receive_message(websocket))

        await asyncio.gather(receive_task, send_task)


async def main(url):
    session_id = str(uuid.uuid4().hex)
    task = asyncio.create_task(start_client(session_id, url))
    try:
        await task
    except KeyboardInterrupt:
        task.cancel()
        await asyncio.wait_for(task, timeout=None)
        print("Client stopped by user")

if __name__ == "__main__":
    print("cleaning the existing message in the queue ...")
    cleanMessageQueue()
    print("cleaning finished")

    print("waiting for connection")
    result = wait_one_message()
    user =  result[0]
    
    url = sys.argv[1] if len(sys.argv) > 1 else 'localhost:8000'
    asyncio.run(main(url))