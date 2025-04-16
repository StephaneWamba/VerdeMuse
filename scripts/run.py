"""
Script to run both the FastAPI backend and Streamlit frontend simultaneously.
This provides a convenient way to start the entire VerdeMuse application.
"""

import os
import sys
import subprocess
import time
import signal
import platform
from dotenv import load_dotenv

# Add the project root to the path so we can import our modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables
load_dotenv()

# Process holders
processes = []

def start_backend():
    """Start the FastAPI backend server."""
    host = os.getenv("API_HOST", "0.0.0.0")
    port = os.getenv("API_PORT", "8000")
    print(f"\n🚀 Starting FastAPI backend on http://{host}:{port}")
    
    backend_process = subprocess.Popen(
        ["uvicorn", "src.api.main:app", "--host", host, "--port", port, "--reload"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    processes.append(backend_process)
    return backend_process

def start_frontend():
    """Start the Streamlit frontend."""
    print("\n🌿 Starting Streamlit frontend on http://localhost:8501")
    
    frontend_process = subprocess.Popen(
        ["streamlit", "run", "src.presentation.streamlit.app.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    processes.append(frontend_process)
    return frontend_process

def process_output(process, prefix):
    """Process and print output from a subprocess with a prefix."""
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            print(f"{prefix} {output.strip()}")
    
    rc = process.poll()
    return rc

def cleanup(signum, frame):
    """Clean up processes when terminating the script."""
    print("\n🛑 Stopping VerdeMuse services...")
    for p in processes:
        try:
            if platform.system() == "Windows":
                # Windows requires a different approach to terminate processes
                subprocess.call(['taskkill', '/F', '/T', '/PID', str(p.pid)])
            else:
                p.send_signal(signal.SIGTERM)
                p.wait()
        except Exception as e:
            print(f"Error stopping process: {e}")
    
    print("✅ All services stopped.")
    sys.exit(0)

if __name__ == "__main__":
    # Register signal handlers
    signal.signal(signal.SIGINT, cleanup)
    if platform.system() != "Windows":
        signal.signal(signal.SIGTERM, cleanup)
    
    try:
        print("🌿 Starting VerdeMuse Intelligent Customer Support Virtual Assistant")
        
        # Start backend
        backend_process = start_backend()
        
        # Wait a moment for backend to start
        time.sleep(2)
        
        # Start frontend
        frontend_process = start_frontend()
        
        print("\n✨ VerdeMuse is now running!")
        print("📊 FastAPI backend: http://localhost:8000")
        print("📚 API Documentation: http://localhost:8000/docs")
        print("💬 Streamlit frontend: http://localhost:8501")
        print("\nPress CTRL+C to stop all services.\n")
        
        # Monitor outputs
        while True:
            backend_output = backend_process.stdout.readline()
            if backend_output:
                print(f"[API] {backend_output.strip()}")
            
            frontend_output = frontend_process.stdout.readline()
            if frontend_output:
                print(f"[UI] {frontend_output.strip()}")
            
            # Check if processes are still running
            if backend_process.poll() is not None and frontend_process.poll() is not None:
                print("Both services have stopped. Exiting.")
                break
            
            # Small sleep to prevent high CPU usage
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
    finally:
        cleanup(None, None)