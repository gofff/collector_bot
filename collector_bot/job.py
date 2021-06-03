from typing import List

class Job:
    def __init__(self, job_id: int) -> None:
        self.job_id: int = job_id
        self.name: str = ""
        self.chat_id: int = 0
        self.times: List[str] = []

    def set_name(self, name: str) -> None:
        self.name = name

    def set_chat_id(self, chat_id: int) -> None:
        self.chat_id = chat_id

    def set_times(self, times: List[str]) -> None:
        self.times = times

    def dump(self) -> None:
        print("=== Job ===")
        print(f"jid: {self.job_id}")
        print(f"cid: {self.chat_id}")
        print(f"name: {self.name}")
        print(f"times: {self.times}")