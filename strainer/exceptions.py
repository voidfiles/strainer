
class ValidationException(Exception):
    def __init__(self, errors):
        super(ValidationException, self).__init__()
        self.errors = errors
