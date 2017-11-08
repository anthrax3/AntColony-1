from lib.rlocation import RadialLocation


class SensableRegion:
    def __init__(self):
        self.objects_and_radial_locations = {}

    def add_object(self, world_object, angle_rad, distance):
        self.objects_and_radial_locations[world_object] = RadialLocation(angle_rad, distance)
