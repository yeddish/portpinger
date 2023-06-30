import socket
import time
import threading
import tkinter as tk
from tkinter import scrolledtext
import subprocess
import re
import platform

class SynTestGui:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Port Pinger')
        self.root.geometry("300x500")

        self.root.grid_columnconfigure(0, weight=1)
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

        self.delay_label = tk.Label(self.root, text='Delay (s):')
        self.delay_label.grid(row=2, column=0, sticky='w')

        self.delay_entry = tk.Entry(self.root)
        self.delay_entry.grid(row=2, column=1, sticky='w')
        self.delay_entry.insert(0, '2')

        self.run_button = tk.Button(self.root, text='Run', command=self.run_test)
        self.run_button.grid(row=3, column=0, sticky='w')

        self.insert_line_button = tk.Button(self.root, text='Insert Line', command=self.insert_line)
        self.insert_line_button.grid(row=3, column=1, sticky='w')

        self.clear_output_button = tk.Button(self.root, text='Clear Output', command=self.clear_output)
        self.clear_output_button.grid(row=3, column=2, sticky='w')

        self.output = scrolledtext.ScrolledText(self.root)
        self.output.grid(row=4, column=0, columnspan=3, sticky='w')

        self.is_running = False

    def get_default_gateway(self):
        if platform.system() == "Windows":
            return re.findall("Default Gateway.*: ([0-9.]+)", subprocess.check_output("ipconfig", shell=True).decode())[0]
        else:
            return re.findall("default via ([0-9.]+)", subprocess.check_output("ip route", shell=True).decode())[0]

    def run_test(self):
        if not self.is_running:
            self.is_running = True
            self.run_button.config(text="Stop")
            threading.Thread(target=self.test_loop).start()
        else:
            self.is_running = False
            self.run_button.config(text="Run")

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
                else:
                    self.output.insert(tk.END, f"Port is not open - {elapsed_time:.2f} seconds\n")
            except Exception as e:
                self.output.insert(tk.END, f"Error: {str(e)} - {elapsed_time:.2f} seconds\n")
            finally:
                s.close()
                time.sleep(delay)
                self.output.see(tk.END)  # Scroll to the bottom

    def insert_line(self):
        self.output.insert(tk.END, "-"*15 + "\n")
        self.output.see(tk.END)  # Scroll to the bottom

    def clear_output(self):
        self.output.delete('1.0', tk.END)

    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    app = SynTestGui()
    app.run()
