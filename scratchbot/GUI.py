from http.server import SimpleHTTPRequestHandler, HTTPServer
import json
import os
import scratchBot as sb
import ticket
import cobot
import settings
import programs
import time
import cameraTracker as cam


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

        

        elif self.path == '/api/update_settings':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            sb.bugp(data)

            # Call the Python function with the received data
            result = settings.updateSettings(data)
            time.sleep(1)

            if(settings.getSett('status') == 'ready'):
                if 'debugging' in data:
                    sb.restartBot()
                elif 'poweredTool' in data:
                    sb.restartBot()
                elif 'checkForce' in data:
                    sb.restartBot()
                elif 'alignoffx' in data or 'alignoffy' in data:
                    sb.getMovesFromFile()
                
            '''
            if 'alignoffx' in data or 'alignoffy' in data:
                if(settings.getSett('status') == 'ready'):
                    sb.adjustStartingPose()
                else:
                    print("cannot adjust aligneroffset during program ( try manual adjust TCP instead )")
            '''

            sb.bugp(result)

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
            sb.bugp(data)
            # Call the Python function with the received data
            result = manualAction(data)
            sb.bugp(result)

            # Send response status code and headers
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            # Send the JSON response back to the client
            response = json.dumps({'result': result})
            self.wfile.write(response.encode('utf-8'))

        elif self.path == '/api/adjust_TCP':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            sb.bugp(data)
            # Call the Python function with the received data
            result = sb.adjustTCP(data['action'],data['value'],data['direction'])
            sb.bugp(result)

            # Send response status code and headers
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            # Send the JSON response back to the client
            response = json.dumps({'result': result})
            self.wfile.write(response.encode('utf-8'))

        elif self.path == '/api/manual_rotate':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            sb.bugp(data)
            # Call the Python function with the received data
            result = manualRotate(data)
            sb.bugp(result)

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
            sb.bugp(data)
            # Call the Python function with the received data
            result = programAction(data)
            sb.bugp(result)

            # Send response status code and headers
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            # Send the JSON response back to the client
            response = json.dumps({'result': result})
            self.wfile.write(response.encode('utf-8'))

        elif self.path == '/api/go_to_pose':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            sb.bugp(f"data: {data}")
            # Call the Python function with the received data
            result = sb.moveTo(data['pose'])
            sb.bugp(result)

            # Send response status code and headers
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            # Send the JSON response back to the client
            response = json.dumps({'result': result})
            self.wfile.write(response.encode('utf-8'))

        elif self.path == '/api/go_to_box':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            sb.bugp(data)
            # Call the Python function with the received data
            result = sb.moveToBox(data['box'])
            sb.bugp(result)

            # Send response status code and headers
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            # Send the JSON response back to the client
            response = json.dumps({'result': result})
            self.wfile.write(response.encode('utf-8'))

        elif self.path == '/api/scratch_single_box':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            sb.bugp(data)
            # Call the Python function with the received data
            result = sb.scratchABox(data['box'])
            sb.bugp(result)

            # Send response status code and headers
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            # Send the JSON response back to the client
            response = json.dumps({'result': result})
            self.wfile.write(response.encode('utf-8'))



        elif self.path == '/api/set_new_starting_pose':
            #sb.shutdown()
            sb.setNewStartingPosition()

            # Send response status code and headers
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            # Send the JSON response back to the client
            response = json.dumps({'result': 'success'})
            self.wfile.write(response.encode('utf-8'))

        elif self.path == '/api/shutdown':
            sb.shutdown()

            # Send response status code and headers
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            # Send the JSON response back to the client
            response = json.dumps({'result': result})
            self.wfile.write(response.encode('utf-8'))

        elif self.path == '/api/enable_free_drive':

            # Call the Python function with the received data
            result = sb.enableFreeDrive()
            #result = sb.restartBot()
            
            

            # Send response status code and headers
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            # Send the JSON response back to the client
            response = json.dumps({'result': result})
            self.wfile.write(response.encode('utf-8'))

        elif self.path == '/api/align_ticket':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            sb.bugp(data)
            
            result = sb.alignTicket(data['location'])
            sb.bugp(result)

            # Send response status code and headers
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            # Send the JSON response back to the client
            response = json.dumps({'result': result})
            self.wfile.write(response.encode('utf-8'))

        elif self.path == '/api/send_cam_to':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            sb.bugp(data)
            
            loc = data['loc']
            if(loc == 'front'):
                cam.goToFront(False)
            elif(loc == 'back'):
                cam.goToBack(False)
            elif(loc == 'ticketTop'):
                cam.goToTicketTop(False)
            else:
                cam.moveToMm(int(loc), False)
            

            result = f"moved to {loc}"

            # Send response status code and headers
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            # Send the JSON response back to the client
            response = json.dumps({'result': result})
            self.wfile.write(response.encode('utf-8'))

        elif self.path == '/api/figure_cam_position':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            cam.getCurrentPosition()
            result = 'ok'

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
            result = ticket.getTicketInfo()
            
            #print(result)


            # Send response status code and headers
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            # Send the JSON response back to the client
            response = json.dumps({'result': result})
            self.wfile.write(response.encode('utf-8'))
        

        elif self.path == '/api/get_settings_data':

            result = settings.getSettingsData()
            sb.bugp(result)

            # Send response status code and headers
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            # Send the JSON response back to the client
            response = json.dumps({'result': result})
            self.wfile.write(response.encode('utf-8'))

        elif self.path == '/api/estimate_time':

            result = sb.estimateTime()
            sb.bugp(result)

            # Send response status code and headers
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            # Send the JSON response back to the client
            response = json.dumps({'result': result})
            self.wfile.write(response.encode('utf-8'))

        elif self.path == '/api/scratch_status':

            # Call the Python function with the received data
            result = programs.getScratchedInfo()
            lines = cobot.getLines()

            # Send response status code and headers
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            # Send the JSON response back to the client
            response = json.dumps({'result': result, 'lines':lines})
            self.wfile.write(response.encode('utf-8'))

        else:
            # Serve static files for other paths
            super().do_GET()

    def my_python_function(self, data):
        # Example function to process data
        return f"You sent: {data}"

