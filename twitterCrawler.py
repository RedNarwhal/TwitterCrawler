# https://marcobonzanini.com/2015/03/02/mining-twitter-data-with-python-part-1/
# http://docs.tweepy.org/en/latest/api.html
# https://developer.twitter.com/en/docs/tweets/data-dictionary/overview/tweet-object
# https://github.com/Jefferson-Henrique/GetOldTweets-python

"""
	TODO
	
	- grab more tweets earlier than the day of running. Sandbox can only be used by Ad APIs as per the Twitter documentation. 
		Standard accounts can only get 7 days of tweets. It was suggested that you could download the entire tweet history of a specific user. 
		Another suggestion is that we open a StreamListener, and leave it running for several hours and/or days. Problem with this method is that we have no control over what the Listener gives us 
	- filter out tweets that have already been grabbed by the crawler
	- fix the header function

"""

import tweepy
from tweepy.auth import OAuthHandler
import string
import config
import csv

def getHeaders():
	header = ["Keyword", "User", "Screen Name","String ID", "URL", "Creation Date", "Tweet Text", "Retweets", "Language", "Tweeter Location" "Place"] #add index and what keyword was used later. Removed URL field because it was not the URL of the tweet
	return header

def getResults(keyword, username, screenName, tweetid, url, creationDate, tweetText, retweets, language, location, place):
	result = [keyword, username, screenName, tweetid, url, creationDate, tweetText, retweets, language, location, place]
	return result

def getID(id):
	result = [id]
	return result

def writeToFile(file, writeArray):
	try:
		with open(file, mode='a') as tweets:
			tweetWriter = csv.writer(tweets, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
			tweetWriter.writerow(writeArray)								
			tweets.close()
	except tweepy.TweepError:
		print("Error!")
		print(tweepy.TweepError)

def queryConstructor(searchTerm):
	query = "'" + searchTerm + "' -filter:retweets" # adding a hashtag to the search query seems to filter out more of the unrelated tweets, but also severely limits the number of tweets returned. 
	print(query)
	return query

tweetOutputFile = "tweetsV3.csv"
tweetidFile = "tweetIDs.csv"

# import list of keywords
searchList = []
with open('keywords.txt', 'r') as myfile:
	search=myfile.read().replace('\n', '')
	print("search file imported\n")
	if search is not None:
		searchList = search.split(',')

idList = [] # IdList is filtering out some Tweets
with open(tweetidFile, 'r') as myfile:
	search = myfile.read().replace('\n', '')
	print("Tweet ids imported\n")
	if search is not None:
		idList = search.split(',')

#additional config file required containing consumer_key, consumer_secret, access_token, and access_secret acquired from Twitter
auth = OAuthHandler(config.consumer_key, config.consumer_secret) 
auth.set_access_token(config.access_token, config.access_secret)

print("Connected to Twitter\n")

api = tweepy.API(auth, wait_on_rate_limit=True)

sniffer = csv.Sniffer() #create csv sniffer that can be used to check a csv file 

if not sniffer.has_header(tweetOutputFile): # if the sniffer detects a header in the first row of the csv, it will skip over adding the headers # sniffer doesn't seem to detect the headers
	writeToFile(tweetOutputFile, getHeaders())
	print("Header created")

#loop here for multiple passes

#for loop for all keywords
for keyword in searchList: #loop through the keyword list
 
	query = queryConstructor(keyword) # create the query to be used for searching Twitter

	print("Query Constructed")

	for result in api.search(q=query, count=100, tweet_mode='extended'):# count is number of returned tweets, max is 100, tweet_mode='extended' makes sure that tweets are not trunicated (displays tweets longer than 140 characters)
		
		# for id in idList: # loop through the idList

		if(result.lang == "en"): # only adds tweets in English to the csv since I can't read tweets written in other languages

			if result.id not in idList: # supposed to check for duplicates and filter them out, but duplicates keep popping up

				# idList.append(result.id)

				if(result.entities['urls']): # checks to see if the tweet entity has a url attribute, and if it does it will add that to the csv. If not it will just say that there is none available
					# print(result.entities['urls'][0]['url'])
					writeToFile(tweetOutputFile, getResults(keyword, result.user.name, result.user.screen_name, result.id_str, result.entities['urls'][0]['url'], result.created_at, result.full_text, result.retweet_count, result.lang, result.user.location, result.place)) # removed URL. It was not the URL of the tweet itself
					writeToFile(tweetidFile, getID(result.id))
				else:
					writeToFile(tweetOutputFile, getResults(keyword, result.user.name, result.user.screen_name, result.id_str, "No URL available", result.created_at, result.full_text, result.retweet_count, result.lang, result.user.location, result.place))
					writeToFile(tweetidFile, getID(result.id))
