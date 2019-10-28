#!/usr/bin/env python3

from quart import Quart, abort, request, Response
import dns.query

app = Quart(__name__)
allowed_content_types = ['application/dns-message']

@app.route('/dns', methods=['GET', 'POST'])
async def serve():
    if request.method == 'POST':
        if request.headers.get('Content-Type') not in allowed_content_types:
            abort(415)
        data = await request.get_data()
        req = bytes(data)
    elif request.method == 'GET':
        return 'GET'
    else:
        abort(405)

    try:
        message = dns.message.from_wire(req)
    except Exception as e:
        print(e)
        return Response('Error parsing DNS message: ' + str(e),
                status=400, mimetype='text/plain')


if __name__ == '__main__':
    app.run(
        host='localhost',
        port=8080,
        certfile='cert.pem',
        keyfile='key.pem')
