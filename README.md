# README #

Surrealist is a Python tool to work with awesome [SurrealDB](https://docs.surrealdb.com/docs/intro)

It is blocking and **unofficial**, so if you need async AND/OR official client go [here](https://github.com/surrealdb/surrealdb.py)

Works and tested on Ubuntu, macOS, Windows 10, can use python 3.8+(including python 3.12)

#### Key features: ####

 * only one small dependency (websocket-client), no need to pull a lot of libraries to your project
 * fully documented
 * well tested (on latest Ubuntu, macOS and Windows 10)
 * fully compatible with latest version of SurrealDB (1.1.1), including [live queries](https://surrealdb.com/products/lq)
 * debug mode to see all that goes in and out, if you need
 * http or websocket transport to use

More to come:
 * connections pool
 * additional features (count, remove etc.)
 * transactions, explain


### Installation ###

Via pip:

`pip install surrealist`

### Before you start ###
Please, make sure you install and start SurrealDB, you can read more [here](https://docs.surrealdb.com/docs/installation/overview)

## Transports ##
First of all, you should know that SurrealDB can work with websocket or http "transports", we chose to support both transports here, 
but websockets is preferred and default one. Websockets can use live queries and other cool features.
Each transport has functions it can not use by itself (in current SurrealDB version)

**Http-transport can not:**
 - invalidate, authenticate session
 - create or kill live query
 - use operations INFO or PATCH (you should use raw query instead)

**Websocket-transport can not:**
 - import or export data (you should use http connection or cli tools for that)
 - import or export ML files (you should use http connection or cli tools for that)

Transports use query where it is possible, for compatibility, in all other cases if you use these methods on transports -CompatibilityError will be raised


## Connect to SurrealDB ##
All you need is url of SurrealDB and sometimes a few more data to connect

**Example 1**

In this example we explicitly show all parameters, but remember many of them are optional

```python
from surrealist import Surreal

# we create surreal object, it can be used to create one or more connections with websockets (use_http=False)
# with timeout 10 seconds and ERROR logging level
surreal = Surreal("http://127.0.0.1:8000", namespace="test", database="test", credentials=("root", "root"),
                  use_http=False, timeout=10, log_level="ERROR")
print(surreal.is_ready())  # prints True if server up and running on that url
print(surreal.version())  # prints server version
```
**Note:** create of Surreal object does not attempt any connections or other actions, just store parameters for future use

Calls of **is_ready()**, **health()** or **version()** on Surreal objects are for server checks only, these not validates or checks your namespace, database or credentials.

### Parameters ###

**url** - url of SurrealDB server, if you sure you will use websocket connection - you can use url like ws://127.0.0.1:8000/rpc, but http will work fine too even for websockets.
So, you can simply use http://127.0.0.1:8000, it will be transform to ws://127.0.0.1:8000/rpc under the hood.
If your url is differs - specify url in ws(s) format

But if you will use ws(s) format, Surreal object will try to predict http url too, it is important for status and version checks.
For example for wss://127.0.0.1:9000/some/rps predicted http url will be https://127.0.0.1:9000/

**namespace** - name of the namespace, it is optional, but if you use it, you should specify database too

**database** - name of the database, it is optional, but if you use it, you should specify namespace too

**credentials** - optional, pair(tuple) of username and password for SurrealDB

**use_http** - optional, False by default, flag of using websockets or http transport, False mean using websocket, specify True if you want to use http transport

**timeout** - optional, 5 seconds by default, it is time in seconds to wait for responses and messages, time for trying to connect to SurrealDB

**log_level** - optional, "ERROR" by default, one of (DEBUG, INFO, ERROR), where ERROR - to see only errors, INFO - to see only operations, DEBUG - to see all, including transport requests/responses

**Example 2**

In this example we do not use default(optional) parameters

```python
from surrealist import Surreal

# we create surreal object, it can be used to create one or more connections with websockets
# with timeout 5 seconds and ERROR logging level
surreal = Surreal("http://127.0.0.1:8000")
print(surreal.is_ready())  # prints True if server up and running on that url
print(surreal.version())  # prints server version
```
## Context managers and close ##
You should always close created connections, when you not need them anymore, the best way to do it is via context manager

**Example 3**

```python
from surrealist import Surreal

surreal = Surreal("http://127.0.0.1:8000", namespace="test", database="test", credentials=("root", "root"))
with surreal.connect() as ws_connection:  # create context manager, it will close connection for us
    result = ws_connection.select("person")  # select from db
    print(result)  # print result
# here connection is closed
```
You can do the same by itself:

**Example 4**

```python
from surrealist import Surreal

surreal = Surreal("http://127.0.0.1:8000", namespace="test", database="test", credentials=("root", "root"))
ws_connection = surreal.connect()  # open connection
result = ws_connection.select("person")  # select from db
print(result)  # print result
ws_connection.close()  # explicitly close connection
# after closing we can not use connection anymore, if you need one - create one more connection with surreal object
```


## Results and RecordID ##
If method of connection not raised it is always returns SurrealResult object on any response of SurrealDB. It was chosen for simplicity.

Here is standard result:
`SurrealResult(id='8ad04f2f-8ec7-4a86-98ba-e0d147fd4a7d', error=None, result=None, code=None, token=None, status='OK', time='')`

Here is standard error:
`SurrealResult(id='9f3afdf6-c66c-468f-85e7-27f0f228ea6c', error={'code': -32000, 'message': "There was a problem with the database: Can not execute KILL statement using id '$id'"}, result=None, code=None, token=None, status='OK', time='')`

You can always check for error, using is_error() method
```python
if result.is_error():
    raise ValueError("Got error")
```

You need read this on SurrealDB recordID: https://docs.surrealdb.com/docs/surrealql/datamodel/ids

For support and compatibility reasons there are many way to specify recordID in method.
Let's consider CREATE method for example:
```python
# all the same
ws_connection.create("person", {"id":"john", "name":"John Doe"})
ws_connection.create("person:john", {"name":"John Doe"})
ws_connection.create("person", {"name":"John Doe"}, record_id="john")
```
These function calls are the same, so, as you can see, recordID can be specified:
 - in data json (if data allowed in method)
 - in table name after colon, for example "person:john"
 - in record_id argument

**Attention!** Using recordID 2 or 3 times in one method will cause error on SurrealDB side, for example
`ws_connection.select("person:john", record_id="john")` is invalid call, id should be specified only once.

**Important note:** uuid-type recordID, like 8424486b-85b3-4448-ac8d-5d51083391c7 should be specified with "`" backticks, for example
```python
ws_connection.select("person:`8424486b-85b3-4448-ac8d-5d51083391c7`")
ws_connection.select("person", record_id="`8424486b-85b3-4448-ac8d-5d51083391c7`")
```
otherwise you cant find your record

**Note:** record_id parameter of methods is only concatenate with table_name and colon, so
ws_connection.select("person", record_id="john") under the hood became
ws_connection.select("person:john"), but no other logic performed. Do not expect we specified "`" for you.


## Debug mode ##
As it was said, if you need to debug something, stuck in some problem or just want to know all about data between you and SurrealDB, you can use log level.
If you specify "INFO" level, then you will see transport operations, which methods were called, which parameters were used.
For example

**Example 5**

```python
from surrealist import Surreal

surreal = Surreal("http://127.0.0.1:8000", namespace="test", database="test", credentials=("root", "root"),
                  log_level="INFO")
with surreal.connect() as connection:
    res = connection.create("article", {"author": "John Doe", "title": "In memoriam", "text": "text"})

```
if you run it, you get in console:
```
2024-02-02 18:31:09,419 : Thread-1 : websocket : INFO : Websocket connected
2024-02-02 18:31:09,521 : MainThread : websocket_connection : INFO : Operation: SIGNIN. Data: {'user': 'root', 'pass': '******', 'NS': 'test', 'DB': 'test'}
2024-02-02 18:31:09,627 : MainThread : websocket_connection : INFO : Got result: SurrealResult(id='836a2834-c6d5-416c-a840-6322a17b47cc', error=None, result='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpYXQiOjE3MDY4ODA2NjksIm5iZiI6MTcwNjg4MDY2OSwiZXhwIjoxNzA2ODg0MjY5LCJpc3MiOiJTdXJyZWFsREIiLCJOUyI6InRlc3QiLCJEQiI6InRlc3QiLCJJRCI6InJvb3QifQ.mrzxXkva3lCg6EihtUEx8c1yjOtuJt_EvJninTqxJ_1...
2024-02-02 18:31:09,627 : MainThread : websocket_connection : INFO : Connected to ws://127.0.0.1:8000/rpc, params: {'NS': 'test', 'DB': 'test'}, credentials: ('root', '******'), timeout: 5
2024-02-02 18:31:09,627 : MainThread : websocket_connection : INFO : Operation: CREATE. Path: article, data: {'author': 'John Doe', 'title': 'In memoriam', 'text': 'text'}
2024-02-02 18:31:09,733 : MainThread : websocket_connection : INFO : Got result: SurrealResult(id='0870492e-faba-4a5f-b454-c7f7315348bd', error=None, result=[{'author': 'John Doe', 'id': 'article:pt0907zkhkhb94evjnze', 'text': 'text', 'title': 'In memoriam'}], code=None, token=None, status='OK', time='')
2024-02-02 18:31:09,734 : MainThread : connection : INFO : Connection was closed
```
but if in example above (example 5) you choose "DEBUG", you will see all, including low-level clients data:
```
2024-02-02 18:33:15,119 : MainThread : root : DEBUG : Log level switch to DEBUG
2024-02-02 18:33:15,124 : Thread-1 : websocket : INFO : Websocket connected
2024-02-02 18:33:15,223 : MainThread : websocket_client : DEBUG : Connected to ws://127.0.0.1:8000/rpc, timeout is 5 seconds
2024-02-02 18:33:15,223 : MainThread : websocket_connection : INFO : Operation: SIGNIN. Data: {'user': 'root', 'pass': '******', 'NS': 'test', 'DB': 'test'}
2024-02-02 18:33:15,224 : MainThread : websocket_client : DEBUG : Send data: {"id": "5a2e9c12-e03e-4879-a78a-bd360cd871b1", "method": "signin", "params": [{"user": "root", "pass": "******", "NS": "test", "DB": "test"}]}
2024-02-02 18:33:15,281 : Thread-1 : websocket_client : DEBUG : Get message b'{"id":"5a2e9c12-e03e-4879-a78a-bd360cd871b1","result":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpYXQiOjE3MDY4ODA3OTUsIm5iZiI6MTcwNjg4MDc5NSwiZXhwIjoxNzA2ODg0Mzk1LCJpc3MiOiJTdXJyZWFsREIiLCJOUyI6InRlc3QiLCJEQiI6InRlc3QiLCJJRCI6InJvb3QifQ.2ekRL9EyiaWOQR0Aw1qX8VE5S822Kab5SiYLHLC3YkPX3_Yu-FkWSCoP3XGoUg9w8'...
2024-02-02 18:33:15,326 : MainThread : websocket_connection : INFO : Got result: SurrealResult(id='5a2e9c12-e03e-4879-a78a-bd360cd871b1', error=None, result='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpYXQiOjE3MDY4ODA3OTUsIm5iZiI6MTcwNjg4MDc5NSwiZXhwIjoxNzA2ODg0Mzk1LCJpc3MiOiJTdXJyZWFsREIiLCJOUyI6InRlc3QiLCJEQiI6InRlc3QiLCJJRCI6InJvb3QifQ.2ekRL9EyiaWOQR0Aw1qX8VE5S822Kab5SiYLHLC3YkP...
2024-02-02 18:33:15,326 : MainThread : websocket_connection : INFO : Connected to ws://127.0.0.1:8000/rpc, params: {'NS': 'test', 'DB': 'test'}, credentials: ('root', '******'), timeout: 5
2024-02-02 18:33:15,326 : MainThread : websocket_connection : INFO : Operation: CREATE. Path: article, data: {'author': 'John Doe', 'title': 'In memoriam', 'text': 'text'}
2024-02-02 18:33:15,326 : MainThread : websocket_client : DEBUG : Send data: {"id": "145b2ed4-9b42-44ab-ade2-e28a27730faa", "method": "create", "params": ["article", {"author": "John Doe", "title": "In memoriam", "text": "text"}]}
2024-02-02 18:33:15,327 : Thread-1 : websocket_client : DEBUG : Get message b'{"id":"145b2ed4-9b42-44ab-ade2-e28a27730faa","result":[{"author":"John Doe","id":"article:s0coora4gedavt2skd36","text":"text","title":"In memoriam"}]}'
2024-02-02 18:33:15,432 : MainThread : websocket_connection : INFO : Got result: SurrealResult(id='145b2ed4-9b42-44ab-ade2-e28a27730faa', error=None, result=[{'author': 'John Doe', 'id': 'article:s0coora4gedavt2skd36', 'text': 'text', 'title': 'In memoriam'}], code=None, token=None, status='OK', time='')
2024-02-02 18:33:15,433 : MainThread : connection : INFO : Connection was closed
2024-02-02 18:33:15,434 : MainThread : websocket_client : DEBUG : Client is closed connection to ws://127.0.0.1:8000/rpc
```

**Note:** passwords and auth information always masked in logs. If you still see it in logs - please, report an issue

## Live Query ##
Live queries let you subscribe on events of desired table, when changes happen - you get notification as simple result or in DIFF format

About live query: https://surrealdb.com/products/lq

Using live select: https://docs.surrealdb.com/docs/surrealql/statements/live-select

About DIFF (jsonpatch): https://jsonpatch.com

LQ can work only with websockets, you have to provide callback function to call on any event.

Callback should have signature `def any_name(param: Dict) -> None`, so it will be called with python dictionary as only argument

**Note 1:** if your connection was interrupted or closed, LQ will disappear, and you need to recreate it

**Note 2:** LQ only produce events which happen after creation of this LQ

**Note 3:** LQ is associated with connection, where it was created, if you have 2 or more connections, LQ will depends only on one, 
and will disappear on connection close, even if other connections still active

**Example 6**

```python
from time import sleep
from surrealist import Surreal


# you need callback, a function which will get dictionary and do something with it
def call_back(response: dict) -> None:
    print(response)


# you need websockets for live query
surreal = Surreal("http://127.0.0.1:8000", namespace="test", database="test", credentials=("root", "root"))
with surreal.connect() as connection:
    res = connection.live("person", callback=call_back)  # here we subscribe on person table
    live_id = res.result  # live_id is a LQ id, we need it to kill query
    connection.create("person", {"name": "John", "surname": "Doe"})  # here we create an event
    sleep(0.5)  # sleep a little cause need some time to get message back
```
in console you will get:
`{'result': {'action': 'CREATE', 'id': 'c2c8952b-b2bc-4d3a-aa68-4609f5818d7c', 'result': {'id': 'person:dik1sm50xr2d5mc7fysi', 'name': 'John', 'surname': 'Doe'}}}`

**Example 7**

```python
from time import sleep
from surrealist import Surreal


# you need callback, a function which will get dictionary and do something with it
def call_back(response: dict) -> None:
    print(response)


# you need websockets for live query
surreal = Surreal("http://127.0.0.1:8000", namespace="test", database="test", credentials=("root", "root"))
with surreal.connect() as connection:
    # here we subscribe on person table and specify we need DIFF
    res = connection.live("person", callback=call_back, return_diff=True)
    live_id = res.result  # live_id is a LQ id, we need it to kill query
    connection.create("person", {"name": "John", "surname": "Doe"})  # here we create an event
    sleep(0.5)  # sleep a little cause need some time to get message back
    connection.kill(live_id)  # we kill LQ, no more events to come
```
in console you will get:
`{'result': {'action': 'CREATE', 'id': '54a4dd0b-0008-46f4-b4e6-83e466cb4141', 'result': [{'op': 'replace', 'path': '/', 'value': {'id': 'person:fhglyrxkit3j0fnosjqg', 'name': 'John', 'surname': 'Doe'}}]}}`

If you do not need LQ anymore, -call KILL method, with live_id

## Threads and thread-safety ##
This library were made for using in multithreaded environments, just remember some rules of thumb:
 - if you work with only one server of SurrealDB, you need only one Surreal object
 - one Connection object represents exactly one connection (websocket or http) with DB
 - it is OK to use connection in different threads, but it can be your bottleneck, as there is only one connection to DB
 - with many queries and high load you should consider using more than 1 connection, but not too much of them. Number of connections equal to number of CPU-cores is the best choice
 - do not forget to properly close connections

## Recursion and JSON in Python ##
SurrealDb has _"no limit to the depth of any nested objects or values within"_, but in Python we have a recursion limit and
standard json library (and str function) use recursion to load and dump objects, so if you will have deep nesting in your objects - 
you can get RecursionLimitError. 

The best choice here is to rethink your schema and objects, because you probably do 
something wrong with such high level of nesting. 

Second choice - increase recursion limit in your system with
```python
import sys
sys.setrecursionlimit(10_000)
```

### Contacts ###
Mail me at farofwell@gmail.com