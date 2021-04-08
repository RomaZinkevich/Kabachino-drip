from flask import Flask, render_template, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
import sys
import json
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'roma))))'


class SearchForm(FlaskForm):
    search = StringField('', validators=[DataRequired()])
    submit = SubmitField('Искать')


@app.route("/", methods=['POST', 'GET'])
def main_page():
    form = SearchForm()
    if form.validate_on_submit():
        print(form.search)
        return 'АХАХАХАХАХА'
    return render_template('main.html', title='PANOS', form=form)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1', debug=True)
