import os
import csv
import requests
import xml.etree.ElementTree as ET
from slackclient import SlackClient
from flask import abort, Flask, jsonify, request

slack_client = SlackClient(os.environ.get('SLACK_BGG_TOKEN'))

app = Flask(__name__)
app.config.from_object(__name__)

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
	command = request.form.get('text', None)
	print(command)
	commandMethod = switchCommand(command)
	commandMethod()

	# https://regex101.com/r/K6q4PR/1/
	# not perfect - will allow for 1d66, 2d44, etc
	REQUEST_REGEX = "^([^\s]+\s+)(...*)"

	matches = re.search(REQUEST_REGEX, parameter_text)

	if not matches:
		return jsonify({
				'text': 'BGG Result: ' + 'INVALID COMMAND - Try again!',
				# 'attachments': [
				# 			{
				# 			'color': '#C70005',
				# 			'author_name': 'BGG',
				# 			# 'image_url': 'https://i.imgur.com/aSRSGkG.gif',
				# 			}
				# 			]
				})

	return jsonify({
		'text': 'bgg result'
		# 'response_type': 'in_channel'
		})

def switchCommand(value):
	
	value = value.lower()

	switcher = {
		"search" : searchBGG
		# list more commands here
	}
	return switcher.get(value, lambda: "not found")

def searchBGG(term):
	results = "none"
	
	return results

def is_request_valid(request):
	is_token_valid = request.form['token'] == os.environ['SLACK_VERIFICATION_TOKEN']
	is_team_id_valid = request.form['team_id'] == os.environ['SLACK_TEAM_ID']

	return is_token_valid and is_team_id_valid

if __name__ == "__main__":
	app.run(debug=True)
