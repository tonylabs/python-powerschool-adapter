import os
import unittest
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
		powerschool.table('students').projection(["ID", "STUDENT_NUMBER", "FIRST_NAME"]).q("enroll_status==0").sort('STUDENT_NUMBER')
		while True:
			students = powerschool.paginate(page_size=1)
			if not students:
				break
			for student in students:
				print(student)

if __name__ == "__main__":
	unittest.main()