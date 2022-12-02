# ---------------------------------------------Import Modules----------------------------------------------------------#
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField, FloatField, IntegerField
from wtforms.validators import DataRequired, Length, Email


# ----------------------------------------------------Create Forms-----------------------------------------------------#
# Register Form for new users
class RegisterForm(FlaskForm):
	email = EmailField(
		label="Email",
		validators=[
			DataRequired(
				message="Invalid Email Address"
			),
			Length(
				min=6,
				message="Email to short. Try again."
			),
			Email(
				message="Invalid Email Address. Try again."
			)
		]
	)
	password = PasswordField(
		label="Password",
		validators=[
			DataRequired(
				message="Invalid password. Try again."
			),
			Length(
				min=8,
				message="Password must be 8 characters minimum. Try again."
			)
		]
	)
	name = StringField(
		label="Name",
		validators=[
			DataRequired(
				message="Need to provide a valid name.")
		]
	)
	submit = SubmitField(
		label="Register"
	)


class LoginForm(FlaskForm):
	email = EmailField(
		label="Email",
		validators=[
			DataRequired(
				message="Invalid Email Address"
			),
			Email(
				message="Invalid Email Address. Try again."
			)
		]
	)
	password = PasswordField(
		label="Password",
		validators=[
			DataRequired(
				message="Invalid password. Try again."
			)
		]
	)
	submit = SubmitField(
		label="Login"
	)


class AddProductForm(FlaskForm):
	product_id = StringField(
		label="Product ID",
		validators=[
			DataRequired(
				message="Need to provide a Product ID."
			)
		]
	)
	product_name = StringField(
		label="Product Name",
		validators=[
			DataRequired(
				message="Need to provide a Product Name."
			)
		]
	)
	product_price = FloatField(
		label="Product Price",
		validators=[
			DataRequired(
				message="Need to provide a Product Price."
			)
		]
	)
	wholesale_price = FloatField(
		label="Wholesale Price",
		validators=[
			DataRequired(
				message="Need to provide a Wholesale Price."
			)
		]
	)
	quantity = IntegerField(
		label="Quantity",
		validators=[
			DataRequired(
				message="Need to provide a Quantity."
			)
		]
	)
	img_url = StringField(
		label="Image URL",
		validators=[
			DataRequired(
				message="Need to provide an Image URL."
			)
		]
	)
	description = StringField(
		label="Product Description",
		validators=[
			DataRequired(
				message="Need to provide a Product Description."
			)
		]
	)
	submit = SubmitField(
		label="Submit Product"
	)