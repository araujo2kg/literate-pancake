from math import ceil

class Pagination:
    def __init__(self, total_items, page=1, per_page=5):
        self.page = page
        self.per_page = per_page
        self.total_items = total_items

    @property
    def total_pages(self):
        return ceil(self.total_items / self.per_page)

    @property
    def offset(self):
        return (self.page - 1) * self.per_page