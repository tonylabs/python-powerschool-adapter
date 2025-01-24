from .request import Request
from .response import Response
from typing import Union

class RequestBuilder:

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"

    def __init__(self, server_address, client_id, client_secret, cache_key="powerschool_token"):
        self.request = Request(server_address, client_id, client_secret, cache_key)
        #self.request.authenticate()
        self.endpoint = None
        self.method = self.GET
        self.options = {}
        self.data = {}
        self.table_name = None
        self.query_string = {}
        self.id = None
        self.include_projection = False
        self.return_as_json = False
        self.page_key = "record"
        self.paginator = None


    def reset(self):
        self.endpoint = None
        self.method = None
        self.data = {}
        self.query_string = {}
        self.table_name = None
        self.include_projection = False
        self.return_as_json = False
        self.page_key = "record"
        self.paginator = None


    def set_table(self, table: str) -> "RequestBuilder":
        self.table_name = table.split('/')[-1]
        self.endpoint = table if table.startswith('/') else f"/ws/schema/table/{table}"
        self.include_projection = True
        self.page_key = 'record'
        return self


    def table(self, table) -> "RequestBuilder":
        return self.set_table(table)


    def for_table(self, table):
        return self.set_table(table)


    def against_table(self, table):
        return self.set_table(table)


    def set_id(self, resource_id: Union[str, int]):
        self.endpoint += f"/{resource_id}"
        self.id = resource_id
        return self


    def id(self, resource_id: Union[str, int]):
        return self.set_id(resource_id)


    def for_id(self, resource_id: Union[str, int]):
        return self.set_id(resource_id)


    def resource(self, endpoint: str, method: str = None, data: dict = None):
        self.endpoint = endpoint
        self.include_projection = False

        if method is not None:
            self.method = method

        if data:
            self.set_data(data)

        # If the method and data are set, automatically send the request
        if self.method is not None and self.data:
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


    def endpoint(self, endpoint: str):
        return self.set_endpoint(endpoint)


    def set_named_query(self, query_name: str, data: dict = None):
        self.endpoint = query_name if query_name.startswith('/') else f"/ws/schema/query/{query_name}"
        self.page_key = 'record'

        # If there's data along with it, it's shorthand for sending the request
        if data:
            return self.set_data(data).post()

        # By default, don't include the projection unless it gets added later explicitly
        self.include_projection = False

        return self.set_method(self.POST)


    def add_query_param(self, key, value):
        self.query_string[key] = value
        return self


    def has_query_param(self, key):
        return key in self.query_string


    def with_query_string(self, query):
        self.query_string.update(query)
        return self


    def set_data(self, data):
        self.data = data
        return self


    def projection(self, projection_fields):
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


    def sort(self, columns, descending=False):
        """
        Sets the sorting columns and direction for the request.

        Args:
            columns (str | list): A single column name or a list of column names to sort by.
            descending (bool): Whether to sort in descending order. Default is False (ascending).

        Returns:
            self: The updated RequestBuilder instance.
        """
        # Handle multiple columns by joining them with commas
        if isinstance(columns, list):
            columns = ",".join(columns)

        # Add sort parameter to the query string
        self.add_query_param("sort", columns)

        # Add descending flag if set to True
        if descending:
            self.add_query_param("sortdescending", "true")
        else:
            self.add_query_param("sortdescending", "false")

        return self


    def order_by(self, field, direction="asc"):
        self.add_query_param("order", f"{field} {direction}")
        return self


    def include_count(self):
        self.add_query_param("count", "true")
        return self


    def data_version(self, version, application_name):
        """
        Sets the data version and application name in the request data.

        Args:
            version (int): The data version.
            application_name (str): The name of the application.

        Returns:
            self: The updated RequestBuilder instance.
        """
        self.add_query_param("$dataversion", version)
        self.add_query_param("$dataversion_applicationname", application_name)
        return self

    def with_data_version(self, version, application_name):
        """
        Alias for the `data_version` method.

        Args:
            version (int): The data version.
            application_name (str): The name of the application.

        Returns:
            self: The updated RequestBuilder instance.
        """
        return self.data_version(version, application_name)


    def extensions(self, extensions):
        """
        Adds `extensions` as a query parameter to the request.
        Handles a single string or a list of extensions.

        Args:
            extensions (str | list): The extension(s) to add.

        Returns:
            self: The updated RequestBuilder instance.
        """
        if isinstance(extensions, list):
            extensions = ",".join(extensions)  # Join list elements into a comma-separated string
        self.add_query_param("extensions", extensions)
        return self


    def with_extensions(self, extensions):
        """
        Alias for the `extensions` method.
        """
        return self.extensions(extensions)


    def with_extension(self, extension):
        """
        Adds a single extension to the request.
        This is useful when adding one extension at a time.

        Args:
            extension (str): The extension to add.

        Returns:
            self: The updated RequestBuilder instance.
        """
        return self.extensions([extension])


    def get_subscription_changes(self, application_name, version):
        """
        Retrieves data subscription changes for a specific application and version.

        Args:
            application_name (str): The name of the application.
            version (int): The version number of the data subscription.

        Returns:
            Response or dict: The response object or raw JSON, depending on the configuration.
        """
        # Set the endpoint for the data subscription changes
        self.set_endpoint(f"/ws/dataversion/{application_name}/{version}")
        self.set_method(self.GET)
        return self.send()


    def count(self):
        self.endpoint += "/count"
        self.include_projection = False
        return self.get()


    def raw(self):
        self.return_as_json = False
        return self


    def as_json_response(self):
        self.return_as_json = True
        return self


    def cast_to_values_string(self, data):
        """
        Recursively casts all values in the data dictionary to strings.
        Handles nested dictionaries and lists.
        """
        if isinstance(data, dict):
            return {key: self.cast_to_values_string(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self.cast_to_values_string(item) for item in data]
        elif isinstance(data, bool):
            return "1" if data else "0"  # Convert boolean to "1"/"0"
        elif data is None:
            return ""  # Convert None to an empty string
        else:
            return str(data)  # Convert everything else to a string


    def build_request_json(self):
        """
        Builds the JSON structure for the request body.
        This handles cases for table-based requests, IDs, and plain data.
        """
        if self.method in [self.GET, self.DELETE]:
            return self  # No JSON body for GET/DELETE requests

        # Prepare JSON options
        json_body = {}

        # Add table-specific data if a table is set
        if self.table_name:
            json_body["tables"] = {self.table_name: self.data}

        # Add ID if set
        if "id" in self.data:
            json_body["id"] = self.data["id"]
            json_body["name"] = self.table_name

        # If there's no table, use the data directly
        if self.data and not self.table_name:
            json_body = self.data

        # Set the JSON options
        self.data = json_body
        return self

    def build_request_query(self):
        """
        Builds the query string for the request.
        Automatically includes `projection=*` for GET requests if not already set.
        """
        if self.method in [self.GET, self.POST]:
            query_parts = []

            # Add existing query string parameters
            for key, value in self.query_string.items():
                query_parts.append(f"{key}={value}")

            # Include `projection=*` if applicable
            if self.include_projection and not self.has_query_param("projection"):
                query_parts.append("projection=*")

            # Combine query parts into a full query string
            if query_parts:
                self.endpoint += f"?{'&'.join(query_parts)}"

        return self


    def set_method(self, method):
        self.method = method
        return self


    def using_method(self, method):
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

        # Build the query string
        if self.query_string:
            query = "&".join([f"{key}={value}" for key, value in self.query_string.items()])
            self.endpoint += f"?{query}"

        # Send the request
        response_data = self.request.make_request(self.method, self.endpoint, {"json": self.data})
        response = Response(response_data)

        if reset:
            self.reset()
        return response


    def paginate(self, page_size=100):
        if not self.paginator:
            from .paginator import Paginator
            self.paginator = Paginator(self, page_size)
        return self.paginator.get_next_page()


    def get_token(self):
        return self.request.token