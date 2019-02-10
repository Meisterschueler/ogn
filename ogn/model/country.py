from geoalchemy2.types import Geometry
from sqlalchemy import Column, String, Integer, Float, SmallInteger, BigInteger

from ogn import db


class Country(db.Model):
    __tablename__ = "countries"

    gid = Column(Integer, primary_key=True)

    fips = Column(String(2))
    iso2 = Column(String(2))
    iso3 = Column(String(3))

    un = Column(SmallInteger)
    name = Column(String(50))
    area = Column(Integer)
    pop2005 = Column(BigInteger)
    region = Column(SmallInteger)
    subregion = Column(SmallInteger)
    lon = Column(Float)
    lat = Column(Float)

    geom = Column('geom', Geometry('MULTIPOLYGON', srid=4326))

    def __repr__(self):
        return "<Country %s: %s,%s,%s,%s,%s,%s,%s,%s,%s,%s>" % (
            self.fips,
            self.iso2,
            self.iso3,
            self.un,
            self.name,
            self.area,
            self.pop2005,
            self.region,
            self.subregion,
            self.lon,
            self.lat)
