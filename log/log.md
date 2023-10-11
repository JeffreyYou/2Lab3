# Development Log

## Project Information

- **Project Name:** RealChar-WhatsApp
- **Project Description:** Connect WhatsApp with RealChar
- **Start Date:** Oct 10. 2023
- **End Date:** Oct 11. 2023
- **Team Members:** Jeffrey You
- **Version:** beta 0.1

## Purpose

Connecting WhatsApp with ReachChar, so users could talk with characters on WhatsApp

## Progress Log

### Oct 10. 2023]

- **Time Spent:** 5 hours
- **Tasks Completed:**
  - Green API funcionalities test
  - Green API Python Implementation
  - Modifying `cli.python` to support WhatsApp connection
- **Issues Encountered:**
  - Green API developer plan restriction
  - Async task stuck in a dead loop
- **Solutions/Actions Taken:**
  - Change to Business Plan
  - Using `await Asyncio.sleep()` instead `time.sleep()`
- **Next Steps:**
  - Support concurrent connection
  - Find a way to support WhatsApp stream transmission

### Oct 11. 2023

- **Time Spent:** 1 hour
- **Tasks Completed:**
  - Remove Character Selection, set default as Elon Musk
- **Issues Encountered:**
  - None
- **Solutions/Actions Taken:**
  - None
- **Next Steps:**
  - Support concurrent connection
  - Find a way to support WhatsApp stream transmission

## Decisions Made

- The connection is triggered by the user's first message

## Code Changes

- ```python
  # generate url for Green API
  def generateUrl(method, id):
      # input the instance number and token
      instanceId = "7103865679"
      token = "0acca0d7f38e4a2d82a331cbba76e565132de8d6aff3413faf"
  
      baseUrl = "https://api.greenapi.com/waInstance" + instanceId +"/"
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
  ```

- ```python
  # send message to recipient phone number
  def sendMessage(message, recipient):
      url = generateUrl("send", 0)
      payload = {
          "chatId": str(recipient),
          "message": str(message)
      }
      data = json.dumps(payload)
  
      headers = {
          'Content-Type': 'application/json'
      }
  
      response = requests.request("POST", url, headers=headers, data=data)
  ```

- ```python
  # receive message from GreenAPI‘s message Queue
  def receiveMessage():
      url = generateUrl("receive", 0)
      data = {}
      headers = {}
      response = requests.request("GET", url, headers=headers, data=data)
      data = json.loads(response.text)
      return data
  ```

- ```python
  # clean GreenAPI‘s message Queue
  def cleanMessageQueue():
      while True:
          data = receiveMessage()
          if data == None:
              return
          deleteMessage(data["receiptId"])
  ```

- ```python
  # wait user to send message, blocking io
  def wait_one_message():
      # block and wait for one message from user
      while True:
          data = receiveMessage()
          # if no message, keep waiting
          if data == None:
              time.sleep(5)
              continue
          else:
              # message not from user, delete
              if data["body"]["typeWebhook"] != "incomingMessageReceived":
                  deleteMessage(data["receiptId"])
                  continue
              # get user message, delete and return sender and message info
              sender = data["body"]["senderData"]["sender"]
              message = data["body"]["messageData"]["textMessageData"]["textMessage"]
              result = [sender, message]
              deleteMessage(data["receiptId"])
              return result
  ```

- ```python
  # get one user message from queue, non-blocking io
  def read_one_message():
      while True:
          data = receiveMessage()
          # if no message, return
          if data == None:
              return None
          else:
              # message not from user, delete
              if data["body"]["typeWebhook"] != "incomingMessageReceived":
                  deleteMessage(data["receiptId"])
                  # print(f"delete 1 message ...")
                  continue
              # get user message, delete and return
              result = data["body"]["messageData"]["textMessageData"]["textMessage"]
              deleteMessage(data["receiptId"])
              return result
  ```

- ```python
  # async task to receive user message and send to server
  async def handle_text(websocket):
      while True:
          # check the queue every 5 seconds
          await asyncio.sleep(5)
          message = read_one_message()
          # if there is no message in the queue, sleep 5 seconds
          if message == None:
              continue
          #send message to server
          print(f"\nUser: {message}")
          await websocket.send(message)
  ```

- ```python
  # async task to receive response from server, concatenate the result and send to user
  async def receive_message(websocket):
      # message init
      finalResult = "Elon>"
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
                  sendMessage(finalResult, user)
                  # reset message
                  finalResult = ""
              elif message == '[thinking]\n':
                  # skip thinking message
                  break
              elif message.startswith('[+]'):
                  # stop playing audio
                  audio_player.stop_playing()
                  # indicate the transcription is done
                  print(f"\n{message}", end="\n", flush=True)
              elif message.startswith('[=]') or re.search(r'\[=([a-zA-Z0-9]+)\]', message):
                  # indicate the response is done
                  print(f"{message}", end="\n", flush=True)
              else:
                  # concatenate message 
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
  ```

- ```python
  # establish connection with user
  def establish_connection(session_id, url):
      # cleaning the message queue and waiting for user connection
      print("cleaning the existing message in the queue ...")
      cleanMessageQueue()
      print("cleaning finished")
      print("waiting for connection")
      result = wait_one_message()
      # get user phone number
      global user
      user =  result[0]
      # generate uri
      api_key = os.getenv('AUTH_API_KEY')
      llm_model = "gpt-3.5-turbo-16k"
      uri = f"ws://{url}/ws/{session_id}?api_key={api_key}&llm_model={llm_model}"
      return uri
  ```

## Testing and Quality Assurance

- **Testing:** print log info in the terminal
- **Bugs/Issues Found:** concurrent connection will result in a malfunction
- **Resolution:** none

## Additional Notes

None

## Resources

- **Links and References:** https://github.com/Shaunwei/RealChar

