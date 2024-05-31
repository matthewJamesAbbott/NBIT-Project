from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

# Receipt is the database for the application it stores the details that have been taken from OCR
class Receipt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(100))
    item_name = db.Column(db.String(10000))
    price = db.Column(db.String(100))
    receipt_number = db.Column(db.String(100))
    quantity = db.Column(db.String(100))
    merchant_name = db.Column(db.String(10000))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    file_name = db.Column(db.String(10000))

# User is the database for authentication and user management.
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    receipts = db.relationship('Receipt') # link to application database so receipts can be tied to users
