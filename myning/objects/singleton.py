class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

    @property
    def _instance(cls):
        return cls._instances[cls]

    @_instance.setter
    def _instance(cls, instance):
        cls._instances[cls] = instance

    @classmethod
    def reset(cls):
        cls._instances = {}
