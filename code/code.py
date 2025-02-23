# Import libraries
from serial import Serial
from serial.tools import list_ports
import time

# Function to read the result from the file
def read_result_from_file(path):
    with open(path, 'r') as f:
        result = f.read().strip()
        f.close()
    return result

# Function to find Arduino port
def find_arduino_port():
    ports = list_ports.comports()
    for port in ports:
        if 'Arduino' in port.description or 'CH340' in port.description:  # CH340 is common Arduino clone chip
            return port.device
    return None

# Find and set Arduino port
port = find_arduino_port()
if port is None:
    print("Error: Arduino not found. Please check connection.")
    available_ports = [p.device for p in list_ports.comports()]
    print(f"Available ports: {available_ports}")
    exit(1)

print(f"Connecting to Arduino on port: {port}")

# Establish a connection with the Arduino
try:
    arduino = Serial(port, 9600, timeout=1)
except Exception as e:
    print(f"Error connecting to Arduino: {e}")
    exit(1)

# Wait for the connection to be established
time.sleep(2)  

# Path to the file containing the result
result_file_path = './output/result.txt'

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