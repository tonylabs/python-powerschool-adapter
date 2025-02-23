import os
import json
import unittest
from faker import Faker
from dotenv import load_dotenv
from powerschool_adapter.powerschool import PowerSchool

load_dotenv()

# Load sensitive data from environment variables
SERVER_ADDRESS = os.getenv("POWERSCHOOL_SERVER_ADDRESS")
CLIENT_ID = os.getenv("POWERSCHOOL_CLIENT_ID")
CLIENT_SECRET = os.getenv("POWERSCHOOL_CLIENT_SECRET")

powerschool = PowerSchool(
    server_address=SERVER_ADDRESS,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
)

class TestPagination(unittest.TestCase):
	def test_pagination(self):
		response = powerschool.table('students').projection(["DCID", "STUDENT_NUMBER", "FIRST_NAME", "LAST_NAME", "LASTFIRST"]).sort('STUDENT_NUMBER').page_size(1).paginate()

		# Loop through all pages
		while True:
			response = response.next_page()
			if not response:
				break
			student_data = json.loads(response.to_json())
			print(json.dumps(student_data, indent=4))

if __name__ == "__main__":
	unittest.main()