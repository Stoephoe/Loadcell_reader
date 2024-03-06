import serial
import matplotlib.pyplot as plt
import csv
from collections import deque
import time

# Specify the COM port and baud rate
COM_PORT = 'COM3'  # Change this to your desired COM port
BAUD_RATE = 230400  # Change this to match your device's baud rate
MAX_DATA_POINTS = 1000  # Adjust this according to the desired number of points to keep

# Initialize the plot
plt.ion()
fig, ax = plt.subplots()
x_data = deque(maxlen=MAX_DATA_POINTS)
y_data = deque(maxlen=MAX_DATA_POINTS)
line, = ax.plot(x_data, y_data, 'b-')
ax.set_xlabel('Time')
ax.set_ylabel('Scaled Data')

# File to save the data
CSV_FILE = 'data.csv'

# Time to keep in seconds
TIME_WINDOW = 10

# Scaling parameters
data_min = -403000
data_max = 82502156
scaled_min = 0
scaled_max = 10000

def scale_data(data):
    return (data - data_min) * (scaled_max - scaled_min) / (data_max - data_min) + scaled_min

def read_data_from_comport(port, baud_rate):
    ser = None
    try:
        ser = serial.Serial(port, baud_rate)
        print(f"Reading data from {port}...")
        with open(CSV_FILE, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(['Time', 'Scaled Data'])
            start_time = time.time()
            while True:
                serial_data = ser.readline().decode().strip()  # Read a line from serial and decode bytes to string
                data_list = serial_data.split(',')  # Split the line using commas as delimiters
                if len(data_list) >= 2:  # Ensure there are at least two columns of data
                    print("Data from second column:", data_list[1])
                    try:
                        raw_data = float(data_list[1])  # Convert the data to float
                        scaled_data = scale_data(raw_data)
                        current_time = time.time()
                        x_data.append(current_time - start_time)
                        y_data.append(scaled_data)
                        csv_writer.writerow([current_time - start_time, scaled_data])
                        line.set_xdata(x_data)
                        line.set_ydata(y_data)
                        ax.relim()
                        ax.autoscale_view()
                        fig.canvas.draw()
                        fig.canvas.flush_events()
                        # Keep only the last 10 seconds of data within the plot
                        if x_data[-1] - x_data[0] > TIME_WINDOW:
                            ax.set_xlim(x_data[-1] - TIME_WINDOW, x_data[-1])
                    except ValueError:
                        print("Invalid data format:", serial_data)
                else:
                    print("Invalid data format:", serial_data)
    except serial.SerialException as e:
        print("Serial port error:", e)
    except KeyboardInterrupt:
        print("Stopping the script...")
    finally:
        if ser and ser.is_open:
            ser.close()

if __name__ == "__main__":
    read_data_from_comport(COM_PORT, BAUD_RATE)
