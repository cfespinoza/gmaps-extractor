class AbstractReader:

    def __init__(self, name=None):
        self._name = name if name else self.__class__.__name__

    def finish(self):
        raise NotImplementedError("Method must be implemented in subclass")

    def auto_boot(self):
        raise NotImplementedError("Method must be implemented in subclass")

    def read(self):
        raise NotImplementedError("Method must be implemented in subclass")


class DbReader(AbstractReader):

    def __init__(self, db_user, db_pass, name=None):
        super().__init__(name=name if name else self.__class__.__name__)
        self.db_user = db_user
        self.db_pass = db_pass

    def finish(self):
        raise NotImplementedError("Method must be implemented in subclass")

    def auto_boot(self):
        raise NotImplementedError("Method must be implemented in subclass")

    def read(self):
        raise NotImplementedError("Method must be implemented in subclass")
