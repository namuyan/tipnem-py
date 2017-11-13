#!/user/env python3
# -*- coding: utf-8 -*-

from tipnem import WebSocketClient
from ed25519 import Ed25519
import time

print("""
【送金GOX対応ツール】
送金時にTagを入れ忘れてGOXしてしまった時に使用するツールです。

：手順
１、Tipnemにログインし、Level1になります。
２、送金時に用いたアドレスの秘密鍵を取得します。
３、GOXしたtxhashを取得します。
４、署名を作成し秘密鍵を削除し送信します。(自動)
５、成功メッセージを確認します。
""")

ws = WebSocketClient(url="ws://153.122.86.46:8088")
ws.start()


print("""
１、Twitter名を入力しましょう。
"@example_name" の場合は "example_name"と入力
""")
ws.login_by_pin_guest(screen=input(" >> "))


print("""
２、秘密鍵を入力します。
秘密鍵は他人に知られると残高を勝手に操作される可能性があります。
取り扱いには十分注意して下さい！
""")
while True:
    sec_ley = input(" >> ")
    sec_ley = sec_ley.lower().lstrip().rstrip()
    if len(sec_ley) != 64:
        print("Error:正しい形式の秘密鍵ではありません。空白などが混在していませんか？")
    try:
        int(sec_ley, 16)
        break
    except Exception as e:
        print("Error:%s" % e)


print("""
３、GOXしたtxhash(トランザクションハッシュ)を入力します。
txhashの取得方法は、まずnanowalletのダッシュボードを開きます。
次にGOXした送金をクリックし"ハッシュ"の右の16進数を探します。
16進数とは 63f52c2998d2 のような0-9とa-fの文字で表された文字列です。
長くて特徴的な見た目なのでわかりやすいと思います。
""")
while True:
    tx_hash = input(" >> ")
    tx_hash = tx_hash.lower().lstrip().rstrip()
    if len(tx_hash) != 64:
        print("Error:正しい形式のハッシュではありません。空白などが混在していませんか？")
        print("`%s`" % tx_hash)
    try:
        int(tx_hash, 16)
        break
    except Exception as e:
        print("Error:%s" % e)

print("４、署名を作成します。")
message = ws.user_code + tx_hash
ecc = Ed25519()
pub_key = ecc.public_key(sk=sec_ley).decode()
sign = Ed25519.sign(message=message, secret_key=sec_ley, public_key=pub_key).decode()
time.sleep(1)

print("４、秘密鍵を削除します。")
del sec_ley
del ecc
time.sleep(1)

print("４、署名を送信します。")
data = {
    'txhash': tx_hash,
    'sign': sign,
    'pubkey': pub_key
}
ok, result = ws.request(command="nem/lost", data=data)
if not ok:
    print("""
    ５、失敗しました。
    REASON: %s""" % result)

else:
    print("""
    ５、成功しました。
    接続を切断します。""")

while True:
    time.sleep(10)