def run(server_class=HTTPServer, handler_class=CustomHTTPRequestHandler, port=8000):
    server_address = ('0.0.0.0', port)
    httpd = server_class(server_address, handler_class)
    sb.bugp(f'Starting server on port {port}...')
    httpd.serve_forever()

def manualAction(d):
    if settings.getSett('status') != 'in progress':
        a = d['action']
        if a == 'x':
            a = float(d['value']) * float(d['direction'])
            sb.manualMove(a, 'x')
        elif a == 'y':
            a = float(d['value']) * float(d['direction'])
            sb.manualMove(a, 'y')
        elif a == 'z':
            a = float(d['value']) * float(d['direction'])
            sb.manualMove(a, 'z')
        elif a == 'tryHome':
            sb.moveTo('home')
        elif a == 'motorToggle'  :
            sb.toggleMotor()

def manualRotate(d):
    sb.bugp('mr')
    if settings.getSett('status') != 'in progress':
        a = d['action']
        if a == 'x':
            a = float(d['value']) * float(d['direction'])
            sb.manualRotate(a, 'x')
        elif a == 'y':
            a = float(d['value']) * float(d['direction'])
            sb.manualRotate(a, 'y')
        elif a == 'z':
            a = float(d['value']) * float(d['direction'])
            sb.manualRotate(a, 'z')
        else:
            sb.manualRotate(a, 'test')

def programAction(d):
    a = d['action']
    if a == 'start':
        if settings.getSett('status') == 'paused':
            sb.togglePause()
        else:
            programs.startCurrentProgram()
    elif a == 'pause':
        sb.togglePause()
    elif a == 'stop':
        programs.endProgram()
    elif a == 'nextgroup':
        programs.advanceToNextGroup()


if __name__ == '__main__':
    run()
