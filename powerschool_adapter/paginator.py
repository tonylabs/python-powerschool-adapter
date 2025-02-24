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


class Paginator:

	def __init__(self, builder, page_size=100):
		print(f"Paginator builder with page size: {page_size}")
		self.builder = builder
		self.page = 1
		self.has_more = True
		self.builder.page_size(page_size).page(self.page)

	def next_page(self):
		if not self.has_more:
			return None
		response = self.builder.page(self.page).send(reset=False)
		if not response.is_empty():
			self.builder.data = response.data

		if response.is_empty():
			self.page = 1
			self.has_more = False
			return None

		self.page += 1
		return response

	def get_next_page(self):
		return self.next_page()

	def has_next(self):
		return self.has_more
