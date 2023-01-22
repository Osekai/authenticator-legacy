from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import subprocess
import re

hostName = "0.0.0.0"
serverPort = 16582

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/authenticateUser"):
            osuid = re.search('\?osuId\=(.*)&', self.path).group(1)
            discordid = re.search('\&discordId\=(.*)', self.path).group(1)
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            subprocess.Popen(["python3","auth.py",osuid,discordid])
            self.wfile.write(bytes("user authenticated - " + osuid + ";" + discordid, "utf-8"))
            return;
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<p>osekai authenticator server</p>", "utf-8"))

if __name__ == "__main__":        
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
