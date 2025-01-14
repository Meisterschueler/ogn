from app import db


class SenderStatistic(db.Model):
    __tablename__ = "sender_statistics"

    id = db.Column(db.Integer, primary_key=True)

    date = db.Column(db.Date)
    is_trustworthy = db.Column(db.Boolean)

    max_distance = db.Column(db.Float(precision=2))
    max_normalized_quality = db.Column(db.Float(precision=2))
    messages_count = db.Column(db.Integer)
    coverages_count = db.Column(db.Integer)
    receivers_count = db.Column(db.Integer)

    # Relations
    sender_id = db.Column(db.Integer, db.ForeignKey("senders.id", ondelete="CASCADE"), index=True)
    sender = db.relationship("Sender", foreign_keys=[sender_id], backref=db.backref("statistics", order_by=date.desc()))

    __table_args__ = (db.Index('idx_sender_statistics_uc', 'date', 'sender_id', 'is_trustworthy', unique=True), )
