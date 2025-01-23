from .request import Request
from .response import Response

class RequestBuilder:
    GET = "get"
    POST = "post"
    PUT = "put"
    PATCH = "patch"
    DELETE = "delete"

    def __init__(self, server_address, client_id, client_secret, cache_key="powerschool_token"):
        # Initialize the Request object
        self.request = Request(server_address, client_id, client_secret, cache_key)

        # Automatically authenticate and set the auth token
        self.request.authenticate()
        self.endpoint = None
        self.method = self.GET
        self.data = {}
        self.query_string = {}
        self.table_name = None
        self.include_projection = False
        self.page_key = "record"
        self.paginator = None

    def set_endpoint(self, endpoint):
        """Sets the API endpoint."""
        self.endpoint = endpoint
        return self

    def set_method(self, method):
        """Sets the HTTP method."""
        self.method = method
        return self

    def set_data(self, data):
        """Sets the request body data."""
        self.data = data
        return self

    def add_query_param(self, key, value):
        """Adds a query parameter to the request."""
        self.query_string[key] = value
        return self

    def has_query_param(self, key):
        """Checks if a query parameter exists."""
        return key in self.query_string

    def with_query_string(self, query):
        """Adds query parameters from a dictionary."""
        self.query_string.update(query)
        return self

    def projection(self, projection_fields):
        """Adds projection fields to the request."""
        if isinstance(projection_fields, list):
            projection_fields = ",".join(projection_fields)
        self.add_query_param("projection", projection_fields)
        self.include_projection = True
        return self

    def page_size(self, size):
        """Sets the page size for paginated requests."""
        self.add_query_param("pagesize", size)
        return self

    def set_table(self, table):
        """Sets the table for the request."""
        self.table_name = table
        self.endpoint = f"/ws/schema/table/{table}"
        self.include_projection = True
        return self

    def table(self, table):
        """Alias for set_table."""
        return self.set_table(table)

    def for_table(self, table):
        """Alias for set_table."""
        return self.set_table(table)

    def against_table(self, table):
        """Alias for set_table."""
        return self.set_table(table)

    def set_id(self, resource_id):
        """Sets a specific resource ID for the request."""
        self.endpoint = f"{self.endpoint}/{resource_id}"
        return self

    def set_named_query(self, query_name, data=None):
        """Sets a named query for the request."""
        self.endpoint = f"/ws/schema/query/{query_name}"
        if data:
            self.set_data(data)
            self.set_method(self.POST)
        return self

    def send(self, reset=True):
        """Sends the request to the server."""
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
        """Handles paginated responses."""
        if not self.paginator:
            from .paginator import Paginator
            self.paginator = Paginator(self, page_size)
        return self.paginator.get_next_page()

    def reset(self):
        """Resets the builder state."""
        self.endpoint = None
        self.method = self.GET
        self.data = {}
        self.query_string = {}
        self.table_name = None
        self.include_projection = False
        self.page_key = "record"
        self.paginator = None

    def get(self, endpoint=None):
        """Shortcut for sending GET requests."""
        if endpoint:
            self.set_endpoint(endpoint)
        self.set_method(self.GET)
        return self.send()

    def post(self):
        """Shortcut for sending POST requests."""
        self.set_method(self.POST)
        return self.send()

    def put(self):
        """Shortcut for sending PUT requests."""
        self.set_method(self.PUT)
        return self.send()

    def patch(self):
        """Shortcut for sending PATCH requests."""
        self.set_method(self.PATCH)
        return self.send()

    def delete(self):
        """Shortcut for sending DELETE requests."""
        self.set_method(self.DELETE)
        return self.send()

    def get_token(self):
        """Retrieve the cached token if available."""
        return self.request.auth_token