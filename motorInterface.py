import serial
import time

arduino = serial.Serial(port='COM4', baudrate=115200, timeout=.1) 

def write_read(x): 
	arduino.write(bytes(x, 'utf-8')) 
	time.sleep(0.05) 
	data = arduino.readline() 
	return data 

while True: 
	if arduino.in_waiting > 0:
		data = arduino.read(arduino.in_waiting)
		print(data)
	#num = input("Enter a number: ") # Taking input from user 
	#value = write_read(num) 
	#print(value) # printing the value 
