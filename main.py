from flask import Flask, render_template, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
import sys
import json
import random
import sqlite3
from data import db_session
from data import clothes_db

app = Flask(__name__)
app.config['SECRET_KEY'] = 'roma))))'


class SearchForm(FlaskForm):
    search = StringField('', validators=[DataRequired()])
    submit = SubmitField('Искать')


@app.route("/")
def main_page():
    form = SearchForm()
    if form.validate_on_submit():
        print(form.search)
        return 'АХАХАХАХАХА'
    return render_template('main.html', title='PANOS', form=form)


@app.route("/<sex>")
def gender(sex):
    form = SearchForm()
    if form.validate_on_submit():
        print(form.search)
        return 'АХАХАХАХАХА'
    if sex == 'woman' or sex == 'man':
        return render_template('choice.html', title='PANOS', form=form, sex=sex)
    else:
        return "<h1> Ошибка: страница не найдена </h1>"


@app.route("/woman<clothes>")
def woman_clothes(clothes):
    form = SearchForm()
    if form.validate_on_submit():
        print(form.search)
        return 'АХАХАХАХАХА'
    db_session.global_init("data.db")
    db_sess = db_session.create_session()
    data = []
    like = 'F%'
    for i in db_sess.query(clothes_db.Clothes).filter(clothes_db.Clothes.sex.like(like)):
        datum = (i.name, i.price, i.pic)
        data.append(datum)
    return render_template('clothes.html', title='PANOS', form=form, data=data)


@app.route("/man<clothes>")
def man_clothes(clothes):
    form = SearchForm()
    if form.validate_on_submit():
        print(form.search)
        return 'АХАХАХАХАХА'
    db_session.global_init("data.db")
    db_sess = db_session.create_session()
    datum = ''
    data = []
    like = '%M'
    for i in db_sess.query(clothes_db.Clothes).filter(clothes_db.Clothes.sex.like(like)):
        datum = (i.name, i.price, i.pic)
        data.append(datum)
    # con = sqlite3.connect("data.db")
    # cur = con.cursor()
    # data = cur.execute(
    #     f"""SELECT * from clothes WHERE sex like '%M' """, ).fetchall()
    # con.close()
    # print(data)
    return render_template('clothes.html', title='PANOS', form=form, data=data)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1', debug=True)
