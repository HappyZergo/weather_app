import datetime

import requests
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'

db = SQLAlchemy(app)


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    temp = db.Column(db.Integer)
    description = db.Column(db.String(20))
    date = db.Column(db.Integer)
    icon = db.Column(db.String(20))

    def __init__(self,id, name, temp, description, date, icon):
        self.id = id
        self.name = name
        self.temp = temp
        self.description = description
        self.date = date
        self.icon = icon


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        new_city = request.form.get('city')

        check = db.session.query(City.query.filter(City.name == new_city).exists()).scalar()

        if check != True:

            url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=271d1234d3f497eed5b1d80a07b3fcd1'

            r = requests.get(url.format(new_city)).json()

            weather = {
                'status': "on server",
                'id' : r['id'],
                'name': r['name'] ,
                'temp': r['main']['temp'],
                'description': r['weather'][0]['description'],
                'icon': r['weather'][0]['icon'],
                'date': datetime.datetime.fromtimestamp(r['dt']).strftime("%d/%m/%y %I:%M"),
            }

            weatherdb = City(weather.get('id'), weather.get('name'), weather.get('temp'), weather.get('description'),  weather.get('date'), weather.get('icon'))
            db.session.add(weatherdb)
            db.session.commit()

        else:
#
            selid = db.session.query(City.id).filter_by(name = new_city)
            id = db.session.execute(selid).fetchone()
            weather = City.query.get(id)

        return render_template('weather.html', weather=weather)

    else:
        weather = {
            'status': "Введите город",
            'temp': 'Что бы узнать температуру ',
            'icon': '01d',
        }

        return render_template('weather.html', weather = weather)