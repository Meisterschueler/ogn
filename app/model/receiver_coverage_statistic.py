from app import db


class ReceiverCoverageStatistic(db.Model):
    __tablename__ = "receiver_coverage_statistics"

    id = db.Column(db.Integer, primary_key=True)

    date = db.Column(db.Date)
    location_mgrs_short = db.Column(db.String(9))
    is_trustworthy = db.Column(db.Boolean)

    messages_count = db.Column(db.Integer)
    max_distance = db.Column(db.Float(precision=2))
    max_normalized_quality = db.Column(db.Float(precision=2))
    max_signal_quality = db.Column(db.Float(precision=2))
    min_altitude = db.Column(db.Float(precision=2))
    max_altitude = db.Column(db.Float(precision=2))
    senders_count = db.Column(db.Integer)

    # Relations
    receiver_id = db.Column(db.Integer, db.ForeignKey("receivers.id", ondelete="CASCADE"), index=True)
    receiver = db.relationship("Receiver", foreign_keys=[receiver_id], backref=db.backref("receiver_coverage_stats", order_by=date))

    __table_args__ = (db.Index('idx_receiver_coverage_statistics_uc', 'date', 'receiver_id', 'location_mgrs_short', 'is_trustworthy', unique=True), )
