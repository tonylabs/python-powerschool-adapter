import base64
import requests
from cachetools import TTLCache
from cachetools import cached


class Request:

	def __init__(self, server_address, client_id, client_secret, cache_key=None, cache_ttl=3600):
		"""
		Initializes a new Request object to interact with PowerSchool's API.

		:param server_address: The URL of the server
		:param client_id: The client ID obtained from installing a plugin with OAuth enabled
		:param client_secret: The client secret obtained from installing a plugin with OAuth enabled
		:param cache_key: The key for the cache (used for auth token caching)
		:param cache_ttl: Time-to-live for the cache in seconds (default: 3600)
		"""
		self.server_address = server_address
		self.client_id = client_id
		self.client_secret = client_secret
		self.cache_key = cache_key
		self.cache = TTLCache(maxsize=100, ttl=cache_ttl) if cache_key else None
		self.token = self._get_cached_token() if cache_key else None
		self.client = requests.Session()
		self.attempts = 0


	def _get_cached_token(self):
		cached_token = self.cache.get(self.cache_key, None) if self.cache else None
		print(f"Cache key: {self.cache_key}, Cached token retrieved: {cached_token}")
		return cached_token


	def _cache_token(self, token, ttl):
		if self.cache:
			print(f"Caching token: {token} with key: {self.cache_key}, TTL: {ttl}")
			self.cache = TTLCache(maxsize=100, ttl=ttl)  # Reinitialize with dynamic TTL if needed
			self.cache[self.cache_key] = token


	def inspect_cache(self):
		if self.cache:
			print(f"Current cache state: {dict(self.cache)}")
		else:
			print("Cache is not initialized.")


	def make_request(self, method, endpoint, options=None, return_response=False):
		if not self.token:
			print("Token not found. Authenticating...")
			self.authenticate()

		self.attempts += 1

		if options is None:
			options = {}

		headers = options.get("headers", {})
		headers.update({
			"Accept": "application/json",
			"Content-Type": "application/json",
			"Authorization": f"Bearer {self.token}"
		})
		options["headers"] = headers

		url = f"{self.server_address}{endpoint}"
		response = self.client.request(method, url, **options)

		try:
			response.raise_for_status()
		except requests.exceptions.HTTPError as e:
			if response.status_code == 401 and self.attempts < 3:
				# Reauthenticate and retry the request
				self.authenticate(force=True)
				return self.make_request(method, endpoint, options, return_response)
			raise e

		self.attempts = 0
		body = response.json()

		return response if return_response else body


	def authenticate(self, force=False):
		"""
		Authenticates against the API and retrieves an auth token.
		:param force: Force authentication even if there is an existing token
		"""
		if not force and self.token:
			return

		if not self.client_id or not self.client_secret:
			raise ValueError("Missing either client ID or secret. Cannot authenticate with PowerSchool API.")

		token = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()

		headers = {
			"Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
			"Authorization": f"Basic {token}"
		}
		response = self.client.post(f"{self.server_address}/oauth/access_token",
									data={"grant_type": "client_credentials"}, headers=headers)
		response.raise_for_status()

		json_response = response.json()

		self.token = json_response["access_token"]
		ttl = int(json_response["expires_in"])

		if self.cache_key:
			print(f"Preparing to Cache the Token: {self.token} with TTL: {ttl}")
			self._cache_token(self.token, ttl)


	def get_client(self):
		return self.client
