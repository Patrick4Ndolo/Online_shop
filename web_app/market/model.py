from datetime import datetime
import json
import base64
import requests
from requests import auth
from requests import api
from requests.models import Response
from flask_restful import Api, Resource, reqparse
from requests.auth import HTTPBasicAuth
from market import db, login_manager
from market import bcrypt
from flask_login import UserMixin
from wtforms.validators import DataRequired


# login manager decorator to authenticate users
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


"""constructing class user to add users' details to the database"""


class User(db.Model, UserMixin, HTTPBasicAuth):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(length=30), nullable=False, unique=True)
    email_address = db.Column(db.String(length=50), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=60), nullable=False)
    budget = db.Column(db.Integer(), nullable=False, default=2000)
    items = db.relationship("Item", backref="owned_user", lazy=True)

    # decorator to split numerical values
    @property
    def prettier_budget(self):
        if len(str(self.budget)) >= 4:
            return f"{str(self.budget)[:-3]}, {str(self.budget)[-3:]}$"
        else:
            return f"{str(self.budget)}'$'"

    @property
    def password(self):
        return self.password

    # decorator to hash users' passwords in the database for security concerns
    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode(
            "utf-8"
        )

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)

    # logic to chech if the user has sufficient fund to purchase an item
    def can_purchase(self, item_obj):
        return self.budget >= item_obj.price

    # method to enable item owner can sell back an item to the shop
    def can_sell(self, item_obj):
        return item_obj in self.items

    @property
    def get_mpesa_token():
        consumer_key = "YOUR_APP_CONSUMER"
        consumer_secret = "YOUR_APP_CONSUMER_SECRET"
        api_URL = "https.get://sandbox.safaricom.co.ke/oaath/v1/generate?grant_type=client_credentials"
        r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))

        def __repr__(self):
            return r.json()["access_token"]


"""constructing class item to add product and its featutes to the database"""


class Item(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=30), nullable=False, unique=True)
    price = db.Column(db.Integer(), nullable=False)
    description = db.Column(db.String(length=1024), nullable=False, unique=True)
    owner = db.Column(db.Integer(), db.ForeignKey("user.id"))

    def __repr__(self):
        return self.name

    # method to deduct price of purchased item from the user account
    def buy(self, user):
        self.owner = user.id
        user.budget -= self.price
        db.session.commit()

    # method to add back fund to user's account after selling back an item
    def sell(self, user):
        self.owner = None
        user.budget += self.price
        db.session.commit()


class MakeSTKpush(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument(
        "phone", DataRequired(), type=str, help="This field is required"
    )
    parser.add_argument(
        "amount", DataRequired(), type=str, help="This field is required"
    )

    def post(self):
        """make and stk push to daraja API"""
        encode_data = b"<Business_shortcode><online_passkey><current timestamp>"
        passkey = base64.b64encode(encode_data)

        try:
            access_token = get_mpesa_token()
            api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
            headers = {
                "Authorization": "Bearer" + {access_token},
                "Content-Type": "application/json",
            }
            data = MakeSTKpush.parser.parse_args()
            request = {
                "BusinessShortCode": "555211",
                "Password": str(passkey)[2:-1],
                "Timestamp": "20210612504545",
                "TransactionType": "CustomerPayBillOnline",
                "Amount": data["amount"],
                "PartyA": data["phone"],
                "PartyB": "<business_shortCode>",
                "PhoneNumber": data["phone"],
                "CallBackUrl": "<YOUR_CALLBACK_URL>",
                "AccountReference": "UNIQUE_REFERENCE",
                "TransactionDesc": "",
            }
            response = requests.post(api_url, json=request, headers=headers)
            if response.status_code > 299:
                return {
                    "success": False,
                    "message": "Sorry, something went wrong. Please try again later.",
                }, 400
                return {"data": json.loads(response.text)}, 200
        except:
            return {
                "success": False,
                "message": "Sorry, something went wrong. Please try again later.",
            }, 400
