#!/usr/bin/env python3

import base64
import logging
from quart import Quart, abort, request, Response
import dns.query
import sys

app = Quart(__name__)
allowed_content_types = ['application/dns-message']

logging.basicConfig(level=logging.DEBUG)

logging.getLogger('hpack.hpack').setLevel(logging.ERROR)

@app.route('/dns', methods=['GET', 'POST'])
async def serve():
    logging.debug(request.method + ' request received')
    if request.method == 'POST':
        # Extract the data from the post body
        if request.headers.get('Content-Type') not in allowed_content_types:
            abort(415)
        data = await request.get_data()
        req = bytes(data)

        logging.debug('Retrieved data from POST body')

    elif request.method == 'GET':
        # Extract the message from the parameter
        req = request.args.get('dns')
        if req == None:
            logging.error('Received GET request without dns parameter')

            return Response('Error extracting dns parameter from URI',
                            status=400, mimetype='text/plain')

        # Once request is extracted, base64 decode
        pad = '=' * (-len(req) % 4)
        req = base64.urlsafe_b64decode(dns + pad)
    else:
        abort(405)

    # Interpret the bytes as a dns message
    try:
        message = dns.message.from_wire(req)
    except Exception as e:
        print(e)
        return Response('Error parsing DNS message: ' + str(e),
                status=400,
                mimetype='text/plain')

    logging.debug('Successfully interpreted query for ' + str(message.question))

    # Check message ID
    if message.id != 0:
        logging.error('Received request with id ' + str(message.id))

    resp = dns.query.udp(message, '8.8.8.8')

    # TODO: query SOA instead of assuming default of 3600
    least_ttl = 3600
    for answer in resp.answer:
        if answer.ttl < least_ttl:
            least_ttle = answer.ttl

    return Response(resp.to_wire(),
                    status=200,
                    mimetype='application/dns-message',
                    headers={'Cache-Control': str(least_ttl)})


if __name__ == '__main__':
    app.run(
        host='localhost',
        port=8080,
        certfile='cert.pem',
        keyfile='key.pem')
        )
