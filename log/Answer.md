# 1. LlamaIndex

#### 1.1 LlamaIndex如何连接到RealChar的数据源？

使用 [llama hub community](https://llamahub.ai/) 提供的data connector生成对应的data loader

或者根据文档[llama hub文档]( https://github.com/run-llama/llama-hub/tree/main)自己上传一个dataloader

#### 1.2 LlamaIndex如何摄取和索引RealChar的数据？

**Data connector:** data loader 读取数据源生成document

**Document/nodes:** document存入各种数据源的raw data，是所有数据的整合，最小单元是node

**Data Indexes:** Raw data将被通过如VectorStoreIndex的被parse成易读取的索引数据存入Knowledge base

#### 1.3 RealChar如何使用LlamaIndex的查询接口来实现知识增强的查询？

**Retriever:** 每次Query从Knowledge base中获取最relevant context(例如对向量索引进行密集检索)

**Node Postprocessor:** 对retrieved数据进行transformation, filtering, re-ranking logic 

**Response Synthesizer:** 对处理过的数据像LLM进行一次或多次Query得到答案

提供的pipeline:

Query Engines: 能够让你 ask questions over your data

Chat Engines: 能够多次have a conversation with your data

Agents: 类似Query和Chat但区别在于上面是遵循写死的logic, 而agen dynamiclly decision.

#### 1.4 LlamaIndex如何支持RealChar的特定功能，例如数据增强的聊天机器人和文档问答？

例如提前获取某个角色例如Elon Musk的数据(例如个人资料，视频，公开讲话，图片，甚至每条发过的Twitter), 然后对这些data进行处理存入Knowledge base中, 这样聊天机器人将会非常贴合这个人的特性.

#### 1.5 LlamaIndex如何保证数据的安全和隐私？

**Data Privacy:** 

由选择的模型policy决定, 如果使用OpenAI则是遵循OpenAI的privacy policy, 其他LLMs同理

如果偏向隐私，安全，成本的话可以选择使用开源模型

**Vector Stores**: LlamaIndex只负责提供module接入Vector DB, 数据安全遵循具体的DB的policy



#### 1.6 在RealChar中实现LlamaIndex需要哪些技术准备和依赖？

实现每一步data connectors, indices, retrievers, query engines对应的依赖

#### 1.7 LlamaIndex如何影响RealChar的性能和响应时间？

性能:

Llamaindex提供Response Evaluation，判断结果的

Correctness, Semantic Similarity, Faithfulness, Context Relevancy, Guideline Adherence

响应时间:

跟从vector DB retrieve数据的速度和精确性以及询问LLM的次数和时间有关

# 2. 关于Chroma和SQLLite

#### 2.1 Chroma和SQLite在RealChar中是如何配置和连接的？

通过sqlalchemy和langchain.vectorstores

```python
from sqlalchemy import sa
from langchain.vectorstores import Chroma
```

#### 2.2 这两个数据库在RealChar中承担哪些具体的功能和责任？

Chroma负责存储经过embedding算法提取成的Vector Data

SQLite负责存储公司的私有数据(例如根据某个角色专门收集的数据)，越全面Chroma匹配时越精准

SQLite同时也储存用户之前的输入的矢量数据，以方便实现记忆功能

同时SQLite也可以储存高频次，高相似度的问题，从而避免次次都需要走模型接口，节省成本提高速度

#### 2.3 如何利用Chroma和SQLite实现长期记忆功能？

由于大语言模型都会有token的限制，为了理解上下文需要把用户之前的输入重复, 超过了token的限制就意味着失去了"长期记忆"的功能.

用户输入prompt的时候，先把prompt使用embedding算法转换成向量，然后再向Vector DB进行Query以获取本次必要的相关知识. 跟据相似度匹配Knowledge base对应的信息，组成Related Text Chunk，然后输入给预先设置好的prompt template生成具备知识和语境的prompt交给大语言模型处理

由于输入由原先的大段字符串变成了提取过特征的Vector Data，大大缩减了真实提交给大语言模型数据量. 同时SQLite用于储存用户之前上下文对应的Vector Data，和本次prompt生成的数据一起提交给大语言模型就实现了长期的记忆功能

#### 2.4 Chroma和SQLite在数据管理和查询方面有何区别？

SQLite作为RDBMS是以Table为储存单元，row代表data entity，column是data feature

SQLite适合精确匹配，例如找到具备某个feature的数据，但是很难做快速similarity比较

Chroma作为Vector DB，存储的Vector Data每一位都代表着某个feature

Chroma由于每个feature因此可以做快速的相似度比对查找，在面对用户没有一个确定格式的输入时可以极速的匹配用户最想表达的意思与相关的知识点，因此很适合用于

#### 2.5 如何确保通过Chroma和SQLite处理的数据的安全和隐私？

实现：用户认证、访问控制、数据加密存储、危险操作审核、数据备份 等功能

#### 2.6 在RealChar的开发和运维过程中，如何管理和维护Chroma和SQLite？

对于SQLite可以使用类似Navicat的软件，支持可视化界面，CRUD，相似数据合并，生成test数据，自动化脚本

Chroma可以部署到docker容器上，使用Jenkins实现CI/CD pipline和Kubernetes管理

#### 2.7 这两个数据库在实现RealChar功能时的性能和可扩展性如何？

访问量低时

SQLite资源消耗很低，速度快，配置简单易用

Chroma同样简单，迅速，功能丰富

访问量高时

SQLite作为RDBMS可以的扩展方案为：分库分表，外部缓存(Redis)，索引优化

Chroma采用distributed architecture，有更好的水平扩展性

#### 2.8 是否有其他技术或工具与Chroma和SQLite配合，以实现RealChar的功能？

可以使用Redis作为缓存降低数据库的压力

使用消息队列例如Kafka，对瞬时高qps进行消峰防止数据库被击穿，异步任务提高Response速度



# 3. 关于LangChain

#### 3.1 LangChain在RealChar中的具体作用是什么？

每个大语言模型以及根据其实现功能的所需要的流程都不相同，LongChain对每个功能实现的流程的每个步骤都提供了标准化的模版

LongChhain可以让RealChar的开发过程变得标准化，并且拥有很高的可扩展性

#### 3.2 LangChain如何协调和管理不同的大型语言模型？

Large Language Models (LLMs) are a core component of LangChain. LangChain does not serve its own LLMs, but rather provides a standard interface for interacting with many different LLMs.

#### 3.3 LangChain如何与RealChar的数据库和前端交互？

连接SQL

create a SQLDatabase object by passing a SQLAlchemy database URI to SQLDatabase

```python
from langchain.utilities import SQLDatabase
db = SQLDatabase.from_uri('sqlite:///chinook.db')

```

连接Chroma

Install Chroma and create a Chroma client. This can be an in-memory client or connect to a Chroma server.

Create or get a Chroma collection to store documents.

Pass the client and collection to `Chroma()` along with an embedding function.

```python
import chromadb
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma

client = chromadb.Client()
collection = client.create_collection("my_collection")

chroma = Chroma(client, "my_collection", OpenAIEmbeddings())
```

前端2种方法

Expose LangChain's HTTP API. This allows sending prompts and getting responses via simple HTTP requests. Frontends can use fetch, axios etc to call the API.

Run LangChain as a service and connect via websockets. Frontends can open a websocket to LangChain to send prompts and receive responses in realtime.

#### 3.4 LangChain如何处理和传输数据？

**Data Decomposition and Distribution**:   decompose data into different modal data types 

**Data Preprocessing**: preprocess the data to store in vector db

**Data Synchronization and Concatenation**: different models synchronize and concatenate operations 

**Data Flow Management**: managing the data flow between different models

**Integration of Model Results**: generate final result

具体流程

document loader -> document transformer -> text embedding -> vector stores -> retriever

#### 3.5 LangChain如何影响RealChar的性能和响应时间？

Caching: 

`InMemoryCache` and `SQLiteCache` to cache LLM responses

Chaining:

`LLMChain` compose multiple LLMs into a chain.

Async APIs：

LongChain support Async API call

#### 3.6 在RealChar的开发和运维中，如何配置和管理LangChain？

配置:

Configure via **Yaml config files** or constructor arguments and methods in LangChain clients.

管理:

LangChainLogger日志

LangChain tools 提供可视化界面

#### 3.7 LangChain如何支持RealChar的长期记忆和个性化交互功能？

缓存最近的上下文context

数据库获取用户信息

生成LLM-based agents，动态获取memory和external source

用以上建立一条支持long-term memory的chains

#### 3.8 LangChain有何安全和隐私保护措施，以保护用户和系统数据？

Access to user data is limited only to authorized personnel

User interactions with the system are encrypted end-to-end.

The system architecture is designed with security in mind.

Regular security audits, penetration testing, and vulnerability assessments are conducted by third parties. 

Prevents the LLM from seeing any contents within the database. only the database scheme 



# 4. 关于Green API

#### 4.1. Green API的核心功能和特性是什么？

可以send and receive message on WhatsApp

#### 4.2. 如何通过Green API发送和接收WhatsApp消息？

购买后根据提供的API提供chatId和message等内容然后向服务器发送http请求就行

#### 4.3. Green API有哪些编程语言的SDK，是否支持我们的技术栈？

支持1C, Node.js, HTML, PHP, Python, Go. 支持我们的技术栈

#### 4.4. 如何通过Green API与RealChar的数据库交互？

从数据库获取用户信息然后根据API放入http请求的parameter里发送给Green API就行

#### 4.5. Green API的安全性如何，如何保护用户数据？

通过end-to-end encryption实现传输数据加密

#### 4.6. Green API的费用结构是什么，哪个套餐最符合我们的需求？

Developer, ChatBot, Business三种模式, Business比较合适

#### 4.7. 如何快速集成Green API，查询详细的文档和技术支持？

根据官方文档快速集成和技术支持https://green-api.com/en/docs/api/

同时支持Slack, Make, Zapier的集成

#### 4.8. Green API对数据发送有什么样的限制，比如消息的发送速率，每月的消息数量限制等？

一个instance每秒可以发送50次send message请求

Rate limiterhttps://green-api.com/en/docs/api/ratelimiter/

#### 4.9. 如何处理超出限制的情况，是否有额外的费用？

超出部分会收到error 429的错误，不会有额外费用

#### 4.10. Green API是否提供任何优化或解决方案，以适应高数据传输需求的场景？​

官网上没有看见，或许可以邮件咨询

# 5. 关于React Native

#### 5.1 如何在React Native中设置和配置WebSocket客户端以连接到RealChar？

 ```react
 // ws生命周期
 var ws = new WebSocket('ws://host.com/path');
 
 ws.onopen = () => {
   // connection opened
   ws.send('something');
 };
 
 ws.onmessage = (e) => {
   // a message was received
   console.log(e.data);
 };
 
 ws.onerror = (e) => {
   // an error occurred
   console.log(e.message);
 };
 
 ws.onclose = (e) => {
   // connection closed
   console.log(e.code, e.reason);
 };
 
 ```

#### 5.2. RealChar的WebSocket服务器如何处理来自React Native的连接和请求？

```python
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)
```

#### 5.3. 是否需要特定的库或工具来实现WebSocket通信？

```python
from fastapi import (
    Cookie,
    Depends,
    FastAPI,
    Query,
    WebSocket,
    WebSocketException,
    status,
)

async def get_cookie_or_token(
    websocket: WebSocket,
    session: Annotated[str | None, Cookie()] = None,
    token: Annotated[str | None, Query()] = None,
):
    if session is None and token is None:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION) 
    return session or token


@app.websocket("/items/{item_id}/ws")
async def websocket_endpoint(
    *,
    websocket: WebSocket,
    item_id: str,
    q: int | None = None,
    cookie_or_token: Annotated[str, Depends(get_cookie_or_token)], //Depends
):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(
            f"Session cookie or query token value is: {cookie_or_token}"
        )
        if q is not None:
            await websocket.send_text(f"Query parameter q is: {q}")
        await websocket.send_text(f"Message text was: {data}, for item ID: {item_id}")
```

#### 5.4. 如何确保WebSocket连接的安全和数据保护？

1、使用SSL/TLS加密协议保护WebSocket通信的数据。

2、使用token或权限验证机制来防止未授权的访问。

3、限制并发连接数，防止DoS攻击。

4、过滤用户输入，防止SQL注入和XSS攻击。

#### 5.5. WebSocket通信在错误处理和异常管理方面有何策略？

连接失败，连接断开， 连接超时，用户认证，会话管理 (用户通知，心跳检测，session token cookie)

异常消息， 异常日志， 跨站脚本和sql注入 (拦截器， 日志

#### 5.6. 如何测试和监控WebSocket连接的性能和稳定性？

测试:

进行负载，压力测试: 

模拟大规模高并发场景，计算丢包率，throughput， 反应时间, 服务器内存使用等等.

或者使用CI/CD pipeline, 自动部署到测试服务器上

模拟网络故障，SQL注入，XSS， DoS等情况下的表现

日志:

服务器日志，客户端日志，第三方监控软件例如prometheus



#### 5.7. 是否有现成的示例或文档来指导WebSocket的实现和集成？

具体的语言和框架对应的document

https://fastapi.tiangolo.com/advanced/websockets/?h=web

#### 5.8. WebSocket连接是否支持实时数据同步和更新？

支持

因为websocket是一个低延迟，持久连接，全双工通信的协议。服务端可以直接推送数据而不是传统HTTP的由用户向服务器请求



# 6. 关于用户自己创建数字人
#### 6.1. 用户能定制哪些属性和特征？

理论上可以按照已有数据的特征划分的特性都可以实现, 例如性别, 声音, 性格, 语气, 人物背景, 心情等等

#### 6.2. 如何存储和管理用户创建的个性数字人数据？

提取特征值然后存入存入用户数字人对应的field

#### 6.3. 如何确保用户数据的安全和隐私？

数据加密, 访问控制, 身份验证, 数据脱敏, 安全监控, 数据备份, 权限管理等等

#### 6.4. 是否需要提供预设模板以简化数字人创建过程？

可以提供模版, 例如列举一些人物的关键特性, 声音音色, 背景故事, 人物性格, 可以大幅度提高用户体验

#### 6.5. 用户如何预览和测试他们创建的数字人？

可以制作一个对应的页面展示数字人的关键信息和一些可以代表用户性格的回答(例如："用你最喜欢的方式向我问候早上好")

#### 6.6. 如何处理用户反馈和数字人的迭代更新？

根据用户的描述确定数字人哪些特征需要改进(最好提供对应的选项方便精准定位)，再根据用户的描述或者提前内置的特性来修改这些特征

#### 6.7. 用户创建的个性数字人如何与RealChar的其他功能和服务集成？

围绕数字人提供一些附加的服务，例如移动端可以制定闹钟或者定时提醒功能，可以模拟数字人像一个朋友一样提醒做一件事情的情景
