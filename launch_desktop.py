#!/usr/bin/env python3
"""
Phiversity Desktop Launcher
A simple desktop application to launch and manage Phiversity
"""

import os
import sys
import subprocess
import webbrowser
import time
import socket
from pathlib import Path
from threading import Thread

try:
    import tkinter as tk
    from tkinter import ttk, messagebox, scrolledtext
    HAS_GUI = True
except ImportError:
    HAS_GUI = False
    print("Warning: tkinter not available, GUI mode disabled")


class PhiversityLauncher:
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.venv_dir = self.find_venv()
        self.python_exe = self.find_python()
        self.process = None
        self.port = 8000
        
    def find_venv(self):
        """Find virtual environment directory"""
        for name in ['.venv', 'venv', '.venv-1', '.venv312']:
            venv_path = self.root_dir / name
            if venv_path.exists():
                return venv_path
        return None
    
    def find_python(self):
        """Find Python executable in virtual environment"""
        if not self.venv_dir:
            return sys.executable
        
        if os.name == 'nt':  # Windows
            python_path = self.venv_dir / 'Scripts' / 'python.exe'
        else:  # Unix-like
            python_path = self.venv_dir / 'bin' / 'python'
        
        if python_path.exists():
            return str(python_path)
        return sys.executable
    
    def is_port_available(self, port):
        """Check if port is available"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                return True
        except OSError:
            return False
    
    def start_server(self, callback=None):
        """Start the Phiversity server"""
        if not self.venv_dir:
            if callback:
                callback("ERROR: Virtual environment not found!\n")
                callback("Please run setup first.\n")
            return False
        
        if callback:
            callback(f"Starting Phiversity server on port {self.port}...\n")
        
        # Check if port is already in use
        if not self.is_port_available(self.port):
            if callback:
                callback(f"WARNING: Port {self.port} already in use!\n")
                callback("Server may already be running.\n")
            return True  # Assume server is already running
        
        try:
            # Start uvicorn server
            cmd = [
                str(self.python_exe),
                '-m', 'uvicorn',
                'api.app:app',
                '--host', '0.0.0.0',
                '--port', str(self.port),
                '--reload'
            ]
            
            if callback:
                callback(f"Command: {' '.join(cmd)}\n")
            
            # Start process
            if os.name == 'nt':  # Windows
                self.process = subprocess.Popen(
                    cmd,
                    cwd=str(self.root_dir),
                    creationflags=subprocess.CREATE_NO_WINDOW,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )
            else:
                self.process = subprocess.Popen(
                    cmd,
                    cwd=str(self.root_dir),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )
            
            # Wait a bit for server to start
            time.sleep(2)
            
            if callback:
                callback("Server started successfully!\n")
            
            return True
            
        except Exception as e:
            if callback:
                callback(f"ERROR: Failed to start server: {e}\n")
            return False
    
    def stop_server(self):
        """Stop the server"""
        if self.process:
            self.process.terminate()
            self.process.wait(timeout=5)
            self.process = None
    
    def open_browser(self):
        """Open browser to Phiversity URL"""
        url = f"http://127.0.0.1:{self.port}"
        webbrowser.open(url)
    
    def run_cli(self):
        """Run command-line interface"""
        print("""
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║              🎬 PHIVERSITY DESKTOP LAUNCHER 🎬             ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
        """)
        
        print("Starting Phiversity...")
        
        if self.start_server(print):
            print(f"\n✅ Server running at: http://127.0.0.1:{self.port}")
            print("\nOpening browser in 3 seconds...")
            time.sleep(3)
            self.open_browser()
            print("\n✅ Browser opened!")
            print("\nPress Ctrl+C to stop the server")
            
            try:
                # Keep running
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n\nStopping server...")
                self.stop_server()
                print("✅ Server stopped. Goodbye!")
        else:
            print("\n❌ Failed to start server")
            print("Please check the error messages above")
    
    def run_gui(self):
        """Run graphical user interface"""
        if not HAS_GUI:
            print("ERROR: GUI not available, falling back to CLI")
            return self.run_cli()
        
        window = tk.Tk()
        window.title("Phiversity - AI Video Generator")
        window.geometry("700x550")
        window.resizable(False, False)
        
        # Set theme colors
        bg_color = "#0f0f23"
        fg_color = "#f8fafc"
        accent_color = "#6366f1"
        
        window.configure(bg=bg_color)
        
        # Header
        header_frame = tk.Frame(window, bg=bg_color)
        header_frame.pack(fill=tk.X, padx=20, pady=20)
        
        title_label = tk.Label(
            header_frame,
            text="🎬 PHIVERSITY",
            font=("Arial", 32, "bold"),
            bg=bg_color,
            fg=accent_color
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            header_frame,
            text="AI-Powered Educational Video Generator",
            font=("Arial", 12),
            bg=bg_color,
            fg=fg_color
        )
        subtitle_label.pack()
        
        # Status Frame
        status_frame = tk.Frame(window, bg=bg_color)
        status_frame.pack(fill=tk.X, padx=20, pady=10)
        
        status_label = tk.Label(
            status_frame,
            text="Status: Ready",
            font=("Arial", 11),
            bg=bg_color,
            fg="#10b981"
        )
        status_label.pack(anchor=tk.W)
        
        # Log area
        log_frame = tk.Frame(window, bg=bg_color)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        log_text = scrolledtext.ScrolledText(
            log_frame,
            height=15,
            bg="#1a1a3e",
            fg=fg_color,
            font=("Consolas", 9),
            insertbackground=fg_color
        )
        log_text.pack(fill=tk.BOTH, expand=True)
        
        def log(message):
            log_text.insert(tk.END, message)
            log_text.see(tk.END)
            window.update()
        
        # Button Frame
        button_frame = tk.Frame(window, bg=bg_color)
        button_frame.pack(fill=tk.X, padx=20, pady=20)
        
        def start_clicked():
            status_label.config(text="Status: Starting...", fg="#f59e0b")
            start_btn.config(state=tk.DISABLED)
            
            # Start server in thread
            def start_thread():
                if self.start_server(log):
                    status_label.config(text="Status: Running", fg="#10b981")
                    log("✅ Server started successfully!\n")
                    log(f"🌐 URL: http://127.0.0.1:{self.port}\n\n")
                    log("Opening browser...\n")
                    time.sleep(1)
                    self.open_browser()
                    log("✅ Browser opened!\n")
                    stop_btn.config(state=tk.NORMAL)
                    browser_btn.config(state=tk.NORMAL)
                else:
                    status_label.config(text="Status: Error", fg="#ef4444")
                    start_btn.config(state=tk.NORMAL)
            
            Thread(target=start_thread, daemon=True).start()
        
        def stop_clicked():
            status_label.config(text="Status: Stopping...", fg="#f59e0b")
            stop_btn.config(state=tk.DISABLED)
            browser_btn.config(state=tk.DISABLED)
            
            self.stop_server()
            log("🛑 Server stopped\n")
            status_label.config(text="Status: Stopped", fg="#ef4444")
            start_btn.config(state=tk.NORMAL)
        
        def browser_clicked():
            self.open_browser()
            log("🌐 Browser opened\n")
        
        def quit_clicked():
            if self.process:
                self.stop_server()
            window.destroy()
        
        # Buttons
        start_btn = tk.Button(
            button_frame,
            text="▶️ Start Server",
            command=start_clicked,
            font=("Arial", 11, "bold"),
            bg=accent_color,
            fg="white",
            padx=20,
            pady=10,
            relief=tk.FLAT,
            cursor="hand2"
        )
        start_btn.pack(side=tk.LEFT, padx=5)
        
        stop_btn = tk.Button(
            button_frame,
            text="⏹️ Stop Server",
            command=stop_clicked,
            font=("Arial", 11),
            bg="#ef4444",
            fg="white",
            padx=20,
            pady=10,
            relief=tk.FLAT,
            cursor="hand2",
            state=tk.DISABLED
        )
        stop_btn.pack(side=tk.LEFT, padx=5)
        
        browser_btn = tk.Button(
            button_frame,
            text="🌐 Open Browser",
            command=browser_clicked,
            font=("Arial", 11),
            bg="#10b981",
            fg="white",
            padx=20,
            pady=10,
            relief=tk.FLAT,
            cursor="hand2",
            state=tk.DISABLED
        )
        browser_btn.pack(side=tk.LEFT, padx=5)
        
        quit_btn = tk.Button(
            button_frame,
            text="❌ Quit",
            command=quit_clicked,
            font=("Arial", 11),
            bg="#6b7280",
            fg="white",
            padx=20,
            pady=10,
            relief=tk.FLAT,
            cursor="hand2"
        )
        quit_btn.pack(side=tk.RIGHT, padx=5)
        
        # Initial log message
        log("Welcome to Phiversity!\n")
        log("Click 'Start Server' to begin.\n\n")
        
        if not self.venv_dir:
            log("⚠️ WARNING: Virtual environment not found!\n")
            log("Please run setup first.\n")
            start_btn.config(state=tk.DISABLED)
        
        # Handle window close
        window.protocol("WM_DELETE_WINDOW", quit_clicked)
        
        # Center window
        window.update_idletasks()
        x = (window.winfo_screenwidth() // 2) - (window.winfo_width() // 2)
        y = (window.winfo_screenheight() // 2) - (window.winfo_height() // 2)
        window.geometry(f"+{x}+{y}")
        
        window.mainloop()


def main():
    """Main entry point"""
    launcher = PhiversityLauncher()
    
    # Check for --cli flag
    if '--cli' in sys.argv or '--no-gui' in sys.argv:
        launcher.run_cli()
    elif HAS_GUI:
        launcher.run_gui()
    else:
        launcher.run_cli()


if __name__ == '__main__':
    main()
