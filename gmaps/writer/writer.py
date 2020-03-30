
class DbWriter:

    def __init__(self, db_user, db_pass):
        self.db_user = db_user
        self.db_pass = db_pass

    def finish(self):
        raise NotImplementedError("Method must be implemented in subclass")

    def auto_boot(self):
        raise NotImplementedError("Method must be implemented in subclass")

    def write(self, element):
        raise NotImplementedError("Method must be implemented in subclass")