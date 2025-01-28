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

import re
import json
from typing import Any, Dict, List, Optional

class Response:

	def __init__(self, data, key: str = "data"):

		self.table_name = data["name"] if isinstance(data, dict) and "name" in data else None
		self.data = self.infer_data(data, key.lower()) if isinstance(data, dict) else data
		self.original_data = data
		self.extensions: Optional[List[str]] = None
		self.expansions: Optional[List[str]] = None
		self.meta: Dict[str, Any] = {}
		self.index = 0
		self.is_single_item = isinstance(key, int) and len(data) == 1

		# Extract metadata, expansions, or extensions if available
		self.meta.update(data.get("@extensions", {}))
		self.meta.update(data.get("@expansions", {}))


	def infer_data(self, data: Dict[str, Any], key: str) -> Dict[str, Any]:
		if not data:
			return {}

		if "results" in data:
			return data["results"]

		# Check if there is nested data
		nested = data.get(f"{key}s")
		if nested:
			return self.infer_data(nested, key)

		keys = list(data.keys())

		# Check if every key is numeric
		if all(k.isdigit() for k in keys):
			return data

		meta_keys = ["@extensions", "@expansions"]
		for meta_key in meta_keys:
			self.set_meta(data, meta_key)
			data.pop(meta_key, None)

		if key in data:
			return data[key]

		# If there's only one key, keep drilling
		if len(keys) == 1:
			first = list(data.values())[0]

			if isinstance(first, dict):  # If this is a dictionary, recurse
				return self.infer_data(first, "")

		return data


	def clean_property(self, property_name: str) -> str:
		return re.sub(r"[^a-zA-Z0-9_]", '', property_name)


	def split_comma_string(self, string: Optional[str]) -> List[str]:
		if not string:
			return []
		parts = string.split(',')
		return [s.strip() for s in parts]


	def get_meta(self):
		return self.meta


	def set_meta(self, data: Dict[str, Any], property_name: str):
		clean = self.clean_property(property_name)
		value = data.get(property_name)

		if clean in ["extensions", "expansions"]:
			setattr(self, clean, self.split_comma_string(value))
		else:
			self.meta[clean] = value


	def is_empty(self) -> bool:
		return not bool(self.data)

	def count(self) -> int:
		return len(self.data) if isinstance(self.data, list) else 1

	def current(self) -> Any:
		if isinstance(self.data, list):
			return self.data[self.index] if self.index < len(self.data) else None
		return self.data

	def to_dict(self) -> Dict[str, Any]:
		return self.data if isinstance(self.data, dict) else {}

	def to_json(self) -> str:
		return json.dumps(self.data)

	def rewind(self) -> None:
		self.index = 0

	def get_original_data(self) -> Dict[str, Any]:
		return self.original_data


	def collect(self) -> List[Dict[str, Any]]:
		return self.data if isinstance(self.data, list) else [self.data]

	def squash_table_response(self):
		if not self.table_name:
			return self

		# Check if self.data is associative (dictionary in Python)
		is_assoc = isinstance(self.data, dict)

		# If it's associative, wrap it in a list
		if is_assoc:
			self.data = [self.data]

		# Map over self.data and extract the required table data
		self.data = [
			datum["tables"][self.table_name] for datum in self.data if "tables" in datum
		]

		# If it was originally associative, take the first element
		if is_assoc:
			self.data = self.data[0] if self.data else None

		return self
