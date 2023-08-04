import socket
import time
import threading
import tkinter as tk
from tkinter import scrolledtext
from tkinter import filedialog
import subprocess
import re
import platform
from datetime import datetime

class SynTestGui:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Port Pinger')
        self.root.geometry("400x500")  # Increase the width to 600

        self.root.grid_columnconfigure(0, weight=2)  # Make the left column twice as wide
        self.root.grid_columnconfigure(1, weight=1)
        
        self.ip_label = tk.Label(self.root, text='IP:')
        self.ip_label.grid(row=0, column=0, sticky='w')

        self.ip_entry = tk.Entry(self.root)
        self.ip_entry.grid(row=0, column=1, sticky='w')
        self.ip_entry.insert(0, self.get_default_gateway())

        self.port_label = tk.Label(self.root, text='Port:')
        self.port_label.grid(row=1, column=0, sticky='w')

        self.port_entry = tk.Entry(self.root)
        self.port_entry.grid(row=1, column=1, sticky='w')
        self.port_entry.insert(0, '443')

        self.success_label = tk.Label(self.root, text='Open #:')
        self.success_label.grid(row=0, column=2, sticky='w')

        self.success_count = tk.Label(self.root, text='0')
        self.success_count.grid(row=0, column=3, sticky='w')

        self.delay_label = tk.Label(self.root, text='Sec:')
        self.delay_label.grid(row=2, column=0, sticky='w')

        self.delay_entry = tk.Entry(self.root)
        self.delay_entry.grid(row=2, column=1, sticky='w')
        self.delay_entry.insert(0, '2')

        self.fail_label = tk.Label(self.root, text='Closed #:')
        self.fail_label.grid(row=1, column=2, sticky='w')

        self.fail_count = tk.Label(self.root, text='0')
        self.fail_count.grid(row=1, column=3, sticky='w')

        self.elapsed_label = tk.Label(self.root, text='Elapsed (s):')
        self.elapsed_label.grid(row=2, column=2, sticky='w')

        self.elapsed_time_label = tk.Label(self.root, text='0')
        self.elapsed_time_label.grid(row=2, column=3, sticky='w')

        self.run_button = tk.Button(self.root, text='Run', command=self.run_test)
        self.run_button.grid(row=3, column=0, sticky='w')

        self.insert_line_button = tk.Button(self.root, text='Insert Line', command=self.insert_line)
        self.insert_line_button.grid(row=3, column=1, sticky='w')

        self.clear_output_button = tk.Button(self.root, text='Clear Output', command=self.clear_output)
        self.clear_output_button.grid(row=3, column=2, sticky='w')

        self.save_output_button = tk.Button(self.root, text='Save Output', command=self.save_output)
        self.save_output_button.grid(row=3, column=3, sticky='w')

        self.output = scrolledtext.ScrolledText(self.root)
        self.output.grid(row=4, column=0, columnspan=4, sticky='w')

        self.is_running = False
        self.successful = 0
        self.unsuccessful = 0
        self.start_time = 0
        self.elapsed_time = 0
        self.pause_time = 0

    def get_default_gateway(self):
        if platform.system() == "Windows":
            return re.findall("Default Gateway.*: ([0-9.]+)", subprocess.check_output("ipconfig", shell=True).decode())[0]
        else:
            return re.findall("default via ([0-9.]+)", subprocess.check_output("ip route", shell=True).decode())[0]

    def run_test(self):
        if not self.is_running:
            self.is_running = True
            self.run_button.config(text="Stop")
            if self.start_time == 0:
                self.start_time = time.time()
            else:
                self.start_time = time.time() - self.pause_time
            self.output.insert(tk.END, f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            threading.Thread(target=self.test_loop).start()
            threading.Thread(target=self.timer_loop).start()
        else:
            self.is_running = False
            self.run_button.config(text="Run")
            self.pause_time = self.elapsed_time
            self.output.insert(tk.END, f"Stop Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            self.insert_line()

    def test_loop(self):
        ip = self.ip_entry.get()
        port = int(self.port_entry.get())
        delay = int(self.delay_entry.get())

        while self.is_running:
            start_time = time.time()
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(delay)
                result = s.connect_ex((ip, port))
                elapsed_time = time.time() - start_time
                if result == 0:
                    self.output.insert(tk.END, f"Port is open - {elapsed_time:.2f} seconds\n")
                    self.successful += 1
                    self.success_count.config(text=str(self.successful))
                else:
                    self.output.insert(tk.END, f"Port is not open - {elapsed_time:.2f} seconds\n")
                    self.unsuccessful += 1
                    self.fail_count.config(text=str(self.unsuccessful))
            except Exception as e:
                self.output.insert(tk.END, f"Error: {str(e)} - {elapsed_time:.2f} seconds\n")
            finally:
                s.close()
                time.sleep(delay)
                self.output.see(tk.END)  # Scroll to bottom

    def timer_loop(self):
        while self.is_running:
            self.elapsed_time = time.time() - self.start_time
            self.elapsed_time_label.config(text=f"{self.elapsed_time:.2f}")
            time.sleep(1)

    def insert_line(self):
        self.output.insert(tk.END, '-' * 15 + '\n')
        self.output.insert(tk.END, f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        self.output.insert(tk.END, '-' * 15 + '\n')

    def clear_output(self):
        self.output.delete(1.0, tk.END)
        self.successful = 0
        self.unsuccessful = 0
        self.start_time = 0
        self.elapsed_time = 0
        self.pause_time = 0
        self.success_count.config(text=str(self.successful))
        self.fail_count.config(text=str(self.unsuccessful))
        self.elapsed_time_label.config(text='0')

    def save_output(self):
        ip = self.ip_entry.get()
        port = self.port_entry.get()
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", initialfile=f"portping-{ip}-{port}.txt")
        if file_path:
            with open(file_path, 'w') as file:
                file.write(self.output.get(1.0, tk.END))

    def start(self):
        self.root.mainloop()


if __name__ == '__main__':
    gui = SynTestGui()
    gui.start()
