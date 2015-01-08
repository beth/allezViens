from flask import Flask, request, jsonify, redirect, url_for
from flask.ext.mail import Mail
from flask.ext.sqlalchemy import SQLAlchemy
import os
import json
import sys
import customutilities

app = Flask(__name__, static_folder='client', static_url_path='')
mail = Mail(app)


app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL",'postgresql://localhost/allezviens')
db = SQLAlchemy(app)

# app.config.update(
# 	#Comment out for production
# 	# DEBUG=True,
# 	#Email Settings
# 	MAIL_SERVER='smtp.gmail.com',
# 	MAIL_PORT=465,
# 	MAIL_USE_SSL=True,
# 	MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
# 	MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
# 	)
db = SQLAlchemy(app)

from connect import * 
from communication import *

@app.route('/')
def root():
	return app.send_static_file('index.html')

@app.route('/api/passenger/update', methods=['POST'])
def passengerUpdate():
	print 'api passenger update'
	if (request.headers['Content-Type'][:16] == 'application/json'):
		data = json.loads(request.data)
		data = customutilities.detuplify(data)
		if updatePassenger(data):
			return 'Passenger record updated successfully'
		else:
			return 'ERROR. Passenger record was not updated.'

@app.route('/api/driver/update', methods=['POST'])
def driverUpdate():
	print 'api driver update'
	if (request.headers['Content-Type'][:16] == 'application/json'):
		data = json.loads(request.data)
		data = customutilities.detuplify(data)
		print 'after data'
		if updateDriver(data):
			return 'Driver record updated successfully.'
		else:
			return 'ERROR. Driver record not updated.'

@app.route('/api/driver', methods=['GET', 'POST'])
def drivers():
	if (request.method == 'GET'):
		oLat, oLon = float(request.args.get('oLat')), float(request.args.get('oLon'))
		dLat, dLon = float(request.args.get('dLat')), float(request.args.get('dLon'))
		date = request.args.get('date')
		results = findMatchableDrivers(oLat, oLon, dLat, dLon, date)
		return jsonify(matches=results)
	if (request.method == 'POST'):
		if (request.headers['Content-Type'][:16] == 'application/json'):
			data = json.loads(request.data)
			if (data['type'] == 'create'):
				oLat, oLon = float(data['origin'][0]), float(data['origin'][1])
				dLat, dLon = float(data['destination'][0]), float(data['destination'][1])
				addDriver(data['id'], oLat, oLon, dLat, dLon, data['date'])
				# sendValidationEmail(data['id'], 'http://giphy.com/gifs/running-penguin-baby-s73EQWBuDlcas')
				return 'Driver added to database'
			if (data['type'] == 'pick'):
				pickPassenger(data['passengerID'],data['driverID'])
				return 'Successful pick'

@app.route('/api/passenger', methods=['GET', 'POST'])
def passengers():
	if (request.method == 'GET'):
		oLat, oLon = float(request.args.get('oLat')), float(request.args.get('oLon'))
		dLat, dLon = float(request.args.get('dLat')), float(request.args.get('dLon'))
		date = request.args.get('date')
		results = findMatchablePassengers(oLat, oLon, dLat, dLon, date)
		return jsonify(matches=results)
	if (request.method == 'POST'):
		if (request.headers['Content-Type'][:16] == 'application/json'):
			data = json.loads(request.data)
			if (data['type'] == 'create'):
				oLat, oLon = float(data['origin'][0]), float(data['origin'][1])
				dLat, dLon = float(data['destination'][0]), float(data['destination'][1])
				addPassenger(data['id'], oLat, oLon, dLat, dLon, data['date'])
				# sendValidationEmail(data['id'], 'http://giphy.com/gifs/running-penguin-baby-s73EQWBuDlcas')
				return 'Passenger added to database'
			if (data['type'] == 'pick'):
				pickDriver(data['driverID'],data['passengerID'])
				return 'Successful pick'

@app.route('/api/trip/<urlID>', methods=['GET'])
def apitrip(urlID):
	print 'in api trip'
	if (request.method == 'GET'):
		print 'in api trip'
		print urlID
		type, info = getInfoByUrl(urlID)
		if(type == 'P'):
		  return jsonify(passenger=info[0])
		if(type == 'D'):
		  return jsonify(driver=info[0])
	
@app.route('/trip/<urlID>', methods=['GET'])
def trip(urlID):
	print 'in trip urlid'
	if (request.method == 'GET'):
		print 'get method'
		print urlExists(urlID)
		if(urlExists(urlID)):
			print 'url exists'
			return app.send_static_file('index.html')
		else: 
			print 'url does not exist'
			return '404 route not found'
	

if (__name__ == '__main__'):
    app.run()