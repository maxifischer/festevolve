import os
import psycopg2
import sys
from os.path import expanduser

from flask import Flask
app = Flask(__name__)

auth = open((expanduser('~') + '/Documents/festevolve/authorization/auth.txt'), 'r')
auths = auth.read().split()
client_id = auths[0]
client_secret = auths[1]
redirect_uri = auths[2]
scopes = auths[3] + ' ' + auths[4]
print(scopes)

@app.route('/')
def main():
	# overview over all festivals
	return "festevolve"

@app.route('/search/')
def helga():
	# looking for helga
	return 'HELGA!'

@app.route('/festival/<festival_id>')
def show_festival(festival_id):
	#show festival page with more information
	return 'Festival %d', festival_id

if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0', port=8888)
