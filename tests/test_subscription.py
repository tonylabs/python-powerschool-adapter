import os
import json
import unittest
from faker import Faker
from dotenv import load_dotenv
from powerschool_adapter.powerschool import PowerSchool

load_dotenv()
fake = Faker()

# Load sensitive data from environment variables
SERVER_ADDRESS = os.getenv("POWERSCHOOL_SERVER_ADDRESS")
CLIENT_ID = os.getenv("POWERSCHOOL_CLIENT_ID")
CLIENT_SECRET = os.getenv("POWERSCHOOL_CLIENT_SECRET")

powerschool = PowerSchool(
    server_address=SERVER_ADDRESS,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
)

class TestSubscription(unittest.TestCase):
    """
    def test_create_subscription(self):
        response = powerschool.to('/ws/v1/event_subscription').method('PUT').send()
        student = response.to_json()
        student_data = json.loads(student)
        print(json.dumps(student_data, indent=4))
    """

    def test_review_subscription(self):
        response = powerschool.to('/ws/v1/event_subscription').method('GET').send()
        student = response.to_json()
        student_data = json.loads(student)
        print(json.dumps(student_data, indent=4))

    def remove_subscription(self):
        response = powerschool.to('/ws/v1/event_subscription').method('DELETE').send()
        student = response.to_json()
        student_data = json.loads(student)
        print(json.dumps(student_data, indent=4))

if __name__ == "__main__":
    unittest.main()