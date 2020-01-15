#!/usr/bin/env python3

import requests
import argparse
import dns.message
import dns.rdatatype
import base64


def main():
    # Parse the arguments
    parser = argparse.ArgumentParser(description='A basic DoH client')
    parser.add_argument('label', metavar='label', type=str,
                        help='The label to make the query for')
    parser.add_argument('uri', metavar='uri', type=str,
                        help='The URI template to make the query to')
    parser.add_argument('type', metavar='type', type=str, default='A',
                        help='The type to query for')
    parser.add_argument('--get', dest='req', action='store_const',
                        const=get, default=post,
                        help='Make a GET request instead of POST')
    parser.add_argument('--insecure', action='store_true',
                        help='Ignore TLS/SSL issues')
    args = parser.parse_args()

    # Build the response, using the values determined from the arguments
    resp = args.req(args.label, args.uri, args.type)
    message = dns.message.from_wire(resp)

    # If NoError, print message info
    if message.rcode() == 0:
        print('Question:')
        for result in message.question:
            print('\t' + str(result))

        print('\nAnswer:')
        for result in message.answer:
            print('\t' + str(result))

        print('\nAuthority:')
        for result in message.authority:
            print('\t' + str(result))

        print('\nAdditional:')
        for result in message.additional:
            print('\t' + str(result))
    elif message.rcode() == 3:
        print('Got NXDOMAIN, label does not exist\n')
        print('Question:')
        for result in message.question:
            print('\t' + str(result))

        print('\nAuthority:')
        for result in message.authority:
            print('\t' + str(result))

        print('\nAdditional:')
        for result in message.additional:
            print('\t' + str(result))
    else:
        print('Error, got rcode ' + str(message.rcode()))


# Get the data with a GET request
def get(label, uri, dnstype):
    # Build the wire request
    rdtype = dns.rdatatype.from_text(dnstype)
    query = dns.message.make_query(label, rdtype)
    query.id = 0
    query_wire = query.to_wire()

    # Build the query url
    query_url = base64.urlsafe_b64encode(query_wire)
    req_uri = uri + '?dns=' + query_url.decode('utf-8')

    resp = requests.get(req_uri)
    try:
        resp.raise_for_status()
    except requests.HTTPError as e:
        print('HTTP error occurred: ' + str(e))
    except Exception as e:
        print('Error occurred: ' + str(e))
    else:
        return resp.content


# Get the data with a POST request
def post(label, uri, dnstype):
    # Build the wire request
    rdtype = dns.rdatatype.from_text(dnstype)
    query = dns.message.make_query(label, rdtype)
    query.id = 0
    query_wire = query.to_wire()

    resp = requests.post(uri, data=query_wire,
                         headers={'Content-Type': 'application/dns-message'})
    try:
        resp.raise_for_status()
    except requests.HTTPError as e:
        print('HTTP error occurred: ' + str(e))
    except Exception as e:
        print('Error occurred: ' + str(e))
    else:
        return resp.content


if __name__ == '__main__':
    main()
