import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from interface import create_interface
from utils.config import SETTINGS

def main():
    app = create_interface()
    app.launch(
        server_name=SETTINGS.host,
        server_port=SETTINGS.port,
        root_path="/tokenizer"
    )

if __name__ == "__main__":
    main() 