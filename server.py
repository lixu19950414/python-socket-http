# coding=utf-8

import socket
import time
import os

# Global Configs
CONFIGS = {
	'root_dir': "/Users/lixu-mac/Desktop/python-socket-http/tests/txt",
	'host': "",
	'port': 8084,
}

g_Break = False

# Redirect Print function
def Print(*args):
	print reduce(lambda x, y: str(x) + str(y) , args)

def StartService():
	svr = Server()
	svr.run()

class Server(object):
	def __init__(self):
		self.port = CONFIGS["port"]
		self.host = CONFIGS["host"]
		self.host_dir = CONFIGS["root_dir"]
		Print(self.host_dir)

	def run(self):
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			self.socket.bind((self.host, self.port))
			Print('HTTP Server Running on Host:', self.host, ' Port:', self.port)
		except Exception as e:
			Print('Sorry! , PORT:',self.port,' already in use. Please try another port')
			return
		Print('Server waiting for requests...')
		Print('-' * 60)
		self.get_connection()
		self.socket.close()
		Print('Break loop, will terminate...')

	def header_gen(self,status):
		# Generate HTTP Headers.
		head = ''
		if(status == 200):
			head = 'HTTP/1.1 200 OK\n'
		elif(status == 404):
			head = 'HTTP/1.1 404 Not Found\n'


		if self.req_file.endswith(".html"):
			mimetype='text/html'
		elif self.req_file.endswith(".jpg"):
			mimetype='image/jpg'
		elif self.req_file.endswith(".gif"):
			mimetype='image/gif'
		elif self.req_file.endswith(".js"):
			mimetype='application/javascript'
		elif self.req_file.endswith(".css"):
			mimetype='text/css'
		else:
			if status == 404:
				mimetype='text/html'
			else:
				mimetype='text/plain'

		# Additional header content
		date = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
		head += 'Date: '+ date +'\n'
		head += 'Content-Type: '+str(mimetype)+'\n'
		# Support Allow-Origin
		head += 'Access-Control-Allow-Origin: *' + '\n'
		head += 'Connection: Close\n\n'

		return head

	def get_connection(self):
		# Loop to get connections
		while True:
			global g_Break
			if g_Break:
				return
			self.socket.listen(1) 

			conn, addr = self.socket.accept() 
			#conn => Connected socket to client
			#addr => Client address

			Print('Client connected on ',addr)

			request = conn.recv(1024)
			Print("Request: ", request)

			temp = request.split(' ')

			if len(temp) < 1:
				Print('Request not valid')
				Print('-' * 60)
				Print(request)
				conn.close()

			method = temp[0]
			req_file = temp[1]
			self.req_file = req_file

			Print('Client requset ',req_file,' using ',method,' method')

			if (method == 'GET'):

				r_file = req_file.split('?')[0]
				if(r_file == '/'):
					r_file = '/index.html'

				if r_file == '/break':
					g_Break = True
					header = self.header_gen(200)
					response = 'Break Success.'
					conn.send(header + response)
					conn.close()
					continue

				request_file = self.host_dir + r_file
				# request_file = os.path.join(self.host_dir, r_file)
				Print("request_file: ", request_file)

				# Read file 
				try:
					file = open(request_file, 'rb') # open file , r => read , b => byte format
					response = file.read()
					file.close()

					header = self.header_gen(200) # Generate hearder
				except Exception as e:
					Print('File not found ',request_file)
					header = self.header_gen(404)
					response = '<html><body><center><h3>Error 404: File not found</h3><p>Python HTTP Server</p></center></body></html>'
				
				final_res = header
				final_res += response

				conn.send(final_res)
				Print('Close connection with client')
				Print('-' * 60)
				conn.close()

			else:
				Print('HTTP request not valid. You are using ', method)
				Print('-' * 60)

			conn.close()

if __name__ == '__main__':
	StartService()
