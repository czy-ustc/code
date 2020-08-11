from .file import file


class txtFile(file):
    _type = "txt"

    def __init__(self, name=None):
        super().__init__(name=name)

    def __call__(self, name=None):
        return txtFile(name)
