import os
import json
import sys
import unittest
import colorama
import faker
from faker import Faker
from colorama import Fore
from dotenv import load_dotenv
from powerschool_adapter.powerschool import PowerSchool

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
    def test_token(self):
        if not CLIENT_ID or not CLIENT_SECRET:
            self.fail("Client ID or Client Secret not set in environment variables")
        print(Fore.LIGHTBLUE_EX + powerschool.get_token())

    def test_table(self):
        print(Fore.LIGHTRED_EX + "Testing table method")
        response = powerschool.table('students').projection(['ID', 'DCID', 'STUDENT_NUMBER', 'LASTFIRST']).sort('lastfirst').method(powerschool.GET).send()
        # Output Response
        student = response.to_json()
        student_data = json.loads(student)
        print(Fore.LIGHTCYAN_EX + json.dumps(student_data, indent=4))

    def test_set_id(self):
        response = powerschool.table('Students').set_id(1).projection(['ID', 'DCID', 'STUDENT_NUMBER', 'LASTFIRST', 'FAMILY_IDENT']).method(powerschool.GET).send()
        student = response.to_json()
        student_data = json.loads(student)
        print(Fore.LIGHTYELLOW_EX + json.dumps(student_data, indent=4))

if __name__ == "__main__":
    unittest.main()