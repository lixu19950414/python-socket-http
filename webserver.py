# coding=utf-8

import socket
import time
import os


# Global configs
CONFIGS = {
	'rootdir': "/Users/lixu-mac/Desktop/python-socket-http/tests/txt",
	'host': "",
	'port': 8084,
}

# Break loop point
g_Break = False

# Thread function
def StartService():
	global g_Break
	g_Break = False
	svr = WebServer()
	svr.Run()

# Close socket
def StopService():
	global g_Break
	g_Break = True

# Parse HTTP GET requests
# Returns status_code, path, headers_dic, args_dic
def AnyliseRequest(req):
	headers = {}
	args = {}
	path = ""
	if not req.endswith("\r\n\r\n"):
		Print("[BreakPoint 1]")
		return 501, path, headers, args
	if not req.startswith("GET"):
		Print("[BreakPoint 2]")
		return 501, path, headers, args
	sp = req.split("\r\n")
	if not len(sp) >= 3:
		Print("[BreakPoint 3]")
		return 501, path, headers, args

	# Get path and args
	print sp[0]
	sp1 = sp[0].split(" ")
	if len(sp1) >= 3:
		p = sp1[1]  # p: /jsdge?args=xxx
		sp2 = p.split("?")
		path = sp2[0]
		if len(sp2) > 1:
			a = "?".join(sp2[1:])
			for sa in a.split("&"):
				saa = sa.split("=")
				if len(saa) == 2:
					args[saa[0]] = saa[1]
				else:
					Print("[BreakPoint 4]")
					return 501, path, headers, args
	else:
		return 501, path, headers, args
	
	# Get headers
	for l in sp[1: -2]:
		sp3 = l.split(":")
		if len(sp3) >= 2:
			headers[sp3[0].strip()] = (":".join(sp3[1:])).strip()
		else:
			Print("[BreakPoint 5]")
			Print(sp3)
			return 501, path, headers, args

	# Judge path exists
	if os.path.exists(CONFIGS['rootdir'] + path):
		return 200, path, headers, args
	else:
		Print("[BreakPoint 6]")
		return 404, path, headers, args

# Generate HTTP Headers.
def GenHeader(statuscode, path, headers, args):
	head = ''
	if(statuscode == 200):
		head = 'HTTP/1.1 200 OK\r\n'
		if path.endswith(".html"):
			mimetype='text/html'
		elif path.endswith(".jpg"):
			mimetype='image/jpg'
		elif path.endswith(".gif"):
			mimetype='image/gif'
		elif path.endswith(".js"):
			mimetype='application/javascript'
		elif path.endswith(".css"):
			mimetype='text/css'
		else:
			mimetype='text/plain'
	elif(statuscode == 404):
		head = 'HTTP/1.1 404 Not Found\r\n'
		mimetype='text/plain'
	elif(statuscode == 501):
		head = 'HTTP/1.1 501 Connection Refused\r\n'
		mimetype='text/plain'

	# Additional header content
	date = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
	head += 'Date: %s\r\n' % date
	head += 'Content-Type: %s\r\n' % mimetype

	# Support Allow-Origin
	head += 'Access-Control-Allow-Origin: *\r\n'
	head += 'Connection: Close\r\n\r\n'

	return head

# Generate HTTP Body
def GenBody(statuscode, path, headers, args):
	if statuscode == 200:
		try:
			file = open(CONFIGS['rootdir'] + path, 'rb') # open file , r => read , b => byte format
			response = file.read()
			file.close()
		except Exception as e:
			Print(e)
			response = ''
	elif statuscode == 404:
		response = '404 Not Found'
	elif statuscode == 501:
		response = '501 Connection Refused'
	return response

# Redirect print function
def Print(*args):
	print reduce(lambda x, y: str(x) + str(y) , args)


class WebServer(object):
	def __init__(self):
		self.Port = CONFIGS["port"]
		self.Host = CONFIGS["host"]

	def Run(self):
		self.Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		while True:
			try:
				self.Socket.bind((self.Host, self.Port))
				global CONFIGS
				CONFIGS['port'] = self.Port
				Print('HTTP Server Running on Host:', self.Host, ' Port:', self.Port)
				break
			except Exception as e:
				Print('Error happened when start server...')
				Print(e)
				self.Port += 1
		Print('Server waiting for requests...')
		Print('-' * 60)
		# Start Loop
		self.get_connection()
		self.Socket.close()
		Print('Break loop, will terminate...')

	def get_connection(self):
		# Loop to get connections
		while True:
			# Judge break point
			global g_Break
			if g_Break:
				return

			self.Socket.listen(1) 
			conn, addr = self.Socket.accept()
			Print('[Section 1: Client Connect]')
			Print('Client connected on ', addr)
			Print("")

			# Receive request
			request = conn.recv(1024)

			# Anylise request
			statuscode, path, headers, args = AnyliseRequest(request)
			if path == "/break" and addr[0] == '127.0.0.1':
				g_Break = True
			
			Print('[Section 2: Anylise Result]')
			Print("Statuscode: ", statuscode)
			Print("Requiredpath: ", path)
			Print("Headers: ", headers)
			Print("Args: ", args)
			Print("")

			# Make body and headers
			body = GenBody(statuscode, path, headers, args)
			if body:
				headers = GenHeader(statuscode, path, headers, args)
			else:
				headers = GenHeader(501, path, headers, args)
			
			# Send to client
			ret = headers + body
			conn.send(ret)
			Print('[Section 3: Send Result]')
			Print(headers, body[:100])
			Print("")

			# Close conn
			Print('[Section 4: Close connection]')
			Print('Close connection with client')
			Print('-' * 60)
			conn.close()

if __name__ == '__main__':
	import threading
	threading.Thread(target=StartService).start()
	while True:
		time.sleep(1)
		Print(1)
