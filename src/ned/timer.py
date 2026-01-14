import threading
import time


class BackgroundTimer:
    def __init__(self):
        self.milliseconds = 0
        self.running = False
        self.thread = None
        self.lock = threading.Lock()

    def _timer_loop(self):
        while self.running:
            time.sleep(0.001)
            with self.lock:
                self.milliseconds += 1

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._timer_loop, daemon=True)
            self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()

    def get_time(self):
        with self.lock:
            return self.milliseconds

    def set_time(self, value):
        with self.lock:
            self.milliseconds = value

    def increment_time(self, value):
        with self.lock:
            self.milliseconds += value

    def decrement_time(self, value):
        with self.lock:
            self.milliseconds -= value

    def reset(self):
        with self.lock:
            self.milliseconds = 0
