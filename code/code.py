# Import libraries
import serial
import time

# Function to read the result from the file
def read_result_from_file(path):
    with open(path, 'r') as f:
        result = f.read().strip()
        f.close()
    return result

# Path to the port where the Arduino is connected
port = '/dev/cu.usbmodem101'

# Establish a connection with the Arduino
arduino = serial.Serial(port, 9600, timeout=1)

# Wait for the connection to be established
time.sleep(2)  

# Path to the file containing the result
result_file_path = '../output/result.txt'

# Read the result from the file
result = read_result_from_file(result_file_path)

# Prepare the message to be sent to the Arduino
message = result + "\n"  

# Encode the message to bytes 
encoded_message = message.encode()

# Send the encoded message to the Arduino
arduino.write(encoded_message)

# Close the connection with the Arduino
arduino.close()  