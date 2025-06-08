import customtkinter as ctk
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
import requests
import json
import threading
import socket
import time
from typing import List, Dict, Optional

# Set appearance mode and default color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.available_models = []
        self.current_model = None
        self.update_available_models()

    def update_available_models(self):
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                self.available_models = [model['name'] for model in response.json()['models']]
            else:
                self.available_models = []
        except requests.exceptions.ConnectionError:
            self.available_models = []

    def generate_response(self, prompt: str, model: str = None) -> str:
        if not model and not self.current_model:
            return "No model selected"
        
        model_to_use = model or self.current_model
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": model_to_use,
                    "prompt": prompt,
                    "stream": False
                }
            )
            if response.status_code == 200:
                return response.json()['response']
            else:
                return f"Error: {response.status_code}"
        except requests.exceptions.ConnectionError:
            return "Error: Could not connect to Ollama server"

class MCPServer:
    def __init__(self, name: str, url: str):
        self.name = name
        self.url = url
        self.status = "unknown"
        self.last_check = None

    def check_status(self) -> bool:
        try:
            response = requests.get(f"{self.url}/health", timeout=5)
            self.status = "online" if response.status_code == 200 else "offline"
            self.last_check = time.time()
            return self.status == "online"
        except:
            self.status = "offline"
            self.last_check = time.time()
            return False

class ServerDiscovery:
    def __init__(self):
        self.discovered_servers: List[MCPServer] = []
        self.discovery_running = False
        self.discovery_thread = None

    def start_discovery(self, port_range: tuple = (8000, 8100)):
        if self.discovery_running:
            return
        
        self.discovery_running = True
        self.discovery_thread = threading.Thread(
            target=self._discovery_worker,
            args=(port_range,)
        )
        self.discovery_thread.daemon = True
        self.discovery_thread.start()

    def stop_discovery(self):
        self.discovery_running = False
        if self.discovery_thread:
            self.discovery_thread.join()

    def _discovery_worker(self, port_range: tuple):
        while self.discovery_running:
            for port in range(port_range[0], port_range[1]):
                if not self.discovery_running:
                    break
                
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(0.1)
                    result = sock.connect_ex(('localhost', port))
                    if result == 0:
                        # Try to identify if it's an MCP server
                        try:
                            response = requests.get(f"http://localhost:{port}/health", timeout=1)
                            if response.status_code == 200:
                                server = MCPServer(f"MCP Server {port}", f"http://localhost:{port}")
                                if server not in self.discovered_servers:
                                    self.discovered_servers.append(server)
                        except:
                            pass
                    sock.close()
                except:
                    continue

class ChatMessage(ctk.CTkFrame):
    def __init__(self, master, message, is_user=True, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="transparent")
        
        # Create message container with different colors for user and AI
        message_frame = ctk.CTkFrame(self, fg_color="#2B2B2B" if is_user else "#1F1F1F")
        message_frame.pack(fill="x", padx=10, pady=5)
        
        # Add timestamp
        timestamp = datetime.now().strftime("%H:%M")
        time_label = ctk.CTkLabel(message_frame, text=timestamp, font=("Arial", 10), text_color="gray")
        time_label.pack(anchor="e", padx=5, pady=2)
        
        # Add message text
        message_label = ctk.CTkLabel(
            message_frame, 
            text=message,
            wraplength=400,
            justify="left",
            font=("Arial", 12)
        )
        message_label.pack(padx=10, pady=5, anchor="w")

class SettingsDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Settings")
        self.geometry("400x300")
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        # Create settings content
        content = ctk.CTkFrame(self)
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Theme settings
        theme_frame = ctk.CTkFrame(content, fg_color="transparent")
        theme_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(theme_frame, text="Theme:", font=("Arial", 12, "bold")).pack(anchor="w")
        theme_menu = ctk.CTkOptionMenu(
            theme_frame,
            values=["Dark", "Light", "System"],
            command=self.change_theme
        )
        theme_menu.pack(fill="x", pady=5)
        
        # Ollama settings
        ollama_frame = ctk.CTkFrame(content, fg_color="transparent")
        ollama_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(ollama_frame, text="Ollama URL:", font=("Arial", 12, "bold")).pack(anchor="w")
        self.ollama_url = ctk.CTkEntry(ollama_frame)
        self.ollama_url.insert(0, "http://localhost:11434")
        self.ollama_url.pack(fill="x", pady=5)
        
        # Save button
        save_btn = ctk.CTkButton(
            content,
            text="Save Settings",
            command=self.save_settings
        )
        save_btn.pack(pady=20)
    
    def change_theme(self, choice):
        ctk.set_appearance_mode(choice.lower())
    
    def save_settings(self):
        # Save Ollama URL
        ollama_url = self.ollama_url.get().strip()
        if ollama_url:
            self.master.ollama_client = OllamaClient(ollama_url)
            self.master.ollama_client.update_available_models()
            self.master.update_llm_list()
        
        messagebox.showinfo("Success", "Settings saved successfully!")
        self.destroy()

class AddServerDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Add Server")
        self.geometry("400x250")
        
        # Make dialog modal
        self.transient(parent)
        self.grab_set()
        
        # Create content
        content = ctk.CTkFrame(self)
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Server name
        name_frame = ctk.CTkFrame(content, fg_color="transparent")
        name_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(name_frame, text="Server Name:", font=("Arial", 12, "bold")).pack(anchor="w")
        self.name_entry = ctk.CTkEntry(name_frame)
        self.name_entry.pack(fill="x", pady=5)
        
        # Server URL
        url_frame = ctk.CTkFrame(content, fg_color="transparent")
        url_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(url_frame, text="Server URL:", font=("Arial", 12, "bold")).pack(anchor="w")
        self.url_entry = ctk.CTkEntry(url_frame)
        self.url_entry.pack(fill="x", pady=5)
        
        # Add button
        add_btn = ctk.CTkButton(
            content,
            text="Add Server",
            command=self.add_server
        )
        add_btn.pack(pady=20)
    
    def add_server(self):
        name = self.name_entry.get().strip()
        url = self.url_entry.get().strip()
        
        if name and url:
            server = MCPServer(name, url)
            if server.check_status():
                self.master.add_server(server)
                messagebox.showinfo("Success", f"Server {name} added successfully!")
                self.destroy()
            else:
                messagebox.showerror("Error", "Could not connect to server")
        else:
            messagebox.showerror("Error", "Please fill in all fields")

