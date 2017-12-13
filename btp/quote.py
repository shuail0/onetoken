import asyncio
import aiohttp
import json

from btp import Ticker


class Quote:
    def __init__(self, host=None):
        self.sess = None
        self.ws = None
        self.last_tick_dict = {}
        self.host = 'http://alihk-debug.qbtrade.org:3014/ws' if not host else host

    def error(self, e, msg):
        if self.sess:
            self.sess.close()

    async def init(self):
        print(f'Connecting to {self.host}')
        try:
            self.sess = aiohttp.ClientSession()
            self.ws = await self.sess.ws_connect(self.host, autoping=False)
        except Exception as e:
            self.error(e, 'try connect to WebSocket failed...')
        else:
            print('Connected to WS')

            asyncio.ensure_future(self.on_msg())

    async def on_msg(self):
        while not self.ws.closed:
            msg = await self.ws.receive()
            try:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    # print(msg.data)
                    self.parse_tick(msg.data)
                elif msg.type == aiohttp.WSMsgType.CLOSED:
                    print('closed')
                    break
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    print('error', msg)
                    break
            except Exception as e:
                print('ws was disconnected...')
                print(e)

    # await ws.send_json({'uri': 'subscribe-single-tick-verbose', 'contract': 'btc.usd:xtc.bitfinex'})

    def parse_tick(self, plant_data):
        try:
            data = json.loads(plant_data)
            # print(data)
            if 'uri' in data and data['uri'] == 'single-tick-verbose':
                tick = Ticker.from_dict_v2(data['data'])
                self.last_tick_dict[tick.contract] = tick
        except:
            print('parse error')

    async def subscribe_tick(self, contract):
        if self.ws:
            await self.ws.send_json({'uri': 'subscribe-single-tick-verbose', 'contract': contract})
        else:
            print('ws is not ready...')

    def get_last_tick(self, contract):
        return self.last_tick_dict.get(contract, None)

# if __name__ == '__main__':
#     asyncio.get_event_loop().run_until_complete(main())
