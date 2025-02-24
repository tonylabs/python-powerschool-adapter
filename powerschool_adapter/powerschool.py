"""
Copyright © 2025 TONYLABS TECH CO., LTD..

Permission is hereby granted, free of charge, to any person obtaining a copy of this software
and associated documentation files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or
substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING
BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES, OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT, OR OTHERWISE, ARISING
FROM, OUT OF, OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from .request import Request
from .response import Response
from .paginator import Paginator
from urllib.parse import parse_qs

class PowerSchool:
	GET = "GET"
	POST = "POST"
	PUT = "PUT"
	PATCH = "PATCH"
	DELETE = "DELETE"

	def __init__(self, server_address, client_id, client_secret, cache_key="powerschool"):
		self.request = Request(server_address, client_id, client_secret, cache_key)
		self.request.authenticate()
		self.endpoint = None
		self.http_method = self.GET
		self.data = {}  # Dictionary to hold request data
		self.options = {}  # Dictionary to hold request options
		self.query_string = {}  # Dictionary to hold query string parameters
		self.table_name: str | None = None
		self.id: str | int | None = None
		self.include_projection: bool = False
		self.response_as_json: bool = True
		self.page_key: str = "record"
		self.paginator = None

	def get_request(self) -> Request:
		return self.request

	def reset(self):
		self.endpoint = None
		self.http_method = None
		self.data = {}
		self.query_string = {}
		self.table_name = None
		self.include_projection = False
		self.response_as_json = True
		self.page_key = "record"
		self.paginator = None

	def set_table(self, table: str):
		self.table_name = table.split('/')[-1]  # Extract the part after the last / in the table string
		self.endpoint = table if table.startswith('/') else f"/ws/schema/table/{table}"
		self.include_projection = True
		self.page_key = "record"
		return self

	def table(self, table: str):
		return self.set_table(table)

	def set_id(self, resource_id: str | int):
		self.endpoint += f"/{resource_id}"
		self.id = resource_id
		return self

	def for_id(self, resource_id: str | int):
		return self.set_id(resource_id)

	def resource(self, endpoint: str, method: str = None, data: dict = None):
		self.endpoint = endpoint
		self.include_projection = False
		if method is not None:
			self.http_method = method
		if data:
			self.set_data(data)
		# If the method and data are set, automatically send the request
		if self.http_method is not None and self.data:
			return self.send()
		return self

	def exclude_projection(self):
		self.include_projection = False
		return self

	def without_projection(self):
		return self.exclude_projection()

	def set_endpoint(self, endpoint: str):
		self.endpoint = endpoint
		self.page_key = endpoint.split('/')[-1]
		return self.exclude_projection()

	def to_endpoint(self, endpoint: str):
		return self.set_endpoint(endpoint)

	def to(self, endpoint: str):
		return self.set_endpoint(endpoint)

	def get_endpoint(self):
		return self.endpoint

	def set_named_query(self, query_name: str, data: dict = None):
		self.endpoint = query_name if query_name.startswith('/') else f"/ws/schema/query/{query_name}"
		self.page_key = "record"
		if data:
			return self.set_data(data).post()
		self.include_projection = False
		return self.set_method(self.POST)

	""" Alias of set_named_query """

	def named_query(self, query: str, data: dict = None):
		return self.set_named_query(query, data)

	""" Alias of set_named_query """

	def power_query(self, query_name: str, data: dict = None):
		return self.set_named_query(query_name, data)

	""" Alias of set_named_query """

	def pq(self, query_name: str, data: dict = None):
		return self.set_named_query(query_name, data)

	def set_data(self, data: dict):
		self.data = self.cast_to_values_string(data)
		return self

	def with_data(self, data: dict):
		return self.set_data(data)

	def set_data_item(self, key: str, value: str | bool | dict | list):
		self.data[key] = self.cast_to_values_string(value)
		return self

	def with_query_string(self, query):
		if isinstance(query, dict):
			self.query_string = query
		elif isinstance(query, str):
			# Remove leading '?' if present
			query = query.lstrip('?')
			# Parse the query string into a dictionary
			parsed = parse_qs(query)
			# Convert list values to single items if only one value exists
			self.query_string = {k: v[0] if len(v) == 1 else v for k, v in parsed.items()}
		return self

	def query(self, query_string: str | list):
		return self.with_query_string(query_string)

	def add_query_param(self, key, value):
		self.query_string[key] = value
		return self

	def has_query_param(self, key):
		return key in self.query_string

	def q(self, query: str):
		return self.add_query_param('q', query)

	def query_expression(self, expression: str):
		return self.q(expression)

	def adhoc_filter(self, expression: str):
		return self

	def filter(self, expression: str):
		return self.adhoc_filter(expression)

	def projection(self, projection_fields: str | list):
		if isinstance(projection_fields, list):
			projection_fields = ",".join(projection_fields)
		self.add_query_param("projection", projection_fields)
		self.include_projection = True
		return self

	def page_size(self, size):
		self.add_query_param("pagesize", size)
		return self

	def page(self, page):
		return self.add_query_param("page", page)

	def sort(self, columns: str | list, descending=False):
		if isinstance(columns, list):
			columns = ",".join(columns)
		self.add_query_param("sort", columns)
		self.add_query_param("sortdescending", "true" if descending else "false")
		return self

	def adhoc_order(self, expression: str):
		return self.add_query_param('order', expression)

	def order(self, expression: str):
		return self.adhoc_order(expression)

	def include_count(self):
		self.add_query_param("count", "true")
		return self

	def data_version(self, version: int | str, application_name: str):
		# The $dataversion parameter is prefixed with $ because it's a special PowerSchool API parameter that:
		self.set_data_item("$dataversion", version).set_data_item("$dataversion_applicationname", application_name)
		return self

	def with_data_version(self, version: int, application_name: str):
		return self.data_version(version, application_name)

	def expansions(self, expansions: str | list):
		if isinstance(expansions, list):
			expansions = ",".join(expansions)
		self.add_query_param("expansions", expansions)
		return self

	def with_expansions(self, expansions: str | list):
		return self.expansions(expansions)

	def with_expansion(self, expansion: str):
		return self.with_expansions(expansion)

	def extensions(self, extensions: str | list):
		if isinstance(extensions, list):
			extensions = ",".join(extensions)
		self.add_query_param("extensions", extensions)
		return self

	def with_extensions(self, extensions: str | list):
		return self.extensions(extensions)

	def with_extension(self, extension: str):
		return self.extensions(extension)

	def get_subscription_changes(self, application: str, version: int):
		self.set_endpoint(f"/ws/dataversion/{application}/{version}")
		self.set_method(self.GET)
		return self.send()

	def count(self):
		self.endpoint += "/count"
		self.include_projection = False
		return self.get()

	def raw(self):
		self.response_as_json = False
		return self

	def as_json_response(self):
		self.response_as_json = True
		return self

	"""
	Recursively casts all values in the data dictionary to strings.
	Handles nested dictionaries and lists.
	"""

	def cast_to_values_string(self, data: dict | list | bool):
		if isinstance(data, dict):
			return {key: self.cast_to_values_string(value) for key, value in data.items()}
		elif isinstance(data, list):
			return ','.join(str(self.cast_to_values_string(item)) for item in data)
		elif isinstance(data, bool):
			return "1" if data else "0"
		elif data is None:
			return ""
		elif isinstance(data, (int, float)):
			return str(data)
		else:
			return str(data).strip()

	"""
	Builds the JSON structure for the request body.
	This handles cases for table-based requests, IDs, and plain data.
	"""

	def build_request_json(self):
		if self.http_method in [self.GET, self.DELETE]:
			return self  # No JSON body for GET/DELETE requests

		# Reset the json object from previous requests
		self.options['json'] = {}

		# Add table-specific data if a table is set
		if self.table_name:
			self.options['json']['tables'] = {self.table_name: self.data}

		# Add ID if set
		if self.id:
			self.options['json']['id'] = self.id
			self.options['json']['name'] = self.table_name

		# If there's no table, use the data directly
		if self.data and not self.table_name:
			self.options['json'] = self.data

		# Remove the json option if there is nothing there
		if not self.options['json']:
			del self.options['json']

		return self

	"""
	Builds the query string for the request.
	Automatically includes `projection=*` for GET requests if not already set.
	"""

	def build_request_query(self):
		if self.http_method not in {self.GET, self.POST}:  # Check if method is not GET or POST
			return self

		self.options['params'] = ""
		query_parts = []

		# Add existing query string parameters
		for key, value in self.query_string.items():
			query_parts.append(f"{key}={value}")

		# Include `projection=*` if applicable
		if self.include_projection and not self.has_query_param("projection"):
			query_parts.append("projection=*")

		# Combine query parts into a full query string
		if query_parts:
			self.options['params'] = "&".join(query_parts)

		return self

	def set_method(self, method: str):
		self.http_method = method
		return self

	def method(self, method: str):
		return self.set_method(method)

	def get(self, endpoint=None):
		if endpoint:
			self.set_endpoint(endpoint)
		self.set_method(self.GET)
		return self.send()

	def post(self):
		self.set_method(self.POST)
		return self.send()

	def put(self):
		self.set_method(self.PUT)
		return self.send()

	def patch(self):
		self.set_method(self.PATCH)
		return self.send()

	def delete(self):
		self.set_method(self.DELETE)
		return self.send()

	def send(self, reset=True):
		if not self.endpoint:
			raise ValueError("Endpoint must be set before sending a request.")

		self.build_request_json().build_request_query()
		response = self.request.make_request(self.http_method, self.endpoint, self.options, self.response_as_json)
		response = Response(response, self.page_key)
		if reset:
			self.reset()

		return response

	def paginate(self, page_size=100):
		if not self.paginator:
			from .paginator import Paginator
			self.paginator = Paginator(self, page_size)
		results = self.paginator.next_page()
		if not results:
			return self.reset()
		# Assuming response.data is iterable
		return results.data  # Ensure this returns an iterable

	def get_token(self):
		return self.request.token
