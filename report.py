import requests

def unshorten(url):

	session = requests.Session()  # so connections are recycled
	resp = session.head(url, allow_redirects=True)
	return resp.url

def main(textMessage, arrayMessage, userID, twitter, TWITTER_OWNER):
	if (len(arrayMessage) == 1):
		twitter.send_direct_message(userID, "You must provide an argument, use /report -help to get more information")
	elif( arrayMessage[1] == "-help" or arrayMessage[1] == "-h"):
		twitter.send_direct_message(userId, "To report a tweet you must provide the URL of the tweet you want to report, you can put as much text as you want as justification for why the tweet should get deleted\nExample:\n/report justification twitter.com/" + twitter.me().screen_name + "/status/...")
	else:
		i = 1
		found = False
		while (not found and i < len(arrayMessage)):
			if (arrayMessage[i].find("t.co") != -1):
				found = True
				url = arrayMessage[i]
		if (not found):
			twitter.send_direct_message(userID, "You must send the url of the tweet you want to report")
		else:
			url = unshorten(url)
			if (url.find("twitter.com/" + str(twitter.me().screen_name) + "/status/") == -1):
				twitter.send_direct_message(userID,"You must send the url of a tweet that contains twitter.com/" + str(twitter.me().screen_name) + "/")
			else:
				print("report received")
				#a twitter url is https://twitter.com/screen_name/status/tweetID so it finds the index of the T of Twitter and adds to it the length of the rest of the url (could be a lot quicker I think but it works)
				tweetID = url[url.find("twitter.com/" + str(twitter.me().screen_name) + "/status/") + len("twitter.com/" + str(twitter.me().screen_name) + "/status/"):]
				twitter.send_direct_message(TWITTER_OWNER, "New report received for tweet :\n" + url +"\nWith justification\n\"" + textMessage + "\"\n\nOf ID : " + tweetID +"\n\nYou can either delete the tweet with /delete [ID] example : /delete 123123123\nOr you can spare the tweet with /spare [ID] example : /spare 123123123")
				twitter.send_direct_message(userID, "The tweet has been reported, you should receive an answer soon")
				reportFile = open("report.txt", "a")
				reportFile.write(tweetID + " " + userID)
				reportFile.close

def delete(tweetID, twitter):
	try:
		twitter.destroy_status(tweetID)
		reportFile = open("report.txt")
		output =[]
		for line in reportFile.readlines():
			ids = line.split()
			if (ids[0] == tweetID):
				twitter.send_direct_message(ids[1], "Thank you for your report, the tweet has been deleted")
			else:
				output.append(line)
		reportFile.close()
		reportFile = open ("report.txt", "w")
		reportFile.writelines(output)
		reportFile.close()
	except:
		twitter.send_direct_message(TWITTER_OWNER, "The ID sent isn't valid")

def reject(tweetID, twitter):
	try:
		reportFile = open("report.txt")
		output =[]
		for line in reportFile.readlines():
			ids = line.split()
			if (ids[0] == tweetID):
				twitter.send_direct_message(ids[1], "Thank you for your report but it was decided that the tweet (twitter.com/" + twitter.me().screen_name + "/status/" + tweetID + " isn't worth deleting")
			else:
				output.append(line)
		reportFile.close()
		reportFile = open ("report.txt", "w")
		reportFile.writelines(output)
		reportFile.close()
	except:
		twitter.send_direct_messages(TWITTER_OWNER, "The ID sent isn't valid")
