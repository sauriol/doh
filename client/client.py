#!/usr/bin/env python3

import requests
import argparse
import dns.message
import dns.rdatatype
import base64


def main():
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

    resp = args.req(args.label, args.uri, args.type)

    message = dns.message.from_wire(resp)

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


def get(label, uri, dnstype):
    rdtype = dns.rdatatype.from_text(dnstype)
    query = dns.message.make_query(label, rdtype).to_wire()

    query_url = base64.urlsafe_b64encode(query)

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


def post(label, uri, dnstype):
    rdtype = dns.rdatatype.from_text(dnstype)
    query = dns.message.make_query(label, rdtype).to_wire()

    resp = requests.post(uri, data=query, headers={'Content-Type': 'application/dns-message'})

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
