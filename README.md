tipnem-py
=========
![ねむりん](nemurin.png)

[Tipnem](https://namuyan.github.io/nem-tip-bot/index)を扱う為のライブラリ。  
Python3で動きます。

Requirement
----------
[websocket-client](https://github.com/websocket-client/websocket-client)

## テストコードを走らせる。
![tipnempy1](tipnempy1.png)  
ログインして適当なコマンドを送る。
```bash
python3 tipnem.py
```

***

## ソースに組み込む。
* `request` の送り方
```python
from tipnem import WebSocketClient
ws = WebSocketClient("ws://153.122.86.46:8088")
ws.start()
 
# コマンドをリクエスト(okがTrueでなければresultにエラー文)
ok, result = ws.request("bot/info")
 
# リクエストをBlockingせずに使用(意味あるｺﾚ)
uuid = ws.request("bot/info", blocking=False)
ok, result = ws.blocking(uuid)
```

Streamingを取得するには
```python
from tipnem import WebSocketClient
ws = WebSocketClient("ws://153.122.86.46:8088")
ws.start()
 
while True:
    cmd, data, time_sec = ws.streaming_que.get()
```

ログインするには
```python
from tipnem import WebSocketClient
ws = WebSocketClient("ws://153.122.86.46:8088")
ws.start()
 
# PINコードでログイン
ws.login_by_pin_guest(screen="example_name") # level1
ws.login_by_pin_user() # level2
 
# 公開鍵でログイン
seckey = "2fa58d280902095a28601840ff392381d5313716ef0dbf06beb202bc2a880f9b"
pubkey = "06cdabf0fd421d88983f7beb849cd804a4876276728d44473d62b47f4146c3ac"
if ws.login_by_key(seckey=seckey, pubkey=pubkey, screen="example_name"):
    print("login成功 level:%d" % ws.level)
else:
    print("login失敗!")
```
## 履歴
* ver 2.0  
    streamingの取得方法を変更、queueによりSocketのブロッキングを防ぐ。  
    PIN認証、や公開鍵認証でログインできるように。
    
* ver 1.0  
    公開開始

## Licence
MIT