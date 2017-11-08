from abc import abstractmethod, ABCMeta


class ISensable(metaclass=ABCMeta):
    @abstractmethod
    def get_intensity(self):
        pass
