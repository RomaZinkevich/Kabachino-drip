from flask import Flask, render_template, redirect, url_for, request
from flask_wtf import FlaskForm
from flask_login import LoginManager, login_required, logout_user, current_user, login_user
from wtforms import StringField, PasswordField, BooleanField, SubmitField, validators, SelectField, TextField
from wtforms.validators import DataRequired
import sys
import json
import random
from data import db_session, clothes_db, user
from passlib.hash import sha256_crypt
from bot import message, send_photo

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


class ClothesSizesForm(FlaskForm):
    sost = SelectField("Размер: ", choices="XS;S;M;L;XL".split(';'))


class ShoesSizesForm(FlaskForm):
    sost = SelectField(
        "Размер: ", choices="UK 6;UK 7;UK 8;UK 9;UK 10;UK 11;UK 12".split(';'))


class OrderForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    mobile = StringField('Номер телефона', validators=[DataRequired()])
    address = StringField('Адрес', validators=[DataRequired()])
    city = StringField('Город', validators=[DataRequired()])
    region = StringField('Регион', validators=[DataRequired()])
    postcode = StringField('Почтовый индекс', validators=[DataRequired()])
    country = StringField('Страна', validators=[DataRequired()])
    submit = SubmitField('Заказать')


@app.route("/")
def main_page():  # Главная страница сайта
    return render_template('main.html', title='KABACHINO-DRIP')


@app.route("/success<page>")
@login_required
def success(page):
    return render_template('success.html', title='KABACHINO-DRIP', error1='', page=page)


@app.route("/order<page>", methods=['GET', 'POST'])
@login_required
def order(page):
    form = OrderForm()
    if request.method == "POST" and form.validate():
        db_session.global_init("data.db")
        db_sess = db_session.create_session()
        for i in db_sess.query(user.User).filter(current_user.id == user.User.id):
            if i.carted:
                carted_start = (str(i.carted)).split(';')
                i.carted = ''
                price = 0
                carted = []
                for j in carted_start:
                    j = j.split(',')
                    carted.append(j)
                db_sess.commit()
                text = ''
                pics = []
                for e in carted:
                    for j in db_sess.query(clothes_db.Clothes).filter(clothes_db.Clothes.id == int(e[0])):
                        clothes_name, clothes_price, clothes_pic, clothes_remaining = j.name, j.price, j.pic, j.remaining.split(
                            ';')
                        remaining = []
                        remain = ''
                        for k in clothes_remaining:
                            k = k.split(':')
                            size = str(e[2])
                            if 'UK' in str(e[2]):
                                size = str(e[2]).split("UK ")[-1]
                            if str(k[0]) == str(size):
                                remain = int(k[1]) - int(e[1])
                                remaining.append(
                                    str(k[0]) + ":" + str(int(k[1]) - int(e[1])))
                            else:
                                remaining.append(':'.join(k))
                        remaining = ';'.join(remaining)
                        j.remaining = remaining
                        db_sess.commit()
                        total_price = int(e[1]) * int(clothes_price)
                        text += f'''{clothes_name} в количестве {e[1]} шт. {e[2]}
                        Данной одежды осталось {remain}
                        '''
                        price += total_price
                        if clothes_pic not in pics:
                            pics.append(clothes_pic)
                message(f"""
                    Новый заказ от {i.login}:
                    Данные о заказе:
                    Имя: {form.name.data}
                    Фамилия: {form.surname.data}
                    Номер телефона: {form.mobile.data}
                    Адрес: {form.country.data} {form.region.data} {form.city.data} {form.address.data} {form.postcode.data}
                    Содержимое заказа: 
                    """ + text + f"""Итоговая стоимость {price} руб.""")
                for j in pics:
                    send_photo(j)
                return redirect(f'success{page}')
            else:
                return redirect(f'profile')
    return render_template('order.html', title='KABACHINO-DRIP', form=form, error1='')


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
    if not current_user.is_authenticated:
        liked = None
    else:
        liked = current_user.liked
    like = []
    for i in data:
        if liked:
            if str(i[3]) + ";" in liked or str(i[3]) == liked or ";" + str(i[3]) in liked:
                like.append('❤')
            else:
                like.append('♡')
        else:
            like.append('♡')
    return render_template('clothes.html', title='KABACHINO-DRIP', data=data, page=f'woman{clothes}', liked=like)


