from app import db

class Seat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    seat_number = db.Column(db.String(10), unique=True, nullable=False)
    is_taken = db.Column(db.Boolean, default=False)
    taken_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
