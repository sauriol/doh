# Notes
  - Server
    - Must support both POST and GET
      - POST:
        - Variables are not processed
        - DNS query is included as the message body
        - Content-Type header indicates media type
      - GET:
        - The variable `dns` is processed as a DNS query
          - The query is encoded with base64url
    - Must be able to process `application/dns-message` requests
    - A successful HTTP response with a 2xx status code is used for any valid
      DNS response
      - Doesn't matter if the response is NXDOMAIN
    - HTTP responses with non-successful HTTP status codes do not contain a
      reply to the original query
    - Must be HTTPS
      - Not HTTP
    - Should assign explicit HTTP freshness lifetime
      - Not sure if this one is possible
      - The assigned freshness must be less than or equal to the smallest TTL
        in the Answer section of the DNS response
      - If there are no responses in the Answer section, the assigned freshness
        must not be greater than the minimum field from the SOA record
    - HTTP/2 is the minimum recommended version of HTTP
  - Client
    - Should include an HTTP Accept request header
      - Indicates type of content client can understand
    - Client must be able to process `application/dns-message`
    - DNS ID should be 0
    - May use HTTP/2 padding and compression
    - Must account for the Age response header field's value when calculating
      the DNS TTL of a response
