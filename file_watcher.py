import time
import subprocess
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class CodeRunner(FileSystemEventHandler):
    def __init__(self):
        self.last_modified = time.time()
        self.code_process = None
        
    def on_modified(self, event):
        if event.src_path.endswith('result.txt'):
            current_time = time.time()
            if current_time - self.last_modified > 1:  # Debounce
                self.last_modified = current_time
                self.run_code()
                
    def run_code(self):
        code_path = os.path.join(os.path.dirname(__file__), 'code', 'code.py')
        if not os.path.exists(code_path):
            print(f"Error: {code_path} not found!")
            return
            
        print(f"Result file changed, running {code_path}...")
        
        # Kill existing process if running
        if self.code_process and self.code_process.poll() is None:
            self.code_process.terminate()
            self.code_process.wait()
        
        # Start code.py as a new process
        try:
            self.code_process = subprocess.Popen(['python', code_path])
        except Exception as e:
            print(f"Error running code.py: {e}")

def start_watching():
    # Ensure directories exist
    base_dir = os.path.dirname(__file__)
    output_dir = os.path.join(base_dir, 'output')
    code_dir = os.path.join(base_dir, 'code')
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    if not os.path.exists(code_dir):
        os.makedirs(code_dir)
    
    event_handler = CodeRunner()
    observer = Observer()
    
    # Watch the output directory
    observer.schedule(event_handler, output_dir, recursive=False)
    observer.start()
    
    print(f"Watching for changes in {output_dir}\\result.txt")
    print("Press Ctrl+C to stop...")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        if event_handler.code_process:
            event_handler.code_process.terminate()
    observer.join()

if __name__ == "__main__":
    start_watching()
