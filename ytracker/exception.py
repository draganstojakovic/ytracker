class ProgramShouldExit(Exception):
    def __init__(self, msg: str, code: int):
        self.msg = msg
        self.code = code
