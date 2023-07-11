from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from market.model import User

"""Creating class for user registration"""


class RegisterForm(FlaskForm):
    def validate_username(self, username_to_check):
        user = User.query.filter_by(username=username_to_check.data).first()
        if user:
            raise ValidationError(
                "Username already exists! Please try a different usename"
            )

    def validate_email_address(self, email_address_to_check):
        email_address = User.query.filter_by(
            email_address=email_address_to_check.data
        ).first()
        if email_address:
            raise ValidationError(
                "Email address already exists! Please try a different email"
            )

    # Instances for user registration details
    username = StringField(
        label="User Name:", validators=[Length(min=2, max=30), DataRequired()]
    )
    email_address = StringField(
        label="Email Address:", validators=[Email(), DataRequired()]
    )
    password1 = StringField(
        label="Password:", validators=[Length(min=6), DataRequired()]
    )
    password2 = StringField(
        label="Confirm Password:", validators=[EqualTo("password1"), DataRequired()]
    )
    submit = SubmitField(label="Create Account")


"""creating login class to sign in users"""


class LoginForm(FlaskForm):
    # instances for user login detains
    username = StringField(label="User Name:", validators=[DataRequired()])
    password = PasswordField(label="Password:", validators=[DataRequired()])
    remember_me = BooleanField(label="Remember me")
    submit = SubmitField(label="Sign in")


"""Creating class purchase item to enable user to buy items from the shop"""


class PurchaseItemForm(FlaskForm):
    submit = SubmitField(label="Purchase Item!")


"""creating class sell items to enable user to take back items to the counter"""


class SellItemForm(FlaskForm):
    submit = SubmitField(label="Sell Item!")


"""creating classs edit enable user admin of the shop to edit features of items"""


class EditForm(FlaskForm):
    submit = SubmitField(label="Edit Item!")
