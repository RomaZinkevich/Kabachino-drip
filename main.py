from flask import Flask, render_template, redirect, url_for, request
from flask_wtf import FlaskForm
from flask_login import LoginManager, login_required, logout_user, current_user, login_user
from wtforms import StringField, PasswordField, BooleanField, SubmitField, validators
from wtforms.validators import DataRequired
import sys
import json
import random
import sqlite3
from data import db_session, clothes_db, user

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
    return render_template('main.html', title='PANOS')


@app.route("/<string:sex>")
def gender(sex):  # Страница отвечающая за выбор пола
    if sex == 'woman' or sex == 'man':
        return render_template('choice.html', title='PANOS', sex=sex)
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
        datum = (i.name, i.price, i.pic, i.id)
        data.append(datum)
    return render_template('clothes.html', title='PANOS', data=data)


@app.route("/man<clothes>")
def man_clothes(clothes):  # Страница отвечающая за мужскую одежду
    datum = ''
    data = []
    like = '%M'
    db_session.global_init("data.db")
    db_sess = db_session.create_session()
    for i in db_sess.query(clothes_db.Clothes).filter((clothes_db.Clothes.sex.like(like)), (clothes_db.Clothes.type == clothes)):
        datum = (i.name, i.price, i.pic, i.id)
        data.append(datum)
    return render_template('clothes.html', title='PANOS', data=data)


@app.route("/<int:clothes>")
@login_required
def selected_clothes(clothes):  # Страница отвечающая за мужскую одежду
    datum = ''
    data = []
    db_session.global_init("data.db")
    db_sess = db_session.create_session()
    for i in db_sess.query(clothes_db.Clothes).filter((clothes_db.Clothes.id == clothes)):
        datum = (i.name, i.price, i.av_sizes.split(","), i.pic, i.id)
        data.append(datum)
    like = '♡'
    for i in db_sess.query(user.User).filter(user.User.id == current_user.id):
        if str(clothes) in i.liked:
            like = '❤'

    return render_template('selected_clothes.html', title='PANOS', data=data, like=like)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    if request.method == "POST" and form.validate():
        db_session.global_init("data.db")
        db_sess = db_session.create_session()
        for i in db_sess.query(user.User):
            if form.username.data == i.login and form.password.data == i.password:
                login_user(i)
                return main_page()
        print(form.username.data, i.login)
        return render_template('login.html', title='PANOS', form=form, error1='Введенный логин или пароль неправильный')
    return render_template('login.html', title='PANOS', form=form, error1='')


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
                return render_template('reg.html', title='PANOS', form=form, error1='Введенный логин уже существует')
        user1 = user.User()
        user1.id = c + 1
        user1.login = form.username.data
        user1.password = form.password.data
        db_sess.add(user1)
        db_sess.commit()
        return login()
    return render_template('reg.html', title='PANOS', form=form, error1='')


@app.route("/profile")
@login_required
def profile():
    data = []
    datum = ''
    db_session.global_init("data.db")
    db_sess = db_session.create_session()
    login = current_user.login
    liked = (str(current_user.liked)).split(';')
    print(liked)
    if liked != ['None']:
        liked = [int(i) for i in liked]
    for i in db_sess.query(clothes_db.Clothes).filter((clothes_db.Clothes.id.in_(liked))):
        datum = (i.name, i.price, i.pic, i.id)
        data.append(datum)
    return render_template('profile.html', title='PANOS', data=data, login=login)


@app.route("/upd<int:clothes>")
@login_required
def upd(clothes):
    db_session.global_init('data.db')
    db_sess = db_session.create_session()
    for i in db_sess.query(user.User).filter(user.User.id == current_user.id):
        liked = str(i.liked).split(';')
        if str(clothes) not in liked:
            liked.append(str(clothes))
        else:
            liked.remove(str(clothes))
        liked = ';'.join(liked)
        i.liked = liked
    db_sess.commit()
    return selected_clothes(clothes)


@app.route("/logout")
@login_required
def logout():
    """User log-out logic."""
    logout_user()
    return redirect(url_for('login'))


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
