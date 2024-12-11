import threading

class TokenMetricsTracker:
    def __init__(self):
        self.prompt_token_count = 0
        self.response_token_count = 0
        self.lock = threading.Lock()

    def add_prompt_tokens(self, count):
        with self.lock:
            self.prompt_token_count += count

    def add_response_tokens(self, count):
        with self.lock:
            self.response_token_count += count

    def get_total_tokens(self):
        with self.lock:
            return self.prompt_token_count + self.response_token_count

    def reset(self):
        with self.lock:
            self.prompt_token_count = 0
            self.response_token_count = 0