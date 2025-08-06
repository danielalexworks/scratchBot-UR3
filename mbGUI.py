from http.server import SimpleHTTPRequestHandler, HTTPServer
import json
import os
import moneyBadger_GUI as mb

class CustomHTTPRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.directory = 'public'  # Serve files from the 'public' directory
        super().__init__(*args, directory=self.directory, **kwargs)

    def do_POST(self):
        if self.path == '/api/call_function':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)

            # Call the Python function with the received data
            result = self.my_python_function(data.get('data'))

            # Send response status code and headers
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            # Send the JSON response back to the client
            response = json.dumps({'result': result})
            self.wfile.write(response.encode('utf-8'))

        elif self.path == '/api/get_settings_data':

            # Call the Python function with the received data
            result = mb.getSettingsData()
            print(result)

            # Send response status code and headers
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            # Send the JSON response back to the client
            response = json.dumps({'result': result})
            self.wfile.write(response.encode('utf-8'))

        elif self.path == '/api/update_settings':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            print(data)
            # Call the Python function with the received data
            result = mb.updateSettings(data)
            print(result)

            # Send response status code and headers
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            # Send the JSON response back to the client
            response = json.dumps({'result': result})
            self.wfile.write(response.encode('utf-8'))

        elif self.path == '/api/manual_actions':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            print(data)
            # Call the Python function with the received data
            result = manualAction(data)
            print(result)

            # Send response status code and headers
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            # Send the JSON response back to the client
            response = json.dumps({'result': result})
            self.wfile.write(response.encode('utf-8'))

        elif self.path == '/api/program_actions':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            print(data)
            # Call the Python function with the received data
            result = programAction(data)
            print(result)

            # Send response status code and headers
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            # Send the JSON response back to the client
            response = json.dumps({'result': result})
            self.wfile.write(response.encode('utf-8'))

        else:
            # If not an API request, use the default file handler
            self.send_error(404, "File not found")

    def do_GET(self):
        if self.path == '/api/get_ticket':

            # Call the Python function with the received data
            result = mb.getTicketInfo()
            #print(result)

            # Send response status code and headers
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            # Send the JSON response back to the client
            response = json.dumps({'result': result})
            self.wfile.write(response.encode('utf-8'))
        elif self.path == '/api/scratch_status':

            # Call the Python function with the received data
            result = mb.getScratchedInfo()
            print(result)

            # Send response status code and headers
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            # Send the JSON response back to the client
            response = json.dumps({'result': result})
            self.wfile.write(response.encode('utf-8'))
        else:
            # Serve static files for other paths
            super().do_GET()

    def my_python_function(self, data):
        # Example function to process data
        return f"You sent: {data}"

def run(server_class=HTTPServer, handler_class=CustomHTTPRequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting server on port {port}...')
    httpd.serve_forever()

def manualAction(d):
    if mb.getProgramStatus() != 'in progress':
        a = d['action']
        if a == 'x':
            a = float(d['value']) * float(d['direction'])
            mb.moveX(a)
        elif a == 'y':
            a = float(d['value']) * float(d['direction'])
            mb.moveY(a)
        elif a == 'z':
            a = float(d['value']) * float(d['direction'])
            mb.moveZ(a)
        elif a == 'tryHome':
            mb.tryHome()
        elif a == 'motorToggle'  :
            mb.toggleMotor()
        elif a == 'resetZero' :
            mb.resetZero()

def programAction(d):
    a = d['action']
    if a == 'start':
        if mb.getSett('status') == 'paused':
            mb.togglePause()
        else:
            mb.startCurrentProgram()
    elif a == 'pause':
        mb.togglePause()
    elif a == 'stop':
        mb.endProgram()


if __name__ == '__main__':
    run()
