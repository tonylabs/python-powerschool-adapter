import os
import json
import unittest
import colorama
import faker
from faker import Faker
from colorama import Fore
from dotenv import load_dotenv
from psps.powerschool import PowerSchool

load_dotenv()
fake = Faker()
colorama.init(autoreset=True)

# Load sensitive data from environment variables
SERVER_ADDRESS = os.getenv("POWERSCHOOL_SERVER_ADDRESS")
CLIENT_ID = os.getenv("POWERSCHOOL_CLIENT_ID")
CLIENT_SECRET = os.getenv("POWERSCHOOL_CLIENT_SECRET")

powerschool = PowerSchool(
    server_address=SERVER_ADDRESS,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
)

class TestPowerSchool(unittest.TestCase):
    def test_expansions(self):
        response = powerschool.to('/ws/v1/student').set_id(52).extensions(['u_admission']).get()
        student = response.to_json()
        student_data = json.loads(student)
        print(Fore.GREEN + json.dumps(student_data, indent=4))

if __name__ == "__main__":
    unittest.main()