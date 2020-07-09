from datetime import datetime
import tweepy
import numpy as np


def main (arrayMessage,userID,twitter):
	
	error = False
	birthday = open("birthday.txt",'r+', encoding='UTF-8')	
	returnMessage = ""

	if (arrayMessage[1] == "-optin" or arrayMessage[1] == "-i" ) :				
		returnMessage = optin(arrayMessage,userID,twitter)				
	elif (arrayMessage[1] == "/optout" or arrayMessage[1] == "-o"):
		returnMessage = optout(arrayMessage,userID,twitter)
	elif (arrayMessage[1] == "-help" or arrayMessage[1] == "-h"):
		returnMessage = returnMessage + "There are 3 options available for the /birthday command :\n\n-help (or -h) : display this message\nExample : /birthday -help\n\n-optin (or -i) followed by month of birth in figures, a space, day of birth in figures\nExample : /birthday -optin 12 31 (if you are born on the 31st of december\n\n-optout (or -o), which deletes every information about you from the database, you won't get any birthday wishes anymore\nExemple : /birthday -optout\n\nNote that you can always write /bd instead of /birthday\n\nDue to the way the bot works there is a 5 minute delay between each command is processed" + '\n'
		print ("[ OK ] Help message was sent to " + userID)
	else:
		print("[ ERROR ] Wrong command entered")
		returnMessage = returnMessage + "The option " + arrayMessage[1] + " doesn't exist. Existing option :\n-optin [month] [day]\n-optout\n-help"
	twitter.send_direct_message(userID, returnMessage)
	birthday.close()

def getScreenName(ID,twitter):

	user = twitter.get_user(ID)
	return user.screen_name

def optin(arrayMessage,userID,twitter):

	for people in birthday:

		if (people.startswith(user)):
			returnMessage = returnMessage + "User : " + getScreenName(userID, twitter) + " is already in the database, registered as : " + people + "\nIf you want to correct your birthday date please do /optout and try again" + '\n'
			error = True
		#The for loop checks if the user has already opt in so that it isn't twice in the database	
					
		if (len(arrayMessage) != 3):
			returnMessage = returnMessage + "invalid number of argument" + '\n'
			print ("[ ERROR ] invalid number of argument")
		elif (error == False) :
			try:
				month = int(arrayMessage[2])					
			except:
				returnMessage = returnMessage + "wrong argument for month : not an integer" + '\n'
				print ("[ ERROR ] wrong argument for month")
				error = True
				month = 1
			try:
				day = int(arrayMessage[3])
			except:
				returnMessage = returnMessage + "wrong argument for day : not an integer" + '\n'
				print ("[ ERROR ] wrong argument for day")
				error = True
				day = 1
			if (month > 12 or month < 1 and error == False):
				returnMessage = returnMessage + "Invalid argument for month : not between 1 and 12"  + '\n'
				print("[ ERROR ] Invalid argument for month")
				error = True
			if (day < 1 or day > 31 or (day > 30 and (month == 4 or month == 6 or month == 9 or month == 11)) or (day > 29 and month == 2) and error == False):
				returnMessage = returnMessage + "Invalid argument for day : the day " + str(day) + " doesn't exist for month " + str(month) + '\n'
				print ("[ ERROR ] Invalid argument for day")
				error = True 
			if (error == False):
				birthday.close()
				birthday = open("birthday.txt", 'a')
				birthday.write(userID + ' ' + str(month) + '/' + str(day) + '\n')
				returnMessage = returnMessage + "You will be wish an happy birthday on the " + str(month) + '/' + str(day) + " (The date is in the ISO 3601 format so month/day), you can opt-out at every moment\n"
				print ("[ OK ] birthday of " + userID + " has been added for the " + str(month) + '/' + str(day))
	return returnMessage

def optout(arrayMessage,userID,twitter):

	error = True
	for people in birthday:
		if (people.startswith(userID)):
			error = False
			deleteLine("birthday.txt",userID)
			returnMessage = returnMessage + "User : " + getScreenName(userID, twitter) + " has been deleted from the database" + '\n'
			print ( "[ OK ] User : " + userID + " has been deleted from the database")
	if (error == True):
		returnMessage = returnMessage + "User : " + getScreenName(userID, twitter) + " was not found in the database" + '\n'
		print ("[ ERROR ] User : " + getScreenName(userID, twitter) + " was not found in the database")
	return returnMessage

def check_birthday(twitter,now):
	dateToday = str(now.month) + '/' + str(now.day)
	done = open('done.txt','r')
	date_test=[]

	data = done.readlines()
	
	if (data[0] != dateToday + '\n'):
		
		done = open('done.txt', 'w')
		done.write(dateToday + '\n')
		done.write(data[1])
		#Change the date in the done.txt file so that the bot doesn't send multiple birthday wish on the same day
		
		birthday = open('birthday.txt','r')
		listString=[]
		listWord=[]

		for word in birthday.readlines():
			listString.append(word.strip('\n'))
		#Create an array of all the different entry in the birthday.txt file

		matrixBirthday = np.empty(shape=(len(listString),2), dtype = "U25")
		#Create a matrix of string of up to 25 character (the twitter handle limit)

		for i in range(0,len(listString)):
			listWord = listString[i].split()
			matrixBirthday[i,0]=listWord[0]
			matrixBirthday[i,1]=listWord[1]
		#separate the words (handle, date) in the array set before and assign each to according place in the matrix		

		i = 0
		found = 0

		for i in range(len(listString)):		

			if (matrixBirthday[i,1] == dateToday):

				found = found + 1			
				
				try:
					twitter.send_direct_message(matrixBirthday[i,0],'Hey, happy Birthday :)')
					print('[ OK ] Birthday DM sent')
				except:
					print ("[ ERROR ] couldn't send birthday DM")
		print('[ OK ] every birthday checked, found ' + str(found))
