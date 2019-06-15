import socket
from bs4 import BeautifulSoup


starLine = "**********************************************************************"
httpMsgStart = "<-----------------Received HTTP Message----------------->"
httpMsgEnd   = "<------------------End of HTTP Message------------------>"


def find_resources_list(tag, attribute, soup):
	list = []
	for x in soup.findAll(tag):
		try:
			list.append(x[attribute])
		except KeyError:
			pass
	return (list)


if __name__ == '__main__':
	initialLoop = 1
	keepAlive = 0
	while True:
		print()
		url = input("Input URL: ")
		print(starLine)
		port = 80
		host = url.split('/')[0]
		path = "/" + "/".join(url.split('/')[1:])
		parentPath = "/" + "/".join(url.split('/')[1:-1])

		if initialLoop:
			try:
				s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				s.connect((host, port))
			except socket.error as msg:
				print("Socket error: " + str(msg) + "\n\n" + "Retry!")
				continue

		elif not keepAlive:
			s.close()
			try:
				s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				s.connect((host, port))
			except socket.error as msg:
				print("Socket error: " + str(msg) + "\n\n" + "Retry!")
				continue

		initialLoop = 0

		print("Host: " + host + " | Path: " + path)
		print()

		s.send(str.encode("GET " + path + " HTTP/1.1" + "\r\n"))
		s.send(str.encode("Host: " + host + "\r\n"))
		s.send(str.encode("Connection: " + "Keep-Alive" + "\r\n"))


		s.send(str.encode("\r\n"))
		s.send(str.encode(""))

		print(httpMsgStart)

		fullHTTP = ""

		response = 'a' * 1023
		while True:
			if len(response) == 1023:
				response = str(bytes.decode(s.recv(1023)))
				fullHTTP = fullHTTP + response
			else:
				break
			if response == "":
				break

		print(fullHTTP)
		print(httpMsgEnd)

		connIndex = response.find("Connection: ")

		if connIndex == -1:
			keepAlive = 0

		elif response[(connIndex + 12):(connIndex + 22)].lower() == "keep-alive":
			keepAlive = 1

		else:
			keepAlive = 0


		htmlContent = "\r\n\r\n".join(fullHTTP.split("\r\n\r\n")[1:])

		#print("htmlContent: " + htmlContent) 

		soup = BeautifulSoup(htmlContent, 'html.parser')
		

		extResourceArr = \
[find_resources_list('img', "src", soup), \
find_resources_list('script', "src", soup), \
find_resources_list("link", "href", soup), \
find_resources_list("video", "src", soup), \
find_resources_list("audio", "src", soup), \
find_resources_list("iframe", "src", soup), \
find_resources_list("embed", "src", soup), \
find_resources_list("object", "data", soup), \
find_resources_list("source", "src", soup)]

		i = 0
		while i < len(extResourceArr):
			j = 0
			while j < len(extResourceArr[i]):
				print()
				subPath = parentPath + extResourceArr[i][j]

				print("Requested resource: " + host + subPath)
				s.send(str.encode("GET " + subPath + " HTTP/1.1" + "\r\n"))
				s.send(str.encode("Host: " + host + "\r\n"))
				s.send(str.encode("Connection: " + "Keep-Alive" + "\r\n"))

				
				s.send(str.encode("\r\n"))
				s.send(str.encode(""))

				print(httpMsgStart)

				fullHTTP = ""

				response = 'a' * 1023
				while True:
					if len(response) == 1023:
						response = str(bytes.decode(s.recv(1023)))
						fullHTTP = fullHTTP + response
					else:
						break
					if response == "":
						break

				print(fullHTTP)
				print(httpMsgEnd)
				j = j + 1
			i = i + 1

		print(starLine)
		print()

