import json


class AbstractWriter:
    """Esta clase abstracta contiene la definición e interfaz de funciones para todos los tipos de `writer` que
    se usan en el programa para volcar la información al soporte de salida que se haya configurado al programa.

    ...
    Methods
    -------
    finish()
        función encargada de cerrar la conexión con la base de datos y de finalizar cualquier conexión que haya abierta
        con el soporte de salida. A implementar por las clases hijas.
    auto_boot()
        función encargada de abrir la conexión con el soporte de salida configurado para la ejecución del programa.
        A implementar por las clases hijas.
    write()
        función encargada de realizar la escritura del soporte de entrada configurada para la ejecución del programa. A
        implementar por las clases hijas.
    is_registered(name, date)
        función auxiliar que checkea si la instancia está ya registrado en el soporte de salida para evitar volver a
        procesarlo o escribirlo en la bbdd. A implementar por las clases hijas.
    """

    def __init__(self, name=None):
        self._name = name if name else self.__class__.__name__

    def finish(self):
        raise NotImplementedError("Method must be implemented in subclass")

    def auto_boot(self):
        raise NotImplementedError("Method must be implemented in subclass")

    def is_registered(self, data):
        raise NotImplementedError("Method must be implemented in subclass")

    def write(self, element, is_update=False):
        raise NotImplementedError("Method must be implemented in subclass")


class DbWriter(AbstractWriter):
    """Esta clase abstracta extiende de `AbstractReader` y contiene la definición e interfaz de funciones para todos
    los `writer` que se tengan que conectar a una base de datos.

    ...
    Attributes
    ----------
    db_user : str
        nombre que se usará para conectarse con la base de datos
    db_pass : str
        contraseña del usuario con el que se conectará con la base de datos
    """

    def __init__(self, db_user, db_pass):
        super().__init__(name=self.__class__.__name__)
        self.db_user = db_user
        self.db_pass = db_pass

    def finish(self):
        raise NotImplementedError("Method must be implemented in subclass")

    def auto_boot(self):
        raise NotImplementedError("Method must be implemented in subclass")

    def write(self, element, is_update=False):
        raise NotImplementedError("Method must be implemented in subclass")

    def is_registered(self, data):
        raise NotImplementedError("Method must be implemented in subclass")


class FileWriter(AbstractWriter):
    """Esta clase abstracta extiende de `AbstractReader` y contiene la definición e interfaz de funciones para todos
    los `writer` que usen como soporte de salida ficheros.

    ...
    Attributes
    ----------
    _root_path : str
        directorio que se usará para almacenar los resultados
    """

    def __init__(self, root_path):
        super().__init__(name=self.__class__.__name__)
        self._root_path = root_path

    def finish(self):
        raise NotImplementedError("Method must be implemented in subclass")

    def auto_boot(self):
        raise NotImplementedError("Method must be implemented in subclass")

    def write(self, element, is_update=False):
        raise NotImplementedError("Method must be implemented in subclass")

    def is_registered(self, data):
        raise NotImplementedError("Method must be implemented in subclass")


class PrinterWriter(AbstractWriter):

    def finish(self):
        pass

    def auto_boot(self):
        pass

    def is_registered(self, data):
        return False

    def write(self, element, is_update=False):
        print(json.dumps(element))
        return element
