class Paginator:

    def __init__(self, builder, page_size=100):
        self.builder = builder
        self.page_size = page_size
        self.current_page = 1
        self.has_more = True
        self.builder.page_size(self.page_size)
        self.builder.page(self.current_page)


    def next_page(self):
        if not self.has_more:
            return None

        self.builder.page(self.current_page)
        self.builder.page_size(self.page_size)
        response = self.builder.send(reset=False)
        
        # Check if we have more pages
        results = response.get_data()
        if not results or len(results) == 0:
            self.has_more = False
            return None

        self.current_page += 1
        return results


    def get_next_page(self):
        return self.next_page()


    def has_next(self):
        return self.has_more