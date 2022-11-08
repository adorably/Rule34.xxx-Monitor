import os 

class System:
    def __init__(self) -> None:
        self.RED = '\x1b[1;31m'
        self.CYAN = '\x1b[1;36m'
        self.GREEN = '\x1b[38;5;48m'
        self.YELLOW = '\x1b[1;33m'
        self.DEFAULT = '\x1b[39m'
        self.RESET = '\x1b[0m'
        self.FLUSH = '\x1b[0K'
    
    @staticmethod
    def cls():
        os.system('cls' if os.name == 'nt' else 'clear')

system = System()