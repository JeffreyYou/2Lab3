import asyncio
import sys
import requests
from typing import List
import json
import hashlib
import os
import websockets
import re

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict(str, str) = {}
        self.sessions = dict()

    # generate url for Green API
    def generate_url(self, method: str, id: int):
        # input the instance number and token
        instanceId = "7103865679"
        token = "0acca0d7f38e4a2d82a331cbba76e565132de8d6aff3413faf"

        baseUrl = "https://api.greenapi.com/waInstance" + instanceId +"/"
        chatId = "/" + str(id)
        if method == 'receive':
            return baseUrl + "receiveNotification/" + token
        if method == 'send':
            return baseUrl + "SendMessage/" + token
        if method == 'delete':
            return baseUrl + "deleteNotification/" + token + chatId

    # send message to recipient phone number 
    def send_message(self, message, recipient):
        url = self.generate_url("send", 0)
        payload = {
            "chatId": str(recipient),
            "message": str(message)
        }
        data = json.dumps(payload)

        headers = {
            'Content-Type': 'application/json'
        }

        requests.request("POST", url, headers=headers, data=data)

    # clean GreenAPI‘s message Queue
    def cleanMessageQueue(self):
        print("cleaning the existing message in the queue ...")

        while True:
            data = self.receive_message()
            if data == None:
                print("cleaning finished")
                return
            self.delete_message(data["receiptId"])
    # receive message from GreenAPI‘s message Queue
    def receive_message(self):
        url = self.generate_url("receive", 0)
        data = {}
        headers = {}
        response = requests.request("GET", url, headers=headers, data=data)
        data = json.loads(response.text)
        return data

    def delete_message(self, receiptId: str):
        payload = {}
        headers = {}
        url = self.generate_url("delete", receiptId)
        requests.request("DELETE", url, headers=headers, data=payload)

    # get one user message from queue, non-blocking io
    def read_one_message(self):
        # get one user message from queue
        while True:
            data = self.receive_message()
            # if no message, return
            if data == None:
                return None
            else:
                # message not from user, delete
                if data["body"]["typeWebhook"] != "incomingMessageReceived":
                    self.delete_message(data["receiptId"])
                    continue
                # get user message, delete and return
                message = data["body"]["messageData"]["textMessageData"]["textMessage"]
                sender = data["body"]["senderData"]["sender"]
                result = [sender, message]
                self.delete_message(data["receiptId"])
                return result
    
    def generate_session_id(self, sender: str):

        hash_object = hashlib.sha256()
        hash_object.update(sender.encode())
        session_id = hash_object.hexdigest()[:40]
        return session_id
    
    def add_connection(self, sender, websocket):
        self.active_connections[sender] = websocket


manager = ConnectionManager()

async def handle_user_prompt():
    while True:
        # check the queue every 1 seconds
        print("user_prompt sleeping")
        await asyncio.sleep(0.5)
        print("user_prompt awake")
        result = manager.read_one_message()
        # if there is no message in the queue, sleep 5 seconds
        if result == None:
            continue
        sender = result[0]
        message = result[1]
        #send message to server
        print(f"\nUser: {message}")
        websocket = manager.active_connections[sender]
        await websocket.send(message)

async def handle_server_response():
    finalResult = ""
    while True:
        if len(manager.active_connections) == 0:
            print("user_response sleeping")
            await asyncio.sleep(0.5)
            print("user_response awake")
            continue
        else:
            break
    websocket = manager.active_connections["12136186873@c.us"]

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
                # transmission end, send message
                manager.send_message(finalResult, "12136186873@c.us")
                # reset message
                finalResult = ""
                continue
            else:
                # concatenate message 
                finalResult += message
                print(f"{message}", end="", flush=True)


async def handle_user_request(url):
    while True:
        
        data = manager.receive_message()
        if data == None:
            print("user_request sleeping")
            await asyncio.sleep(2)
            print("user_request awake")
            continue
        # message not from user, delete
        if data["body"]["typeWebhook"] != "incomingMessageReceived":
            manager.delete_message(data["receiptId"])
            continue
        if data["body"]["typeWebhook"] == "incomingMessageReceived":
            sender = data["body"]["senderData"]["sender"]
            if sender in manager.active_connections:
                print(f"user {sender} already exist")
                await asyncio.sleep(2)
                continue
            if sender not in manager.active_connections:
                session_id = manager.generate_session_id(sender)
                api_key = os.getenv('AUTH_API_KEY')
                llm_model = "gpt-3.5-turbo-16k"
                uri = f"ws://{url}/ws/{session_id}?api_key={api_key}&llm_model={llm_model}"
                manager.delete_message(data["receiptId"])
                print(f"new user {sender} received")
                try:
                    websocket = await websockets.connect(uri)
                    await websocket.send('terminal')
                    welcome_message = await websocket.recv()
                    # select Elon Musk
                    await websocket.send("1")
                    manager.send_message("[Connection established!]\nYou are chatting with Elon Musk", sender)
                    manager.add_connection(sender, websocket)
                except Exception as e:
                    print(f"sender: {sender} websocket connection error")
                

async def main(url):
    manager.cleanMessageQueue()
    new_user_task = asyncio.create_task(handle_user_request(url))
    server_response_task = asyncio.create_task(handle_server_response())
    user_prompt_task = asyncio.create_task(handle_user_prompt())
    task = asyncio.gather(new_user_task, user_prompt_task, server_response_task)
    try:
        await task
    except KeyboardInterrupt:
        task.cancel()
        await asyncio.wait_for(task, timeout=None)
        print("Client stopped by user")


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else 'localhost:8000'
    asyncio.run(main(url))