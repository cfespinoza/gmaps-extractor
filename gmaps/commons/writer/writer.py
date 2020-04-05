class AbstractWriter:

    def __init__(self, name=None):
        self._name = name if name else self.__class__.__name__

    def finish(self):
        raise NotImplementedError("Method must be implemented in subclass")

    def auto_boot(self):
        raise NotImplementedError("Method must be implemented in subclass")

    def write(self, element):
        raise NotImplementedError("Method must be implemented in subclass")


class DbWriter(AbstractWriter):

    def __init__(self, db_user, db_pass):
        super().__init__(name=self.__class__.__name__)
        self.db_user = db_user
        self.db_pass = db_pass

    def finish(self):
        raise NotImplementedError("Method must be implemented in subclass")

    def auto_boot(self):
        raise NotImplementedError("Method must be implemented in subclass")

    def write(self, element):
        raise NotImplementedError("Method must be implemented in subclass")


class FileWriter(AbstractWriter):

    def __init__(self, root_path):
        super().__init__(name=self.__class__.__name__)
        self._root_path = root_path

    def finish(self):
        raise NotImplementedError("Method must be implemented in subclass")

    def auto_boot(self):
        raise NotImplementedError("Method must be implemented in subclass")

    def write(self, element):
        raise NotImplementedError("Method must be implemented in subclass")