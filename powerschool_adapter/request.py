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

import time
import base64
import requests
from diskcache import Cache


class Request:

	def __init__(self, server_address, client_id, client_secret, cache_key=None):
		self.server_address = server_address
		self.client_id = client_id
		self.client_secret = client_secret
		self.cache_key = cache_key
		self.cache = Cache('.cache') if cache_key else None
		self.token = self._get_cached_token() if cache_key else None
		self.client = requests.Session()
		self.attempts = 0

	def _get_cached_token(self):
		# Fetch the token and its expiration time
		cached_token = self.cache.get(self.cache_key, default=None, expire_time=True)
		if cached_token:
			token, expire_time = cached_token
			if expire_time:
				expiration_time_str = time.strftime('%Y-%m-%d %H:%M', time.localtime(expire_time))
				print(f"The cached token '{token}' will expire at: {expiration_time_str}")
			return token
		print("No token found in cache.")
		return None

	def _cache_token(self, token, ttl):
		self.cache.set(self.cache_key, token, expire=ttl)
		self.cache.close()
		print(f"Token cached successfully with key '{self.cache}' and TTL: {ttl}")

	def make_request(self, method, endpoint, options=None, json=False):
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

		response = self.client.request(method, f"{self.server_address}{endpoint}", **options)

		try:
			response.raise_for_status()
		except requests.exceptions.HTTPError as e:
			if response.status_code == 401 and self.attempts < 3:
				# Reauthenticate and retry the request
				self.authenticate(force=True)
				return self.make_request(method, endpoint, options, json)
			raise e

		self.attempts = 0

		return response.json() if json else response

	def authenticate(self, force=False):
		if not force and self.token:
			return
		if not self.client_id or not self.client_secret:
			raise ValueError("Missing either client ID or secret. Cannot authenticate with PowerSchool API.")
		token = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
		headers = {
			"Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
			"Authorization": f"Basic {token}"
		}
		response = self.client.post(f"{self.server_address}/oauth/access_token", data={"grant_type": "client_credentials"}, headers=headers)
		response.raise_for_status()
		json_response = response.json()
		self.token = json_response["access_token"]
		ttl = int(json_response["expires_in"])
		print(f"Authenticated successfully. Token expires in {ttl} seconds.")
		if self.cache_key:
			self._cache_token(self.token, ttl)

	def get_client(self):
		return self.client
