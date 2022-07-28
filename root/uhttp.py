import urequests as requests
import uasyncio as asyncio
import ujson as json
import usys as sys


class Error(Exception):
    def __init__(self, status, message=None):
        self.status = status
        self.message = message


class Request:
    def __init__(self, method, url, headers, body):
        self.method = method
        self.url = url
        self.body = body
        self.headers = headers     

    async def text(self):
        if not self.headers[b"Content-Type"].startswith("text/"):
            raise Error(400, "Bad Request")

        return self.body.readexactly(int(self.headers["content-length"]))

    async def json(self):
        if not self.headers[b"Content-Type"].startswith(b"application/json"):
            raise Error(400, "Bad Request")

        size = int(self.headers[b"Content-Length"])
        data = await self.body.readexactly(size)

        return json.loads(data)


async def read_request(stream):
    start_line = await stream.readline()
    method, url, _version = start_line.split() 
    headers = {}

    while True:
        line = await stream.readline()
        if line == b"\r\n":
            break
    
        key, value = line.split(b":", 1)
        headers[key] = value.strip()

    return Request(method, url, headers, stream)  


class Response:
    def __init__(self, status=200, message=None, headers=None, body=None):
        self.status = status
        self.message = message if message is not None else ""
        self.headers = headers if headers is not None else {}
        self.body = body

    def json(data, headers=None, **kwargs):
        headers = {} if headers is None else headers
        headers["Content-Type"] = "application/json"

        def generator():
            yield json.dumps(data)
            yield b"\r\n"

        body = generator()

        return Response(headers=headers, body=body, **kwargs)

    def html(file, headers=None, **kwargs):
        headers = {} if headers is None else headers
        headers["Content-Type"] = "text/html"

        return Response.file(file, headers=headers, **kwargs)

    def file(file, chunk_size=32, **kwargs):
        def generator():
            while True:
                chunk = file.read(chunk_size)
                if not chunk: break
                yield chunk

        return Response(body=generator(), **kwargs)


async def write_response(response, stream):
    stream.write(b"HTTP/1.1 {status} {message}\r\n".format(status=response.status, message=response.message))

    if response.headers:
        for key, value in response.headers.items():
            stream.write(b"{key}: {value}\r\n".format(key=key, value=value))
        stream.write(b"\r\n")

    if response.body:
        for chunk in response.body:
            stream.write(chunk)

    await stream.drain()
    stream.close()
    await stream.wait_closed()


class Server:

    def __init__(self):
        self.routes = {}

    def route(self, url, method="GET"):
        def wrapper(f):
            self.routes[(bytes(method, "utf-8"), bytes(url, "utf-8"))] = f
            return f

        return wrapper   

    async def start(self, host="0.0.0.0", port=80):
        print(f"starting server")
        return await asyncio.start_server(self.serve, host, port)

    async def handle(self, request):
        if not (request.method, request.url) in self.routes:
            raise Error(404, "Not Found")

        return await self.routes[(request.method, request.url)](request)


    async def serve(self, reader, writer):
        peer = writer.get_extra_info('peername')
        print(f"serving client:", peer)

        try:
            request = await read_request(reader)
            response = await self.handle(request)
            await write_response(response, writer)
        except Error as e:
            print("http error:", e)
            await write_response(Response.json({"error": str(e)}, status=e.status, message=e.message), writer)
        #except Exception as e:
        #    print("server error:", e)
        #    await write_response(Response.json({"error": str(e)}, status=500, message="Internal Server Error"), writer)
        except KeyboardInterrupt as e:
            print("keyboard interrupt:", e)
            sys.exit(0)
        finally:
            pass