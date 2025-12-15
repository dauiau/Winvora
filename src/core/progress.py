from typing import Callable, Optional
from threading import Thread
import time


ProgressCallback = Callable[[int, str], None]


class ProgressManager:
    def __init__(self):
        self.current_operation: Optional[str] = None
        self.current_progress: int = 0
        self.current_message: str = ""
        self.is_running: bool = False
        self.callbacks: list[ProgressCallback] = []
    
    def add_callback(self, callback: ProgressCallback):
        self.callbacks.append(callback)
    
    def remove_callback(self, callback: ProgressCallback):
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def start(self, operation: str):
        self.current_operation = operation
        self.current_progress = 0
        self.current_message = f"Starting {operation}..."
        self.is_running = True
        self._notify(0, self.current_message)
    
    def update(self, progress: int, message: str):
        self.current_progress = min(100, max(0, progress))
        self.current_message = message
        self._notify(self.current_progress, message)
    
    def complete(self, message: str = "Complete"):
        self.current_progress = 100
        self.current_message = message
        self.is_running = False
        self._notify(100, message)
    
    def error(self, message: str):
        self.current_message = f"Error: {message}"
        self.is_running = False
        self._notify(self.current_progress, self.current_message)
    
    def _notify(self, progress: int, message: str):
        for callback in self.callbacks:
            try:
                callback(progress, message)
            except Exception:
                pass
    
    def get_status(self) -> dict:
        return {
            "operation": self.current_operation,
            "progress": self.current_progress,
            "message": self.current_message,
            "is_running": self.is_running,
        }


class BackgroundTask:
    def __init__(self, name: str, func, *args, **kwargs):
        self.name = name
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.thread: Optional[Thread] = None
        self.result = None
        self.error = None
        self.is_running = False
        self.is_complete = False
    
    def start(self):
        if self.is_running:
            return False
        
        self.is_running = True
        self.thread = Thread(target=self._run)
        self.thread.daemon = True
        self.thread.start()
        return True
    
    def _run(self):
        try:
            self.result = self.func(*self.args, **self.kwargs)
        except Exception as e:
            self.error = str(e)
        finally:
            self.is_running = False
            self.is_complete = True
    
    def join(self, timeout=None):
        if self.thread:
            self.thread.join(timeout)
    
    def get_result(self):
        return self.result, self.error


class TaskQueue:
    def __init__(self):
        self.tasks: list[BackgroundTask] = []
        self.current_task: Optional[BackgroundTask] = None
        self.auto_start = True
    
    def add_task(self, task: BackgroundTask):
        self.tasks.append(task)
        if self.auto_start and not self.current_task:
            self._start_next()
    
    def _start_next(self):
        if not self.tasks:
            self.current_task = None
            return
        
        self.current_task = self.tasks.pop(0)
        self.current_task.start()
    
    def update(self):
        if self.current_task and self.current_task.is_complete:
            self._start_next()
    
    def get_queue_status(self) -> dict:
        return {
            "current_task": self.current_task.name if self.current_task else None,
            "pending_tasks": len(self.tasks),
            "is_busy": self.current_task is not None,
        }
