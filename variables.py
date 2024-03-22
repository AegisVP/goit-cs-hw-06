from pathlib import Path 

from dotenv import dotenv_values   # pip install python-dotenv
from os import environ


config = {
    **dotenv_values(".env"),  # load shared development variables
    **environ,  # override loaded values with environment variables
}
BASE_PATH = Path(__file__).resolve().parent

if __name__ == "__main__":
    config = dict()