@app.route("/man<clothes>")
def man_clothes(clothes):  # Страница отвечающая за мужскую одежду
    datum = ''
    data = []
    like = '%M'
    db_session.global_init("data.db")
    db_sess = db_session.create_session()
    for i in db_sess.query(clothes_db.Clothes).filter((clothes_db.Clothes.sex.like(like)), (clothes_db.Clothes.type == clothes)):
        datum = (i.name, i.price, i.pic, str(i.id))
        data.append(datum)
    if not current_user.is_authenticated:
        liked = None
    else:
        liked = current_user.liked
    like = []
    for i in data:
        if liked:
            if str(i[3]) + ";" in liked or str(i[3]) == liked or ";" + str(i[3]) in liked:
                like.append('❤')
            else:
                like.append('♡')
        else:
            like.append('♡')
    return render_template('clothes.html', title='KABACHINO-DRIP', data=data, page=f'man{clothes}', liked=like)


@app.route("/<int:clothes><prev>", methods=['GET', 'POST'])
@login_required
def selected_clothes(clothes, prev):  # Страница отвечающая за мужскую одежду
    datum = ''
    error = ''
    data = []
    maxi = 0
    carted_point = '🛒'
    db_session.global_init("data.db")
    db_sess = db_session.create_session()
    for i in db_sess.query(clothes_db.Clothes).filter((clothes_db.Clothes.id == clothes)):
        datum = (i.name, i.price, i.av_sizes.split(","), i.pic, i.id)
        clothes_type = i.type
        data.append(datum)
    if clothes_type == 'shoes':
        form = ShoesSizesForm()
    else:
        form = ClothesSizesForm()
    like = '♡'
    for i in db_sess.query(user.User).filter(user.User.id == current_user.id):
        if i.liked:
            if str(clothes) + ";" in i.liked or str(clothes) == i.liked or ";" + str(clothes) in i.liked:
                like = '❤'
    if request.method == 'POST':
        # for i in db_sess.query(user.User).filter((user.User.id == current_user.id)):
        carted = []
        carted_fin = []
        flag = False
        for i in db_sess.query(clothes_db.Clothes).filter((clothes_db.Clothes.id == clothes)):
            remaining = i.remaining.split(";")
        size = form.sost.data
        if 'UK' in size:
            size = size.split("UK ")[-1]
        for i in remaining:
            i = i.split(':')
            if i[0] == str(size):
                remain = int(i[1])
        if current_user.carted != None:
            carted_start = (str(current_user.carted)).split(';')
            if carted_start != ['']:
                for i in carted_start:
                    i = i.split(',')
                    carted.append(i)
            carted_start = []
            for i in carted:
                if i[0] == str(clothes) and i[2] == form.sost.data and (remain - int(i[1])) > 0 and int(i[1]) <= 10:
                    flag = True
                    i[1] = str(int(i[1]) + 1)
                if i[1] == '10':
                    maxi = 10
                carted_start.append(i)
        flag2 = True
        for i in carted:
            if str(form.sost.data) in i:
                flag2 = False
        if flag2 and not flag:
            carted.append([str(clothes), '1', form.sost.data])
        for i in carted:
            carted_fin.append(','.join(i))
        print(maxi)
        carted_fin = ';'.join(carted_fin)
        for i in db_sess.query(user.User).filter(user.User.id == current_user.id):
            i.carted = carted_fin
        db_sess.commit()
        if maxi == 10:
            error = 'Максимум'
    return render_template('selected_clothes.html', title='KABACHINO-DRIP', carted=carted_point, form=form, data=data, like=like, prev=prev, error=error)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    error1 = ''
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    if request.method == "POST" and form.validate():
        db_session.global_init("data.db")
        db_sess = db_session.create_session()
        for i in db_sess.query(user.User):
            if form.username.data == i.login and sha256_crypt.verify(str(form.password.data), i.password):
                login_user(i)
                return redirect('')
        error1 = 'Введенный логин или пароль неправильный'
    return render_template('login.html', title='KABACHINO-DRIP', form=form, error1=error1)


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


