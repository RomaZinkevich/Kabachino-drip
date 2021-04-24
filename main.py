from flask import Flask, render_template, redirect, url_for, request
from flask_wtf import FlaskForm
from flask_login import LoginManager, login_required, logout_user, current_user, login_user
from wtforms import StringField, PasswordField, BooleanField, SubmitField, validators
from wtforms.validators import DataRequired
import sys
import json
import random
from data import db_session, clothes_db, user
from passlib.hash import sha256_crypt


app = Flask(__name__)
app.config['SECRET_KEY'] = 'hgowoeqeghsdlgh'

login_manager = LoginManager()
login_manager.init_app(app)


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Пароли должны совпадать')
    ])
    confirm = PasswordField('Повторите пароль')
    submit = SubmitField('Зарегистрироваться')


@app.route("/")
def main_page():  # Главная страница сайта
    return render_template('main.html', title='KABACHINO-DRIP')


@app.route("/<string:sex>")
def gender(sex):  # Страница отвечающая за выбор пола
    if sex == 'woman' or sex == 'man':
        return render_template('choice.html', title='KABACHINO-DRIP', sex=sex)
    else:
        return "<h1> Ошибка: страница не найдена </h1>"


@app.route("/woman<clothes>")
def woman_clothes(clothes):  # Страница отвечающая за женскую одежду
    datum = ''
    data = []
    like = 'F%'
    db_session.global_init("data.db")
    db_sess = db_session.create_session()
    for i in db_sess.query(clothes_db.Clothes).filter((clothes_db.Clothes.sex.like(like)), (clothes_db.Clothes.type == clothes)):
        datum = (i.name, i.price, i.pic, str(i.id))
        data.append(datum)
    liked = current_user.liked
    return render_template('clothes.html', title='KABACHINO-DRIP', data=data, page=f'woman{clothes}', liked=liked)


@app.route("/man<clothes>")
def man_clothes(clothes):  # Страница отвечающая за мужскую одежду
    datum = ''
    data = []
    like = '%M'
    print(current_user.is_authenticated)
    db_session.global_init("data.db")
    db_sess = db_session.create_session()
    for i in db_sess.query(clothes_db.Clothes).filter((clothes_db.Clothes.sex.like(like)), (clothes_db.Clothes.type == clothes)):
        datum = (i.name, i.price, i.pic, str(i.id))
        data.append(datum)
    if not current_user.is_authenticated:
        liked = None
    else:
        liked = current_user.liked
    return render_template('clothes.html', title='KABACHINO-DRIP', data=data, page=f'man{clothes}', liked=liked)


@app.route("/<int:clothes><prev>")
@login_required
def selected_clothes(clothes, prev):  # Страница отвечающая за мужскую одежду
    datum = ''
    data = []
    db_session.global_init("data.db")
    db_sess = db_session.create_session()
    for i in db_sess.query(clothes_db.Clothes).filter((clothes_db.Clothes.id == clothes)):
        datum = (i.name, i.price, i.av_sizes.split(","), i.pic, i.id)
        data.append(datum)
    like = '♡'
    for i in db_sess.query(user.User).filter(user.User.id == current_user.id):
        if i.liked:
            if str(clothes) in i.liked:
                like = '❤'
    return render_template('selected_clothes.html', title='KABACHINO-DRIP', data=data, like=like, prev=prev)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    if request.method == "POST" and form.validate():
        db_session.global_init("data.db")
        db_sess = db_session.create_session()
        for i in db_sess.query(user.User):
            if form.username.data == i.login and sha256_crypt.verify(str(form.password.data), i.password):
                login_user(i)
                return redirect('')
        return render_template('login.html', title='KABACHINO-DRIP', form=form, error1='Введенный логин или пароль неправильный')
    return render_template('login.html', title='KABACHINO-DRIP', form=form, error1='')


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == "POST" and form.validate():
        db_session.global_init("data.db")
        db_sess = db_session.create_session()
        c = 0
        for i in db_sess.query(user.User):
            c += 1
            if form.username.data == i.login:
                return render_template('reg.html', title='KABACHINO-DRIP', form=form, error1='Введенный логин уже существует')
        user1 = user.User()
        user1.id = c + 1
        user1.login = form.username.data
        user1.password = sha256_crypt.encrypt(str(form.password.data))
        db_sess.add(user1)
        db_sess.commit()
        return redirect('login')
    return render_template('reg.html', title='KABACHINO-DRIP', form=form, error1='')


@app.route("/profile")
@login_required
def profile():
    data = []
    datum = ''
    db_session.global_init("data.db")
    db_sess = db_session.create_session()
    login = current_user.login
    liked = (str(current_user.liked)).split(';')
    if liked != ['None'] and liked != ['']:
        liked = [int(i) for i in liked]
    for i in db_sess.query(clothes_db.Clothes).filter((clothes_db.Clothes.id.in_(liked))):
        datum = (i.name, i.price, i.pic, i.id)
        data.append(datum)
    return render_template('profile.html', title='KABACHINO-DRIP', data=data, login=login, page='profile')


@app.route("/cart")
@login_required
def cart():
    data = []
    datum = ''
    db_session.global_init("data.db")
    db_sess = db_session.create_session()
    login = current_user.login
    carted_start = (str(current_user.carted)).split(';')
    carted = []
    for i in carted_start:
        i = i.split(',')
        carted.append(i)
    for j in carted:
        for i in db_sess.query(clothes_db.Clothes).filter((clothes_db.Clothes.id == int((j[0])))):
            datum = (i.name, i.price, i.pic, i.id, j[1], j[2])
            data.append(datum)
    return render_template('cart.html', title='KABACHINO-DRIP', data=data, login=login, page='cart')


@app.route("/upd<int:clothes><prev>")
@login_required
def upd(clothes, prev):
    db_session.global_init('data.db')
    db_sess = db_session.create_session()
    for i in db_sess.query(user.User).filter(user.User.id == current_user.id):
        if i.liked:
            liked = str(i.liked).split(';')
            if str(clothes) not in liked:
                liked.append(str(clothes))
            else:
                liked.remove(str(clothes))
            liked = ';'.join(liked)
        else:
            liked = str(clothes)
        i.liked = liked
    db_sess.commit()
    return redirect(f'{clothes}{prev}')


@app.route("/plus<clothes><prev>")
@login_required
def plus(clothes, prev):
    db_session.global_init('data.db')
    db_sess = db_session.create_session()
    for i in db_sess.query(user.User).filter(user.User.id == current_user.id):
        if i.liked:
            liked = str(i.liked).split(';')
            if str(clothes) not in liked:
                liked.append(str(clothes))
            else:
                liked.remove(str(clothes))
            liked = ';'.join(liked)
        else:
            liked = str(clothes)
        i.liked = liked
    db_sess.commit()
    return redirect(f'{clothes}{prev}')


@app.route("/logout")
@login_required
def logout():
    """User log-out logic."""
    logout_user()
    return redirect('login')


@login_manager.user_loader
def load_user(user_id):
    if user_id is not None:
        db_session.global_init("data.db")
        db_sess = db_session.create_session()
        for i in db_sess.query(user.User):
            if int(i.id) == int(user_id):
                return i
    return None


@login_manager.unauthorized_handler
def unauthorized():
    """Redirect unauthorized users to Login page."""
    return login()


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1', debug=True)
