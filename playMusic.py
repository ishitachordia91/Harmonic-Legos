import serial
import binascii
import time

# Mapping RGB values to Channel, Pitch and Velocity
def rgb_map(red,green,blue):
	red=red%8+144
	green=green%80+40
	blue=blue%80+40
	return red,green,blue

# Function to send data on serial port to play music	
def playMusic(rgbValues):
	#rgbValues = (124,215,84)
	val_red = rgbValues[0]
	val_green = rgbValues[1]
	val_blue = rgbValues[2]
	midi_val = rgb_map(val_red,val_green,val_blue)
	ser.open()
	#ser.write(b'\x94')
	#ser.write(b'\x3C')
	#ser.write(b'\x7F')
	ser.write(binascii.unhexlify(hex(midi_val[0])[2:]))
	ser.write(binascii.unhexlify(hex(midi_val[1])[2:]))
	ser.write(binascii.unhexlify(hex(midi_val[2])[2:]))
	ser.close()
	time.sleep(0.5)
	
# Initialize the serial port	
def initSerial():
	ser=serial.Serial()
	ser.baudrate = 115200
	ser.port = 'COM1'
	return ser

	
ser=initSerial()	# declaring serial port

newColor=[(144,10,10),(145,20,20),(146,30,30),(144,40,40),(145,50,50),(146,60,60),(144,70,70),(145,80,80),(146,90,90),(144,100,100)]

for x in range (0,10):
		playMusic(newColor[x])
		x=x+1







