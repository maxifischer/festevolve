import os
import psycopg2
import sys

from flask import Flask
app = Flask(__name__)

@app.route('/')
def main():
	# overview over all festivals
	return "festevolve"

@app.route('/helga/')
def helga():
	# looking for helga
	return 'HELGA!'

@app.route('/festival/<festival_id>')
def show_festival(festival_id):
	#show festival page with more information
	return 'Festival %d', festival_id
