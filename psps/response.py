import json
from collections.abc import Iterator, MutableMapping
from typing import Any, List, Dict, Union

class Response(Iterator, MutableMapping):

    def __init__(self, data: Dict[str, Any], key: str = ""):

        self.data = data.get(key, data) if isinstance(data, dict) else data
        self.original_data = data
        self.meta = {}
        self.index = 0

        # Extract metadata, expansions, or extensions if available
        self.meta.update(data.get("@extensions", {}))
        self.meta.update(data.get("@expansions", {}))

    def is_empty(self) -> bool:
        """
        Checks if the response data is empty.
        """
        return not bool(self.data)

    def count(self) -> int:
        """
        Returns the count of items in the data.
        """
        return len(self.data) if isinstance(self.data, list) else 1

    def current(self) -> Any:
        """
        Returns the current element for iteration.
        """
        if isinstance(self.data, list):
            return self.data[self.index] if self.index < len(self.data) else None
        return self.data

    def to_dict(self) -> Dict[str, Any]:
        return self.data if isinstance(self.data, dict) else {}


    def to_json(self) -> str:
        return json.dumps(self.data)


    def rewind(self) -> None:
        """
        Resets the iterator to the beginning.
        """
        self.index = 0

    def __iter__(self) -> Iterator:
        """
        Returns the iterator object.
        """
        return iter(self.data) if isinstance(self.data, list) else iter([self.data])

    def __next__(self) -> Any:
        """
        Iterates over the response data.
        """
        if isinstance(self.data, list):
            if self.index < len(self.data):
                result = self.data[self.index]
                self.index += 1
                return result
            else:
                raise StopIteration
        else:
            if self.index == 0:
                self.index += 1
                return self.data
            else:
                raise StopIteration

    def __getitem__(self, key: str) -> Any:
        """
        Allows dictionary-like access to the response data.
        """
        if isinstance(self.data, dict):
            return self.data.get(key)
        raise TypeError("Response data is not a dictionary.")

    def __setitem__(self, key: str, value: Any) -> None:
        """
        Allows setting values like a dictionary.
        """
        if isinstance(self.data, dict):
            self.data[key] = value
        else:
            raise TypeError("Response data is not a dictionary.")

    def __delitem__(self, key: str) -> None:
        """
        Allows deleting keys like a dictionary.
        """
        if isinstance(self.data, dict):
            del self.data[key]
        else:
            raise TypeError("Response data is not a dictionary.")

    def __contains__(self, key: str) -> bool:
        """
        Checks if a key exists in the data.
        """
        if isinstance(self.data, dict):
            return key in self.data
        return False

    def __len__(self) -> int:
        """
        Returns the length of the data.
        """
        return len(self.data) if isinstance(self.data, list) else 1

    def __repr__(self) -> str:
        """
        Returns a string representation of the Response object.
        """
        return f"<Response data={self.data}>"

    def get_original_data(self) -> Dict[str, Any]:
        """
        Returns the original unprocessed data.
        """
        return self.original_data

    def get_meta(self) -> Dict[str, Any]:
        """
        Returns metadata associated with the response.
        """
        return self.meta

    def collect(self) -> List[Dict[str, Any]]:
        """
        Returns the data as a collection (list of dictionaries).
        """
        return self.data if isinstance(self.data, list) else [self.data]

    def squash_table_response(self, table_name: str) -> "Response":
        """
        Squashes table-specific responses into a simpler format.
        """
        if isinstance(self.data, list) and all("tables" in item for item in self.data):
            self.data = [item["tables"].get(table_name, item) for item in self.data]
        elif isinstance(self.data, dict) and "tables" in self.data:
            self.data = self.data["tables"].get(table_name, self.data)
        return self