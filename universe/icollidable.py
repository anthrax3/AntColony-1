from abc import abstractmethod, ABCMeta


class ICollidable(metaclass=ABCMeta):
    @abstractmethod
    def get_collision_radius(self):
        pass