@app.route("/cart<int:clothes><string:size><int:flag>")
@login_required
def cart(size, flag, clothes):
    data = []
    datum = ''
    db_session.global_init("data.db")
    db_sess = db_session.create_session()
    login = current_user.login
    total_price = 0
    if current_user.carted != None:
        carted_start = (str(current_user.carted)).split(';')
        if carted_start != ['']:
            carted = []
            for i in carted_start:
                i = i.split(',')
                carted.append(i)
            for j in carted:
                for i in db_sess.query(clothes_db.Clothes).filter((clothes_db.Clothes.id == int((j[0])))):
                    total_price += int(i.price) * int(j[1])
                    datum = (i.name, i.price, i.pic, i.id, j[1], j[2])
                    data.append(datum)
        else:
            carted = []
    else:
        data = []
    return render_template('cart.html', title='KABACHINO-DRIP', total_price=total_price, size=size, clothes=clothes, data=data, login=login, page='cart', flag=flag)


@app.route("/upd<int:clothes><prev><int:flag>", methods=['GET', 'POST'])
@login_required
def upd(clothes, prev, flag):
    print(1)
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
    if flag:
        return redirect(prev)
    return redirect(f'{clothes}{prev}')


@app.route("/<size>plus<int:clothes><prev>")
@login_required
def plus(size, clothes, prev):
    db_session.global_init('data.db')
    db_sess = db_session.create_session()
    carted_start = (str(current_user.carted)).split(';')
    for i in db_sess.query(clothes_db.Clothes).filter((clothes_db.Clothes.id == clothes)):
        remaining = i.remaining
    remaining = remaining.split(';')
    size_full = ''
    if 'UK' in size:
        size, size_full = size.split(' ')[1], size
    for i in remaining:
        j = i.split(':')
        if str(j[0]) == size:
            rem_size = int(j[1])
    if 'UK' in size_full:
        size = size_full
    carted = []
    carted_fin = []
    maxi = False
    for i in carted_start:
        i = i.split(',')
        carted.append(i)
    for i in carted:
        if int(i[0]) == clothes and i[2] == size:
            if int(i[1]) == 20 or int(i[1]) >= rem_size:
                maxi = True
                carted_fin.append([i[0], str(int(i[1])), i[2]])
            else:
                carted_fin.append([i[0], str(int(i[1]) + 1), i[2]])
        else:
            carted_fin.append([i[0], i[1], i[2]])
    carted = []
    for i in carted_fin:
        carted.append(','.join(i))
    carted = ';'.join(carted)
    for i in db_sess.query(user.User).filter(user.User.id == current_user.id):
        i.carted = carted
    db_sess.commit()
    if maxi:
        return redirect(f'cart{clothes}{size}1')
    return redirect(f'cart{clothes}{size}0')


@app.route("/<size>minus<int:clothes><prev>")
@login_required
def minus(size, clothes, prev):
    db_session.global_init('data.db')
    db_sess = db_session.create_session()
    carted_start = (str(current_user.carted)).split(';')
    carted = []
    carted_fin = []
    mini = False
    for i in carted_start:
        i = i.split(',')
        carted.append(i)
    for i in carted:
        if int(i[0]) == clothes and i[2] == size:
            if int(i[1]) == 1:
                mini = True
                carted_fin.append([i[0], int(i[1]), i[2]])
            else:
                carted_fin.append([i[0], str(int(i[1]) - 1), i[2]])
        else:
            carted_fin.append([i[0], i[1], i[2]])
    carted_final = []
    if mini:
        for i in carted:
            if i[0] != str(clothes) or i[2] != size:
                carted_final.append(i)
        carted_fin = carted_final
    carted = []
    for i in carted_fin:
        carted.append(','.join(i))
    carted = ';'.join(carted)
    for i in db_sess.query(user.User).filter(user.User.id == current_user.id):
        i.carted = carted
    db_sess.commit()
    return redirect(f'cart000')


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
