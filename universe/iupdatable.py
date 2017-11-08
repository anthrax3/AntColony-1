from abc import abstractmethod, ABCMeta


class IUpdatable(metaclass=ABCMeta):
    @abstractmethod
    def update(self, ms_elapsed, local_context):
        pass
