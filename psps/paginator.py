class Paginator:
    def __init__(self, builder, page_size=100):
        self.builder = builder
        self.page_size = page_size
        self.current_page = 1

    def next_page(self):
        """Retrieve the next page of results."""
        self.builder.query_params["page"] = self.current_page
        self.builder.query_params["pagesize"] = self.page_size
        results = self.builder.send()

        if not results or len(results) == 0:
            return None  # No more pages

        self.current_page += 1
        return results