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

def parseXML(xmlfile):
 
    # create element tree object
	tree = ET.parse(xmlfile)
 
	# get root element
	root = tree.getroot()
 
	# create empty list for news items
	newsitems = []
 
	# iterate news items
	for item in root.findall('./channel/item'):
 
		# empty news dictionary
		news = {}
 
		# iterate child elements of item
		for child in item:
 
			# special checking for namespace object content:media
			if child.tag == '{http://search.yahoo.com/mrss/}content':
				news['media'] = child.attrib['url']
			else:
				news[child.tag] = child.text.encode('utf8')
 
		# append news dictionary to news items list
		newsitems.append(news)
     
	# return news items list
	return newsitems

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

	# result = parseXML(xmlResult)

	return jsonify({
		# 'text': result.body
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
	print(r.status_code, r.reason, r.text)
	
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

def is_request_valid(request):
	is_token_valid = request.form['token'] == os.environ['SLACK_VERIFICATION_TOKEN']
	is_team_id_valid = request.form['team_id'] == os.environ['SLACK_TEAM_ID']

	return is_token_valid and is_team_id_valid

if __name__ == "__main__":
	app.run(debug=True)
