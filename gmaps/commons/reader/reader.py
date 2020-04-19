class AbstractReader:
    """
    Esta clase abstracta contiene la definición e interfaz de funciones para todos los tipos de `reader` que
    se usan en el programa para obtener la información del soporte de entrada que se haya configurado al programa.

    ...
    Methods
    -------
    finish()
        función encargada de cerrar la conexión con la base de datos y de finalizar cualquier conexión que haya abierta
        con el soporte de entrada. A implementar por las clases hijas.
    auto_boot()
        función encargada de arrancar y configurar la conexión con el soporte de entrada configurado para la ejecución
        del programa. A implementar por las clases hijas.
    read()
        función encargada de realizar la lectura del soporte de entrada configurada para la ejecución del programa. A
        implementar por las clases hijas.
    """

    def __init__(self, name=None):
        self._name = name if name else self.__class__.__name__

    def finish(self):
        raise NotImplementedError("Method must be implemented in subclass")

    def auto_boot(self):
        raise NotImplementedError("Method must be implemented in subclass")

    def read(self):
        raise NotImplementedError("Method must be implemented in subclass")


class DbReader(AbstractReader):
    """Esta clase abstracta extiende de `AbstractReader` y contiene la definición e interfaz de funciones para todos
    los `reader` que se tengan que conectar a una base de datos.

    ...
    Attributes
    ----------
    db_user : str
        nombre que se usará para conectarse con la base de datos
    db_pass : str
        contraseña del usuario con el que se conectará con la base de datos
    """

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
