# Developer

### Phone发送

outgoingMessageReceived 

```json
{
   "receiptId": 3,
   "body": {
      "typeWebhook": "outgoingMessageReceived",
      "instanceData": {
         "idInstance": 7103864968,
         "wid": "12136186873@c.us",
         "typeInstance": "whatsapp"
      },
      "timestamp": 1696995484,
      "idMessage": "3A9C769F161793E69BBF",
      "senderData": {
         "chatId": "12136186873@c.us",
         "chatName": "Jeffrey You",
         "sender": "12136186873@c.us",
         "senderName": "Jeffrey"
      },
      "messageData": {
         "typeMessage": "textMessage",
         "textMessageData": {
            "textMessage": "Hello"
         }
      }
   }
}
```



outgoingMessageStatus

```json
{
   "receiptId": 4,
   "body": {
      "typeWebhook": "outgoingMessageStatus",
      "chatId": "12136186873@c.us",
      "instanceData": {
         "idInstance": 7103864968,
         "wid": "12136186873@c.us",
         "typeInstance": "whatsapp"
      },
      "timestamp": 1696995484,
      "idMessage": "3A9C769F161793E69BBF",
      "status": "sent",
      "sendByApi": false
   }
}
```





### API to Phone

```json
{
   "receiptId": 5,
   "body": {
      "typeWebhook": "outgoingAPIMessageReceived",
      "instanceData": {
         "idInstance": 7103864968,
         "wid": "12136186873@c.us",
         "typeInstance": "whatsapp"
      },
      "timestamp": 1696995932,
      "idMessage": "BAE56C187AB86608",
      "senderData": {
         "chatId": "12136186873@c.us",
         "chatName": "Jeffrey You",
         "sender": "12136186873@c.us",
         "senderName": ""
      },
      "messageData": {
         "typeMessage": "extendedTextMessage",
         "extendedTextMessageData": {
            "text": "Hello World",
            "description": "",
            "title": "",
            "previewType": "None",
            "jpegThumbnail": "",
            "forwardingScore": 0,
            "isForwarded": false
         }
      }
   }
}
```



```json
{
   "receiptId": 6,
   "body": {
      "typeWebhook": "outgoingMessageStatus",
      "chatId": "12136186873@c.us",
      "instanceData": {
         "idInstance": 7103864968,
         "wid": "12136186873@c.us",
         "typeInstance": "whatsapp"
      },
      "timestamp": 1696995932,
      "idMessage": "BAE56C187AB86608",
      "status": "sent",
      "sendByApi": true
   }
}
```



# Business

### Phone发送

```json
{
   "receiptId": 5,
   "body": {
      "typeWebhook": "incomingMessageReceived",
      "instanceData": {
         "idInstance": 7103865679,
         "wid": "13145997724@c.us",
         "typeInstance": "whatsapp"
      },
      "timestamp": 1697051568,
      "idMessage": "3AE53B8E7C4C74BB3980",
      "senderData": {
         "chatId": "12136186873@c.us",
         "chatName": "Jeffrey",
         "sender": "12136186873@c.us",
         "senderName": "Jeffrey"
      },
      "messageData": {
         "typeMessage": "textMessage",
         "textMessageData": {
            "textMessage": "Hello World"
         }
      }
   }
}

```

### API to Phone

```json
{
   "receiptId": 7,
   "body": {
      "typeWebhook": "outgoingMessageReceived",
      "instanceData": {
         "idInstance": 7103865679,
         "wid": "13145997724@c.us",
         "typeInstance": "whatsapp"
      },
      "timestamp": 1697051817,
      "idMessage": "3A4F840254081BB53675",
      "senderData": {
         "chatId": "12136186873@c.us",
         "chatName": "Jeffrey",
         "sender": "13145997724@c.us",
         "senderName": "Cealum"
      },
      "messageData": {
         "typeMessage": "textMessage",
         "textMessageData": {
            "textMessage": "yep testing"
         }
      }
   }
}
```

