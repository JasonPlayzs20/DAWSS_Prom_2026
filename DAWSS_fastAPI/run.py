"""
Smart server starter that kills existing processes on port 8000
"""
import subprocess
import sys
import time
import platform

def kill_process_on_port(port=8000):
    """Kill any process running on the specified port"""
    system = platform.system()

    try:
        if system == "Windows":
            # Find process on Windows
            result = subprocess.run(
                f'netstat -ano | findstr :{port}',
                shell=True,
                capture_output=True,
                text=True
            )

            if result.stdout:
                # Extract PID (last column)
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    parts = line.split()
                    if len(parts) > 4:
                        pid = parts[-1]
                        subprocess.run(f'taskkill /PID {pid} /F', shell=True)
                        print(f"✓ Killed process {pid} on port {port}")
                        time.sleep(1)

        else:  # macOS/Linux
            result = subprocess.run(
                f'lsof -ti:{port}',
                shell=True,
                capture_output=True,
                text=True
            )

            if result.stdout:
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    if pid:
                        subprocess.run(f'kill -9 {pid}', shell=True)
                        print(f"✓ Killed process {pid} on port {port}")
                        time.sleep(1)

    except Exception as e:
        print(f"⚠ Could not kill existing process: {e}")

def start_server(port=8000):
    """Start the FastAPI server"""
    print(f"\nStarting FastAPI server on port {port}...")
    print(f"API: http://localhost:{port}")
    print(f"Docs: http://localhost:{port}/docs")
    print(f"Press Ctrl+C to stop\n")

    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "app.main:app",
            "--reload",
            "--port", str(port)
        ])
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped")

if __name__ == "__main__":
    PORT = 8000

    # Check if custom port provided
    if len(sys.argv) > 1:
        try:
            PORT = int(sys.argv[1])
        except ValueError:
            print("⚠ Invalid port number, using default 8000")

    # Kill existing process
    print(f"🔍 Checking for existing processes on port {PORT}...")
    kill_process_on_port(PORT)

    # Start server
    start_server(PORT)