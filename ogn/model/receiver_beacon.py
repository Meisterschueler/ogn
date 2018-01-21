from sqlalchemy import Column, Float, String, Integer, SmallInteger, ForeignKey, Index
from sqlalchemy.orm import relationship

from .beacon import Beacon


class ReceiverBeacon(Beacon):
    __tablename__ = "receiver_beacons"

    # ReceiverBeacon specific data
    version = Column(String)
    platform = Column(String)
    cpu_load = Column(Float(precision=2))
    free_ram = Column(Float(precision=2))
    total_ram = Column(Float(precision=2))
    ntp_error = Column(Float(precision=2))
    rt_crystal_correction = Column(Float(precision=2))
    voltage = Column(Float(precision=2))
    amperage = Column(Float(precision=2))
    cpu_temp = Column(Float(precision=2))
    senders_visible = Column(Integer)
    senders_total = Column(Integer)
    rec_crystal_correction = 0       # obsolete since 0.2.0
    rec_crystal_correction_fine = 0  # obsolete since 0.2.0
    rec_input_noise = Column(Float(precision=2))
    senders_signal = Column(Float(precision=2))
    senders_messages = Column(Integer)
    good_senders_signal = Column(Float(precision=2))
    good_senders = Column(Integer)
    good_and_bad_senders = Column(Integer)

    user_comment = None

    # Relations
    receiver_id = Column(Integer, ForeignKey('receivers.id', ondelete='SET NULL'))
    receiver = relationship('Receiver', foreign_keys=[receiver_id], backref='receiver_beacons')

    # Multi-column indices
    Index('ix_receiver_beacons_receiver_id_name', 'receiver_id', 'name')

    def __repr__(self):
        return "<ReceiverBeacon %s: %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s>" % (
            self.version,
            self.platform,
            self.cpu_load,
            self.free_ram,
            self.total_ram,
            self.ntp_error,
            self.rt_crystal_correction,
            self.voltage,
            self.amperage,
            self.cpu_temp,
            self.senders_visible,
            self.senders_total,
            # self.rec_crystal_correction,
            # self.rec_crystal_correction_fine,
            self.rec_input_noise,
            self.senders_signal,
            self.senders_messages,
            self.good_senders_signal,
            self.good_senders,
            self.good_and_bad_senders)

    @classmethod
    def get_csv_columns(self):
        return['location',
               'altitude',
               'name',
               'receiver_name',
               'dstcall',
               'timestamp',
               'track',
               'ground_speed',

               'version',
               'platform',
               'cpu_load',
               'free_ram',
               'total_ram',
               'ntp_error',
               'rt_crystal_correction',
               'voltage',
               'amperage',
               'cpu_temp',
               'senders_visible',
               'senders_total',
               # 'rec_crystal_correction',
               # 'rec_crystal_correction_fine',
               'rec_input_noise',
               'senders_signal',
               'senders_messages',
               'good_senders_signal',
               'good_senders',
               'good_and_bad_senders']

    def get_csv_values(self):
        return [
            self.location_wkt,
            int(self.altitude) if self.altitude else None,
            self.name,
            self.receiver_name,
            self.dstcall,
            self.timestamp,
            self.track,
            self.ground_speed,

            self.version,
            self.platform,
            self.cpu_load,
            self.free_ram,
            self.total_ram,
            self.ntp_error,
            self.rt_crystal_correction,
            self.voltage,
            self.amperage,
            self.cpu_temp,
            int(self.senders_visible) if self.senders_visible else None,
            int(self.senders_total) if self.senders_visible else None,
            # self.rec_crystal_correction,
            # self.rec_crystal_correction_fine,
            self.rec_input_noise,
            self.senders_signal,
            int(self.senders_messages) if self.senders_messages else None,
            self.good_senders_signal,
            int(self.good_senders) if self.good_senders else None,
            int(self.good_and_bad_senders) if self.good_and_bad_senders else None]
