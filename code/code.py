import os
import sys
import time

# Add parent directory to Python path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from serial import Serial
    from serial.tools import list_ports
except ImportError as e:
    print(f"Error importing serial: {e}")
    print("Please install pyserial: pip install pyserial")
    print("If already installed, try: python -m pip install --upgrade pyserial")
    exit(1)

def find_arduino_port():
    """Attempt to find the Arduino port"""
    try:
        ports = list(list_ports.comports())
        print("Available ports:")
        for port in ports:
            print(f" - {port.device}: {port.description}")
            if "Arduino" in port.description or "CH340" in port.description:
                return port.device
        return None
    except Exception as e:
        print(f"Error finding ports: {e}")
        return None

# Arduino configuration
BAUD_RATE = 9600
arduino = None

# Get absolute path for result.txt
RESULT_PATH = os.path.abspath(os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    'output',
    'result.txt'
))

print(f"Looking for Arduino...")
try:
    arduino_port = find_arduino_port()
    if arduino_port:
        arduino = Serial(port=arduino_port, baudrate=BAUD_RATE, timeout=1)
        print(f"Connected to Arduino on {arduino_port}")
        time.sleep(2)  # Wait for Arduino to initialize
    else:
        print("No Arduino device found.")
except Exception as e:
    print(f"Failed to connect to Arduino: {e}")
    print("Make sure Arduino is connected and no other program is using it")
    exit(1)

def read_result():
    """Read the result from result.txt"""
    try:
        with open(RESULT_PATH, "r") as f:
            content = f.read().strip().lower()
            print(f"Read from {RESULT_PATH}: {content}")
            return content == "true"
    except Exception as e:
        print(f"Error reading {RESULT_PATH}: {e}")
        return False

# Main loop
try:
    print("Starting main loop...")
    while True:
        person_detected = read_result()
        if arduino:
            try:
                message = '1\n' if person_detected else '0\n'
                arduino.write(message.encode('utf-8'))
                arduino.flush()
                print(f"Sent to Arduino: {message.strip()}")
                
                # Read response if any
                response = arduino.readline().decode('utf-8').strip()
                if response:
                    print(f"Arduino response: {response}")
                
            except Exception as e:
                print(f"Error communicating with Arduino: {e}")
                break
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nExiting...")
finally:
    if arduino:
        arduino.close()
        print("Arduino connection closed")