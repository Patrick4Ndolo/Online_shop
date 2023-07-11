from market import app
from flask import render_template, redirect, url_for, flash, request
from market.model import Item, User
from market.forms import RegisterForm, LoginForm, PurchaseItemForm, SellItemForm, EditForm
from market import db
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime

@app.route('/')
@app.route('/home')
#Landing page route
def index():
    return render_template('home.html')
#route for market page
@app.route('/market', methods=['GET', 'POST'])
@login_required
def market_page():
    purchase_form = PurchaseItemForm()
    selling_form = SellItemForm()
    edit_form = EditForm()
    if request.method == "POST":
        purchased_item = request.form.get('purchased_item')
        p__item__object = Item.query.filter_by(name=purchased_item).first()
        if p__item__object:
            if current_user.can_purchase(p__item__object):
                p__item__object.buy(current_user)
                flash(f"You have successfully purchased {str(p__item__object.name)} for {str(p__item__object.price)}$", category='success')
            else:
                flash("Dear client, you not have sufficient fund to purchase " + p__item__object.name, category='danger')

    if request.method == "POST":
        edited_item = request.form.get('edited_item')
        i__item__object = Item.query.filter_by(name=edited_item).first()
        if i__item__object:
            if current_user.can_edit(i__item__object):
                i__item__object.edit(current_user)
                flash(f"You have successfully edited {str(i__item__object.name)}", category='success')
        sold_item = request.form.get('sold_item')
        s_item_object = Item.query.filter_by(name=sold_item).first()
        if s_item_object:
            if current_user.can_sell(s_item_object):
                s_item_object.sell(current_user)
                flash("You have successfully sold " + s_item_object.name + " back to the market", category='success')
            else:
                flash("Unfortunately, something went wrong" + s_item_object.name, category='danger')
        
        return redirect(url_for('market_page'))
    if request.method == "GET":
        items = Item.query.filter_by(owner=None)
        owned_items = Item.query.filter_by(owner=current_user.id)
        return render_template('market.html', items=items, purchase_form=purchase_form, owned_items=owned_items, selling_form=selling_form, edit_form=edit_form)

#route to render users registraion form
@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data, email_address=form.email_address.data, password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash('Account Created successfully, thank you! You are now registered as: ' + str(user_to_create.username), category='success')
        return redirect(url_for('login_page'))
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f'There was an error in creating a user: {err_msg}', category='danger')

    return render_template('register.html', form=form)

#route to render users login form
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    """condition to check if user has entered the correct login details"""
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        """this condition check the user input against the details stored in the database. 
        If the details match, the user will be rediredted to the market page. 
        The validation will be okayed by a flash message indicating that the login was successful"""
        if attempted_user and attempted_user.check_password_correction(attempted_password=form.password.data):
            login_user(attempted_user)
            flash('Success! You are logged in sucessfully as: ' + str(attempted_user.username), category='success')
            return redirect(url_for('market_page'))

        else:
            flash('Username and password are not matched! Please try again.', category='danger')



    return render_template('login.html', form=form)

#route to render users logout form
@app.route('/logout')
def logout_page():
    logout_user()
    flash("You have successfully logged out", category='info')
    return redirect(url_for('index'))

@app.route("/insert", methods=['GET', 'POST'])
def insert():
    if request.method == 'POST':
        product_name = request.form['Name']
        product_price= request.form['Price']
        product_barcode = request.form['Barcode']

        data = Item(product_name, product_price, product_barcode)
        db.session.add(data)
        db.session.commit()
        return render_template(url_for('home.html'))