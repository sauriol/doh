#!/usr/bin/env python3

from quart import Quart, abort, request

app = Quart(__name__)

@app.route('/dns', methods=['GET', 'POST'])
async def dns():
    if request.method == 'GET':
        return 'GET'
    elif request.method == 'POST':
        return 'POST'
    else:
        abort(405)


if __name__ == '__main__':
    app.run(
        host='localhost',
        port=8080,
        certfile='cert.pem',
        keyfile='key.pem')
