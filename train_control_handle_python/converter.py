import serial
import argparse
import json
import time

SERIAL_BAUD = 9600

# Function to map ADC value to a discrete output with proper rounding
def map_to_discrete(value, min_value, max_value, divisions):
    # Avoid division by zero
    if max_value == min_value:
        return 0
    # Map the value and round to nearest discrete level
    scale = (divisions - 1) / (max_value - min_value)
    return round((value - min_value) * scale)

# Function to read calibration data from file
def load_calibration(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {'min_adc1': 0, 'max_adc1': 1023, 'min_adc2': 0, 'max_adc2': 1023}

# Function to save calibration data to file
def save_calibration(file_path, calibration_data):
    with open(file_path, 'w') as file:
        json.dump(calibration_data, file)

def read_line_to_values(ser):
    line = ser.readline()
    if len(line) == 0:
        print("empty read")
        return None
    if line[0] == b'\x00':
        print("null line received")
        return None
    try:
        decoded = line.decode('utf-8').strip()
    except Exception as e:
        print("bad line was: ", line)
        print(f"Bad line exception: {e}")
    else:
        if ',' not in decoded:
            print("bad line was: ", decoded)
            return None
        split = decoded.split(',')
        return split[:2]


# Function to run calibration mode
def calibrate(serial_port, file_path):
    calibration_data = {'min_adc1': 1023, 'max_adc1': 0, 'min_adc2': 1023, 'max_adc2': 0}
    
    print("Calibrating... Move the inputs to their minimum and maximum positions.")
    print("Press Ctrl+C to stop calibration.")
    
    try:
        while True:
            values = read_line_to_values(serial_port)
            if values:
                adc1, adc2 = map(int, values)
                
                calibration_data['min_adc1'] = min(calibration_data['min_adc1'], adc1)
                calibration_data['max_adc1'] = max(calibration_data['max_adc1'], adc1)
                calibration_data['min_adc2'] = min(calibration_data['min_adc2'], adc2)
                calibration_data['max_adc2'] = max(calibration_data['max_adc2'], adc2)

                print(f"ADC1: {adc1}, ADC2: {adc2}")
                print(f"Calibrating: {calibration_data}")
            
    except KeyboardInterrupt:
        save_calibration(file_path, calibration_data)
        print("\nCalibration saved.")
    except Exception as e:
        print(f"Error during calibration: {e}")

# Main function
def main(port_name, calibration_file, calibrate_mode):
    # Open serial port
    ser = serial.Serial(port_name, SERIAL_BAUD, timeout=1)
    
    # Calibration mode
    if calibrate_mode:
        calibrate(ser, calibration_file)
        return

    # Load calibration data
    calibration_data = load_calibration(calibration_file)
    
    print("Starting data processing...")

    try:
        while True:
            values = read_line_to_values(ser)
            if values:
                adc1, adc2 = map(int, values)
                
                # Map to discrete outputs based on calibration data and division
                discrete_adc1 = map_to_discrete(adc1, calibration_data['min_adc1'], calibration_data['max_adc1'], 3)
                discrete_adc2 = map_to_discrete(adc2, calibration_data['min_adc2'], calibration_data['max_adc2'], 20)
                
                print(f"Raw: {adc1}, {adc2} -> Discrete: {discrete_adc1}, {discrete_adc2}")
                

    except KeyboardInterrupt:
        print("\nStopping data processing.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ser.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Read serial data and process ADC values.")
    parser.add_argument('--port-name', required='true', help='address of com port (e.g. COM7, /etc/ttyUSB0)')
    parser.add_argument('--calibrate', action='store_true', help='Run in calibration mode')
    parser.add_argument('--calibration-file', type=str, default='calibration.json', help='File to store/load calibration data')
    args = parser.parse_args()

    main(args.port_name, args.calibration_file, args.calibrate)
