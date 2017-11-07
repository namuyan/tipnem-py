#!/user/env python3
# -*- coding: utf-8 -*-

import websocket
import threading
import logging
import time
import json
import random

"""
Tipnemを扱うライブラリ
2017/11/07
"""

version = "1.0"
author = "namuyan"


class WebSocketClient:
    timeout = 60
    result = dict()
    result_lock = threading.Lock()
    user_code = None
    height = 0

    def __init__(self, url, test=False):
        self.url = url
        self.test = test
        self.ws = None

    def create_connect(self):
        retry = 0
        while True:
            try:
                retry += 1
                websocket.enableTrace(self.test)
                ws = websocket.WebSocketApp(self.url)
                ws.on_message = self.on_message
                ws.on_close = self.on_error
                ws.on_open = self.on_open
                ws.on_error = self.on_error
                ws.run_forever()
            except Exception as e:
                logging.error(e)
                logging.error("# retry connect to tipnem after 180s, %s" % retry)
                time.sleep(180)

    def start(self, name="tipnem"):
        threading.Thread(
            target=self.create_connect, name=name, daemon=True
        ).start()
        while self.ws is None:
            time.sleep(0.2)
        logging.debug("# create ws connection")

    def blocking(self, uuid):
        time_span = 0.005  # 1mS
        for c in range(int(self.timeout / time_span)):
            time.sleep(time_span)
            with self.result_lock:
                if uuid not in self.result:
                    continue
                else:
                    data = self.result[uuid]
                    del (self.result[uuid])
                return data['result'], data
        else:
            raise TimeoutError("UUID [%s]" % uuid)

    def request(self, command, data=None, blocking=True):
        uuid = random.randint(1, 2147483647)
        message = {
           "command": command,
           "data": data,
           "uuid": uuid
        }
        self.ws.send(json.dumps(message))
        if blocking is False:
            return uuid

        time_span = 0.005  # 1mS
        for c in range(int(self.timeout / time_span)):
            time.sleep(time_span)
            with self.result_lock:
                if uuid not in self.result:
                    continue
                else:
                    r = self.result[uuid]
                    del(self.result[uuid])
                return r['result'], r['data']
        else:
            raise TimeoutError("[%s] [%s]" % (command, data))

    """ request """
    @staticmethod
    def check_key(keys, data):
        for k in keys:
            if k not in data:
                return False
        else:
            return True

    def on_message(self, ws, message):
        logging.debug("msg: %s" % message)
        try:
            data = json.loads(message)
        except Exception as e:
            logging.error(e)
            return
        if self.check_key(('level', 'user_code'), data):
            self.user_code = data['user_code']
            return

        elif self.check_key(('type', 'command'), data):
            if data['type'] == 'streaming':
                if data['command'] == 'nis/block':
                    self.on_nis_block(ws, data['data'])
                elif data['command'] == 'nis/incoming':
                    self.on_nis_incoming(ws, data['data'])
                elif data['command'] == 'tip/receive':
                    self.on_tip_receive(ws, data['data'])
                else:
                    raise Exception("unknown command '%s'" % data['command'])

            elif data['type'] == 'request':
                with self.result_lock:
                    self.result[data['uuid']] = data

            else:
                raise Exception("unknown type '%s'" % data['type'])
            return

        else:
            raise Exception("none...")

    def on_error(self, ws, error):
        logging.error("error: %s" % error)
        # self.ws.close()

    def on_close(self, ws):
        logging.debug("close: %s" % ws)
        # self.ws.close()
        # time.sleep(5)
        # logging.debug("try reconnect")
        # self.create_connect()

    def on_open(self, ws):
        self.ws = ws
        logging.debug("open: %s" % ws)

    """ streaming """
    def on_nis_block(self, ws, data):
        if self.height != data['height']:
            logging.info("nis/block  %s" % data)
            self.height = data['height']

    def on_nis_incoming(self, ws, data):
        logging.info("nis/incoming  %s" % data)
        pass

    def on_tip_receive(self, ws, data):
        logging.info("tip/receive  %s" % data)
        pass


""" テストコード """
if __name__ == '__main__':
    def on_nis_block_overwrite(ws, data):
        print(data)
        print("GET!")

    ws = WebSocketClient(url="ws://153.122.86.46:8088")
    # ws.on_nis_block = on_nis_block_overwrite  # 上書きする
    ws.start()
    print(ws.request(command="bot/info"))

    while True:
        print()
        screen = input("screen >> ")
        data = {"screen_name": screen}
        ok, result = ws.request(command="user/offer", data=data)
        if not ok and result != "pincode has been already created.":
            print("# failed login: ", result)
            continue

        pin_code = input("pincode >> ")
        data = {"screen_name": screen, "pincode": int(pin_code)}
        ok, result = ws.request(command="user/check", data=data)
        if not ok:
            print("# failed login: ", result)
            continue

        print("# login OK!")
        while True:
            try:
                print()
                command = input("cmd >> ")
                data = json.loads(input("data >> "))
                ok, result = ws.request(command=command, data=data)
                print(ok)
                print(result)
            except:
                pass