import time
import subprocess
import os
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ResultFileHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_modified = time.time()
        self.main_process = None
        
    def on_modified(self, event):
        if event.src_path.endswith('result.txt'):
            current_time = time.time()
            if current_time - self.last_modified > 1:
                self.last_modified = current_time
                print("Result file changed, running code.py...")
                
                # Kill existing process if running
                if self.main_process and self.main_process.poll() is None:
                    self.main_process.terminate()
                    self.main_process.wait()
                
                # Start code.py as a new process with correct Python environment
                try:
                    # Use the same Python interpreter that's running this script
                    python_exe = sys.executable
                    code_path = os.path.join(os.path.dirname(__file__), 'code', 'code.py')
                    
                    # Create environment variables for the subprocess
                    env = os.environ.copy()
                    env['PYTHONPATH'] = os.path.dirname(__file__)
                    
                    # Run pip install if needed
                    subprocess.run([python_exe, '-m', 'pip', 'install', 'pyserial'], 
                                check=True)
                    
                    # Start the main process
                    self.main_process = subprocess.Popen(
                        [python_exe, code_path],
                        env=env,
                        cwd=os.path.dirname(__file__)
                    )
                except Exception as e:
                    print(f"Error running code.py: {e}")

def start_watching():
    event_handler = ResultFileHandler()
    observer = Observer()
    
    # Watch the output directory
    watch_path = os.path.join(os.path.dirname(__file__), 'output')
    observer.schedule(event_handler, watch_path, recursive=False)
    observer.start()
    
    print(f"Watching for changes in {watch_path}\\result.txt")
    print("Press Ctrl+C to stop...")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        if event_handler.main_process:
            event_handler.main_process.terminate()
    observer.join()

if __name__ == "__main__":
    start_watching()
