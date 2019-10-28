#!/usr/bin/env python3

from quart import Quart, abort, request

app = Quart(__name__)
allowed_content_types = ['application/dns-message']

@app.route('/dns', methods=['GET', 'POST'])
async def dns():
    if request.method == 'GET':
        if request.headers.get('Content-Type') not in allowed_content_types:
            abort(415)
        data = request.get_data()
        req = bytes(data)
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