class MCPClient(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Initialize Ollama client
        self.ollama_client = OllamaClient()
        
        # Initialize server discovery
        self.server_discovery = ServerDiscovery()
        self.known_servers: List[MCPServer] = []
        
        # Configure window
        self.title("MCP Client")
        self.geometry("1200x800")
        self.minsize(800, 600)
        
        # Configure grid layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create sidebar
        self.create_sidebar()
        
        # Create main chat area
        self.create_chat_area()
        
        # Start server discovery
        self.server_discovery.start_discovery()
        
    def create_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_rowconfigure(4, weight=1)
        
        # Logo/Title
        title_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        title_frame.pack(fill="x", padx=20, pady=(20, 10))
        ctk.CTkLabel(
            title_frame,
            text="MCP Client",
            font=("Arial", 24, "bold")
        ).pack()
        
        # LLM Selection
        llm_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        llm_frame.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(
            llm_frame,
            text="Choose LLM:",
            font=("Arial", 12, "bold")
        ).pack(anchor="w")
        self.llm_selector = ctk.CTkOptionMenu(
            llm_frame,
            values=self.ollama_client.available_models,
            font=("Arial", 12),
            command=self.on_llm_change
        )
        self.llm_selector.pack(fill="x", pady=(5, 0))
        
        # Server Selection
        server_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        server_frame.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(
            server_frame,
            text="MCP Servers:",
            font=("Arial", 12, "bold")
        ).pack(anchor="w")
        self.server_list = ctk.CTkOptionMenu(
            server_frame,
            values=["No servers available"],
            font=("Arial", 12),
            command=self.on_server_change
        )
        self.server_list.pack(fill="x", pady=(5, 0))
        
        # Server Management Buttons
        button_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=10)
        
        self.add_server_btn = ctk.CTkButton(
            button_frame,
            text="Add Server",
            font=("Arial", 12),
            height=35,
            command=self.show_add_server_dialog
        )
        self.add_server_btn.pack(fill="x", pady=(0, 5))
        
        self.discover_server_btn = ctk.CTkButton(
            button_frame,
            text="Discover Servers",
            font=("Arial", 12),
            height=35,
            command=self.discover_servers
        )
        self.discover_server_btn.pack(fill="x")
        
        # Settings button at bottom
        settings_btn = ctk.CTkButton(
            sidebar,
            text="Settings",
            font=("Arial", 12),
            height=35,
            command=self.show_settings_dialog
        )
        settings_btn.pack(side="bottom", fill="x", padx=20, pady=20)
        
    def create_chat_area(self):
        # Main chat container
        chat_container = ctk.CTkFrame(self)
        chat_container.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        chat_container.grid_rowconfigure(0, weight=1)
        chat_container.grid_columnconfigure(0, weight=1)
        
        # Chat history
        self.chat_history = ctk.CTkScrollableFrame(
            chat_container,
            fg_color="transparent"
        )
        self.chat_history.grid(row=0, column=0, sticky="nsew")
        
        # Input area
        input_frame = ctk.CTkFrame(chat_container)
        input_frame.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        input_frame.grid_columnconfigure(0, weight=1)
        
        self.chat_input = ctk.CTkEntry(
            input_frame,
            placeholder_text="Type your message here...",
            height=40,
            font=("Arial", 12)
        )
        self.chat_input.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        self.send_btn = ctk.CTkButton(
            input_frame,
            text="Send",
            width=100,
            height=40,
            font=("Arial", 12),
            command=self.send_message
        )
        self.send_btn.grid(row=0, column=1)
        
        # Bind enter key to send message
        self.chat_input.bind("<Return>", lambda e: self.send_message())
    
    def show_settings_dialog(self):
        SettingsDialog(self)
    
    def show_add_server_dialog(self):
        AddServerDialog(self)
    
    def discover_servers(self):
        # Update discovered servers list
        discovered = self.server_discovery.discovered_servers
        for server in discovered:
            if server not in self.known_servers:
                self.add_server(server)
        
        if discovered:
            messagebox.showinfo("Server Discovery", f"Found {len(discovered)} servers")
        else:
            messagebox.showinfo("Server Discovery", "No servers found")
    
    def add_server(self, server: MCPServer):
        if server not in self.known_servers:
            self.known_servers.append(server)
            self.update_server_list()
    
    def update_server_list(self):
        server_names = [server.name for server in self.known_servers]
        if not server_names:
            server_names = ["No servers available"]
        self.server_list.configure(values=server_names)
        if server_names[0] != "No servers available":
            self.server_list.set(server_names[0])
    
    def update_llm_list(self):
        models = self.ollama_client.available_models
        if not models:
            models = ["No models available"]
        self.llm_selector.configure(values=models)
        if models[0] != "No models available":
            self.llm_selector.set(models[0])
    
    def on_llm_change(self, choice):
        self.ollama_client.current_model = choice
        messagebox.showinfo("LLM Changed", f"Selected LLM: {choice}")
    
    def on_server_change(self, choice):
        if choice != "No servers available":
            messagebox.showinfo("Server Changed", f"Selected Server: {choice}")
    
    def send_message(self):
        message = self.chat_input.get().strip()
        if message:
            # Add user message
            ChatMessage(self.chat_history, message, is_user=True)
            # Clear input
            self.chat_input.delete(0, "end")
            
            # Get response from Ollama
            if self.ollama_client.current_model:
                response = self.ollama_client.generate_response(message)
                ChatMessage(self.chat_history, response, is_user=False)
            else:
                ChatMessage(self.chat_history, "Please select an LLM model first", is_user=False)

if __name__ == "__main__":
    app = MCPClient()
    app.mainloop()
