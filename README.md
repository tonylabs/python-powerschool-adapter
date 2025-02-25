# PowerSchool Python Adapter

The PowerSchool Adapter is a Python package designed to facilitate seamless integration with the PowerSchool Student Information System (SIS). It provides a set of tools and functionalities that enable developers to interact programmatically with PowerSchool’s data and services, streamlining tasks such as data retrieval, updates, and synchronization between PowerSchool and other applications. This adapter is particularly useful for educational institutions and software developers aiming to enhance their systems’ interoperability with PowerSchool, ensuring efficient data management and operational workflows.

## Prerequisites

This package is to be used with alongside a PowerSchool plugin that has enabled <oauth/> in the plugin.xml. This guide assumes you have PowerSchool API and plugin knowledge and does not cover the details of a plugin or its API.

## Installation

```bash
pip install powerschool-adapter
```

## Configuration

You need to set some variables in `.env`.

```dotenv
POWERSCHOOL_SERVER_ADDRESS=
POWERSCHOOL_CLIENT_ID=
POWERSCHOOL_CLIENT_SECRET=
```

## API

#### `PowerSchool`

The PowerSchool token is automatically retrieved upon executing an API call.

```python
from dotenv import load_dotenv
from powerschool_adapter.powerschool import PowerSchool

load_dotenv()

SERVER_ADDRESS = os.getenv("POWERSCHOOL_SERVER_ADDRESS")
CLIENT_ID = os.getenv("POWERSCHOOL_CLIENT_ID")
CLIENT_SECRET = os.getenv("POWERSCHOOL_CLIENT_SECRET")

powerschool = PowerSchool(
	server_address=SERVER_ADDRESS,
	client_id=CLIENT_ID,
	client_secret=CLIENT_SECRET
)
```

#### `set_table(table)`

_Aliases: table()_

The set_table function is used to specify which database table should be queried.

```python
response = powerschool.table('students').projection(["DCID", "STUDENT_NUMBER", "LASTFIRST"]).set_method("GET").send()
student_data = json.loads(response.to_json())
print(json.dumps(student_data, indent=4))
```

#### `set_endpoint(query)`

_Aliases: to_endpoint(), to()_

```python
response = powerschool.set_endpoint("/ws/v1/student").set_id(1).get()
student_data = json.loads(response.to_json())
print(json.dumps(student_data, indent=4))
```

#### `get_endpoint()`

Return the current endpoint

#### `setId($id)`

_Aliases: for_id()_

```python
response = powerschool.to("/ws/v1/student").set_id(1).get()
student_data = json.loads(response.to_json())
print(json.dumps(student_data, indent=4))
```

### `extensions`

```python
response = powerschool.to('/ws/v1/student').set_id(52).expansions(['demographics', 'addresses', 'alerts', 'phones', 'school_enrollment', 'ethnicity_race', 'contact', 'contact_info', 'initial_enrollment']).get()
```

#### `q(expression)`

_Aliases: query_expression()_

Sets the `q` variable to the given FIQL expression.

```python
response = powerschool.set_endpoint("/ws/v1/student").q("name.last_name==Ada*").get()
student_data = json.loads(response.to_json())
print(json.dumps(student_data, indent=4))
```

#### `paginator()`

```python
powerschool.table('students').projection(["ID", "STUDENT_NUMBER", "FIRST_NAME"]).sort('STUDENT_NUMBER')
		while True:
			students = powerschool.paginate(page_size=1)
			if not students:
				break
			for student in students:
				print(student)
```