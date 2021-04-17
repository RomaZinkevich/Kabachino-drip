from flask import Flask, render_template, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
import sys
import json
import random
import sqlite3

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
    if sex == 'woman':
        return render_template('woman_main.html', title='PANOS', form=form)
    elif sex == 'man':
        return render_template('man_main.html', title='PANOS', form=form)
    else:
        return "<h1> Ошибка: страница не найдена </h1>"


@app.route("/woman<clothes>")
def page(clothes):
    form = SearchForm()
    if form.validate_on_submit():
        print(form.search)
        return 'АХАХАХАХАХА'
    if clothes == 'shoes':
        con = sqlite3.connect("data.db")
        cur = con.cursor()
        data = cur.execute(
            """SELECT * from shoes WHERE sex=='F' """).fetchall()
        return render_template('shoes_woman.html', title='PANOS', form=form, data=data)
    else:
        return 'пчелты'


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1', debug=True)
