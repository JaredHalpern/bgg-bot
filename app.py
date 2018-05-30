import re
import os
import csv
import json
import requests
import xml.etree.ElementTree as ET
from slackclient import SlackClient
from flask import abort, Flask, jsonify, request

slack_client = SlackClient(os.environ.get('SLACK_BGG_TOKEN'))

app = Flask(__name__)
app.config.from_object(__name__)

BASE_API_URL = 'https://www.boardgamegeek.com//xmlapi2'

@app.route('/', methods=['POST'])
def defaultPOST():
	if not is_request_valid(request):
		abort(400)

	# command = request.form.get('command', None)
	userInput = request.form.get('text', None)
	print("user input: " + userInput)
	words = userInput.split()

	queryType = words[0]
	params = ''

	for val in range (1, len(words)):
		params += ' ' + words[val]

	if not queryType:
		invalidQuery()

	# https://regex101.com/r/K6q4PR/1/
	# REQUEST_REGEX = "^([^\s]+\s+)(...*)"

	# matches = re.search(REQUEST_REGEX, userInput)

	# if not matches:
		# return jsonify({
				# 'text': 'BGG Result: ' + 'INVALID COMMAND - Try again!'
				# })

	# queryType = matches.group(1)
	# param1 = matches.group(2)
	
	# /bgg <querytype> optional: <param1>
	commandMethod = switchCommand(queryType)
	xmlResult = commandMethod(params)

	result = parseXML(xmlResult)

	return jsonify({
		'text': "hi"
		# 'response_type': 'in_channel'
		})

def searchBGG(term):
	results = "none"
	term = term.strip()

	api_url = BASE_API_URL + '/search?query=' + term
	print(api_url)
	# r.headers['content-type']
	r = requests.get(url=api_url)
	# print(r.text)
	print(r.status_code, r.reason, r.text)
	
	return r.text

def getHotGames(term):
	api_url = BASE_API_URL + '/hot?boardgame'
	r = requests.get(url=api_url)
	# print(r.status_code, r.reason, r.text)
	return r.text

def invalidQuery():
	return 'BGG Result: INVALID COMMAND - Try again!'

def switchCommand(value):
	value = str(value.lower()).strip()

	switcher = {
		"search" : searchBGG,
		"hot" : getHotGames,
		"hotgames" : getHotGames
	}
	return switcher.get(value)

def parseXML(xmlfile):
 
	root = ET.fromstring(xmlfile)
	gameItems = []

	# iterate games
	for item in root.findall('./'):
		gameDict = {}
 
		# iterate child elements of item
		for child in item:
			print(child.tag, child.attrib)
			# gameDict['thumbnail'] = child.tag['thumbnail']
			# gameDict['name'] = child.tag['name'].attrib

		gameItems.append(gameDict)

	print("number of game items " + str(len(gameItems)))
	return gameItems

def is_request_valid(request):
	is_token_valid = request.form['token'] == os.environ['SLACK_VERIFICATION_TOKEN']
	is_team_id_valid = request.form['team_id'] == os.environ['SLACK_TEAM_ID']

	return is_token_valid and is_team_id_valid

if __name__ == "__main__":
	app.run(debug=True)
