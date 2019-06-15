import socket
import sys


connCloseMsg = "Connection closed: Client socket [{} | {}] freed"
httpMsgStart = "<-----------------Received HTTP Message----------------->"
httpMsgEnd   = "<------------------End of HTTP Message------------------>"



class Server():
	def __init__(self, port=80):
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.host = 'localhost'
		self.port = port

	def bind_socket(self):
		try:
			print("Binding socket: Host " + self.host + " | Server Port " + str(self.port))
			self.s.bind((self.host, self.port))
		except socket.error as msg:
			print("Socket error: " + str(msg))
			self.bind_socket()


	def connect(self):
		self.s.listen(5)
		keepAlive = 0
		initialLoop = 1

		while True:
			print()
			if initialLoop:
				conn, addr = self.s.accept()
				print("Connection established | " + "IP " + addr[0] + " | Client Port " + str(addr[1]))

			elif not keepAlive:
					conn.close()
					print(connCloseMsg.format(addr[0], str(addr[1])))
					conn, addr = self.s.accept()
					print()
					print("Connection established | " + "IP " + addr[0] + " | Client Port " + str(addr[1]))

			initialLoop = 0


			fullHTTP = ""

			#print("1")
			strdata = 'a' * 1023
			while True:
				if len(strdata) == 1023:
					data = conn.recv(1023)
					strdata = str(bytes.decode(data))
					#print("strdata: " + strdata)
					fullHTTP = fullHTTP + strdata
				else:
					break

				if strdata == "":
					break

			connIndex = fullHTTP.find("Connection: ")
			if connIndex == -1:
				keepAlive = 0

			elif fullHTTP[(connIndex + 12):(connIndex + 22)].lower() == "keep-alive":
				keepAlive = 1

			else:
				keepAlive = 0

			print(httpMsgStart)
			print(fullHTTP)
			print(httpMsgEnd)



			headerHTTP = fullHTTP.split("\r\n\r\n")[0]
			#print("headerHTTP: " + headerHTTP)

			reqLine = headerHTTP.split("\r\n")[0]
			#print("reqLine: " + reqLine)

			arrReqLine = reqLine.split(' ')
			#print("arrReqLine: " + str(arrReqLine))

			reqMethod = arrReqLine[0]

			if reqMethod != "GET":
				conn.send(str.encode("HTTP/1.1 400 Bad Request" + "\r\n"))
				conn.send(str.encode("\r\n"))
				continue

			filePath = arrReqLine[1]
			if filePath == '/':
				filePath = '/index.html'

			httpVersion = arrReqLine[2]


			#print("reqMethod: " + reqMethod)
			#print("filePath: " + filePath)
			#print("httpVersion: " + httpVersion)


			try:
				file_to_open = open(filePath[1:]).read()

			except FileNotFoundError as msg:
				file_to_open = str(msg)
				conn.send(str.encode("HTTP/1.1 404 Not Found" + "\r\n"))
				conn.send(str.encode("\r\n"))
				
				conn.send(str.encode(file_to_open))
				
				continue

			if httpVersion != "HTTP/1.1":
				conn.send(str.encode("HTTP/1.1 400 Bad Request" + "\r\n"))
				conn.send(str.encode("\r\n"))
				
				continue

			conn.send(str.encode("HTTP/1.1 200 OK" + "\r\n"))
			conn.send(str.encode("Content-Length: " + str(len(file_to_open)) + "\r\n"))
			conn.send(str.encode("Connection: " + "Keep-Alive" + "\r\n"))

			conn.send(str.encode("\r\n"))
			conn.send(str.encode(file_to_open))

			conn.send(str.encode(""))


		self.s.close()


	def close_server(self):
		self.s.close()


if __name__ == '__main__':
	myServer = Server()
	myServer.bind_socket()
	myServer.connect()

