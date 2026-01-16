#!/usr/bin/env python3

from flask import Flask, request, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Hero, Power, HeroPower
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'


class Heroes(Resource):
    def get(self):
        heroes = Hero.query.all()
        return [hero.to_dict(rules=('-hero_powers',)) for hero in heroes], 200


class HeroDetail(Resource):
    def get(self, id):
        hero = Hero.query.filter_by(id=id).first()
        if not hero:
            return {'error': 'Hero not found'}, 404
        return hero.to_dict(), 200


class Powers(Resource):
    def get(self):
        powers = Power.query.all()
        return [power.to_dict(rules=('-hero_powers',)) for power in powers], 200


class PowerDetail(Resource):
    def get(self, id):
        power = Power.query.filter_by(id=id).first()
        if not power:
            return {'error': 'Power not found'}, 404
        return power.to_dict(rules=('-hero_powers',)), 200

    def patch(self, id):
        power = Power.query.filter_by(id=id).first()
        if not power:
            return {'error': 'Power not found'}, 404
        
        try:
            data = request.get_json()
            if 'description' in data:
                power.description = data['description']
            db.session.commit()
            return power.to_dict(rules=('-hero_powers',)), 200
        except ValueError:
            db.session.rollback()
            return {'errors': ['validation errors']}, 400


class HeroPowers(Resource):
    def post(self):
        try:
            data = request.get_json()
            hero_power = HeroPower(
                hero_id=data['hero_id'],
                power_id=data['power_id'],
                strength=data['strength']
            )
            db.session.add(hero_power)
            db.session.commit()
            return hero_power.to_dict(), 200
        except ValueError:
            db.session.rollback()
            return {'errors': ['validation errors']}, 400


api.add_resource(Heroes, '/heroes')
api.add_resource(HeroDetail, '/heroes/<int:id>')
api.add_resource(Powers, '/powers')
api.add_resource(PowerDetail, '/powers/<int:id>')
api.add_resource(HeroPowers, '/hero_powers')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
