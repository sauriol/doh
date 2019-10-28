#!/usr/bin/env python3

from quart import Quart

app = Quart(__name__)

@app.route('/dns')
async def dns():
    return 'test'


if __name__ == '__main__':
    app.run(
        host='localhost',
        port=8080,
        certfile='cert.pem',
        keyfile='key.pem')
