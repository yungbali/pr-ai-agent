import subprocess
import time

def main():
    try:
        # Start FastAPI backend
        backend = subprocess.Popen(
            ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print("Started FastAPI backend on port 8000")
        time.sleep(2)  # Give backend time to start

        # Start Streamlit frontend
        frontend = subprocess.Popen(
            ["streamlit", "run", "frontend/app.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print("Started Streamlit frontend")

        # Keep both processes running
        backend.wait()
        frontend.wait()

    except KeyboardInterrupt:
        print("\nShutting down servers...")
        backend.terminate()
        frontend.terminate()

if __name__ == "__main__":
    main() 