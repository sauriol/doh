#!/usr/bin/env python3

import base64
import logging
from quart import Quart, abort, request, Response
import dns.query
import dns.zone
import sys
import os
import argparse


app = Quart(__name__)

allowed_content_types = ['application/dns-message']

# Instantiate logger and disable some of the default quart logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger('hpack.hpack').setLevel(logging.ERROR)

# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument('--zone-file', dest='filename', default=None,
                    metavar='filename', type=str)
parser.add_argument('--resolver', dest='resolver', default='8.8.8.8', type=str,
                    help='Resolver to use if not resolving from a zone file')
args = parser.parse_args()

# If a zone file has been passed, open it for reading
if args.filename:
    zonefile = open(args.filename, 'r')
    zone = dns.zone.from_file(zonefile, args.filename)


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
        req = base64.urlsafe_b64decode(req + pad)
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

    if args.filename:
        answer_list = list()

        # Search for responses in the zone file and build a list
        for query in message.question:
            querytype = query.rdtype
            queryname = query.name
            data = zone.find_rrset(queryname, querytype)

            answer_list.append(data)

        # Build the response and add the answers
        resp = dns.message.make_response(message)
        resp.answer = answer_list

        # Convert to wire, passing the origin for appending to the names
        wire_resp = resp.to_wire(dns.zone.Zone(args.filename).origin)

    else:
        # Resolve by querying a configured server
        resp = dns.query.udp(message, args.resolver)

        wire_resp = resp.to_wire()

    least_ttl = 3600
    for answer in resp.answer:
        if answer.ttl < least_ttl:
            least_ttl = answer.ttl

    return Response(wire_resp,
                    status=200,
                    mimetype='application/dns-message',
                    headers={'Cache-Control': str(least_ttl)})


if __name__ == '__main__':
    app.run(
        host='localhost',
        port=8080,
        certfile='cert.pem',
        keyfile='key.pem'
        )
