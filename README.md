# python-socket-http
## An Simple Web Server Depends on Python's Socket Library.

### Featers
+ Depend on socket.
+ Support cross origin. (Access-Control-Allow-Origin: *)
+ Stop service by GET request /break from 127.0.0.1. (http://127.0.0.1/break)

### Limit
+ Only support GET method now.
+ Receive 1024 bytes per request.
+ Only support minetypes like text/html, text/css, text/plain, application/javascript, image/jpg, image/gif.
+ Oly support statuscode like 200, 404, 501.

