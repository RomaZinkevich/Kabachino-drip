from flask_restful import reqparse, abort, Api, Resource
from flask import Flask, render_template, redirect, url_for, request
from data import db_session, clothes_db, user
from flask import current_app, flash, jsonify, make_response, redirect, request, url_for
import jsonify


app = Flask(__name__)
app.config['SECRET_KEY'] = 'hgowoeqeghsdlgh'

api = Api(app)


def abort_if_news_not_found(user_id):
    session = db_session.create_session()
    news = session.query(user.User).get(user_id)
    if not news:
        abort(404, message=f"News {user_id} not found")


class NewsResource(Resource):
    def get(self, news_id):
        abort_if_news_not_found(news_id)
        session = db_session.create_session()
        news = session.query(News).get(news_id)
        return jsonify({'news': news.to_dict(
            only=('title', 'content', 'user_id', 'is_private'))})

    def delete(self, news_id):
        abort_if_news_not_found(news_id)
        session = db_session.create_session()
        news = session.query(user.User).get(news_id)
        session.delete(news)
        session.commit()
        return jsonify({'success': 'OK'})


class NewsListResource(Resource):
    def get(self):
        db_session.global_init("data.db")
        session = db_session.create_session()
        news = session.query(user.User).all()
        print(news)
        return jsonify({'users': [item.to_dict() for item in news]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        news = News(
            title=args['title'],
            content=args['content'],
            user_id=args['user_id'],
            is_published=args['is_published'],
            is_private=args['is_private']
        )
        session.add(news)
        session.commit()
        return jsonify({'success': 'OK'})


parser = reqparse.RequestParser()
parser.add_argument('title', required=True)
parser.add_argument('content', required=True)
parser.add_argument('is_private', required=True, type=bool)
parser.add_argument('is_published', required=True, type=bool)
parser.add_argument('user_id', required=True, type=int)


api.add_resource(NewsListResource, '/api/v2/news')


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1', debug=True)
