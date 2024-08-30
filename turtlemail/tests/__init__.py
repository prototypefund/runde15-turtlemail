import enum
from django.contrib.gis.geos import Point


class TestLocations(enum.Enum):
    HAMBURG = Point(9.58292, 53.33145)
    BERLIN = Point(13.431700, 52.592879)
    MUNICH = Point(11.33371, 48.08565)
    BREMEN = Point(53.04052, 8.56428)
