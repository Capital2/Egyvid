class ScrapeError(Exception):
    pass


class EgybestApiNotResponding(Exception):
    """Raised when the Egybest Api won't return the Vidstreal Url"""
    def __init__(self, url):
        self.url = url
        self.message = "the returned url"
        super(EgybestApiNotResponding, self).__init__(self.message)

    def __str__(self):
        return f"{self.message} -> {self.url}"
    pass
