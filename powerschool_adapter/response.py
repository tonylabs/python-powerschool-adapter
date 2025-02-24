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

	def __init__(self, data, key: str = "record"):
		# Data Example:
		"""
		{'name': 'Students', 'record': [{'id': 1, 'tables': {'students': {'dcid': '1', 'student_number': '10006', 'id': '1', 'first_name': 'Tony'}}}]}
		"""
		self.data = self.infer_data(data, key.lower()) if isinstance(data, dict) else data
		self.table_name = data["name"].lower() if isinstance(data, dict) and "name" in data else None
		self.original_data = data
		self.expansions: Optional[List[str]] = None
		self.extensions: Optional[List[str]] = None
		self.meta: Dict[str, Any] = {}
		self.index = 0
		self.is_single_item = isinstance(key, int) and len(data) == 1
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

	def set_data(self, data: Dict[str, Any]):
		self.data = data
		return self

	def get_original_data(self) -> Dict[str, Any]:
		return self.original_data

	def clean_property(self, property_name: str) -> str:
		return re.sub(r"[^a-zA-Z0-9_]", '', property_name)

	def set_meta(self, data: Dict[str, Any], property_name: str):
		property = self.clean_property(property_name)
		value = data.get(property_name)
		if property in ["extensions", "expansions"]:
			setattr(self, property, self.split_comma_string(value))
		else:
			self.meta[property] = value

	def get_meta(self):
		return self.meta

	def squash_table_response(self):
		if not self.table_name:
			return self
		is_assoc = isinstance(self.data, dict)
		if is_assoc:
			self.data = [self.data]
		self.data = [
			datum["tables"][self.table_name] for datum in self.data if "tables" in datum
		]
		if is_assoc:
			self.data = self.data[0] if self.data else None
		return self

	def split_comma_string(self, string: Optional[str]) -> List[str]:
		if not string:
			return []
		parts = string.split(',')
		return [s.strip() for s in parts]

	def is_empty(self) -> bool:
		return not bool(self.data)

	def count(self) -> int:
		return len(self.data) if isinstance(self.data, list) else 1

	def current(self) -> Any:
		if isinstance(self.data, list):
			return self.data[self.index] if self.index < len(self.data) else None
		return self.data

	def next(self):
		self.index += 1

	def key(self):
		return self.index

	def to_list(self) -> List[Dict[str, Any]]:
		return self.data if isinstance(self.data, list) else [self.data]

	def to_dict(self) -> Dict[str, Any]:
		if isinstance(self.data, dict):
			return self.data  # Already a dictionary, return as is

		if isinstance(self.data, list):
			# Convert the list to a dictionary using 'id' as the key if available
			try:
				return {str(item["id"]): item for item in self.data if "id" in item}
			except TypeError:
				# If items are not dicts, just enumerate them
				return {str(index): item for index, item in enumerate(self.data)}

		return {}  # If self.data is not a list or dict, return an empty dict

	def to_json(self) -> str:
		return json.dumps(self.data)

	def rewind(self) -> None:
		self.index = 0
