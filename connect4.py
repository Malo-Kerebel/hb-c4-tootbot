import numpy as np
import tweepy


def main(arrayMessage, userID, twitter):

	if(len(arrayMessage)>1):

		if (arrayMessage[1][0] == '-'):
			
			if (arrayMessage[1] == "-challenge" or arrayMessage[1] == "-c"):
				
				challenge(arrayMessage, userID, twitter)

			elif (arrayMessage[1] == "-quit" or arrayMessage[1] == "-q"):

				deleteGame(userID)
				if (game[0] == str(userID)):
					opponentID = game[1]
				else:
					opponentID = game[0]				
				twitter.send_direct_message(userID, "You have quit the game with " + getScreenName(opponentID, twitter) + " successfully")
				twitter.send_direct_message(opponentID, getScreenName(userID, twitter) + " has quit the game")

			elif (arrayMessage[1] == "-help" or arrayMessage[1] == "-h"):

				twitter.send_direct_message(userID, help(userID))
		else:
			
			
			if (arrayMessage[1].isdecimal()):
				collumn = int(arrayMessage[1])
				if(checkUser(userID)):

					if (collumn > 0 and collumn <8):						

						game = get_game(userID)
						
						if ((game[0] == str(userID) and game[3] == str(2)) or (game[1] == str(userID) and game[3] == str(1))):
							newGame = updateGame(collumn-1,get_game(userID),userID)

							if (game[0] == str(userID)):
								opponentID = game[1]
							else:
								opponentID = game[0]
				
							if (newGame == str(-1)):
								
								twitter.send_direct_message(userID,"The collumn you entered is full, choose another one")

							elif (isDraw(get_game(userID), collumn)):
								twitter.send_direct_message(userID,"It is a draw\n" + newGame + "1   2   3   4   5   6   7")
								twitter.send_direct_message(opponentID,"It is a draw\n" + newGame + "1   2   3   4   5   6   7")
								deleteGame(userID)
							elif (isWin(get_game(userID), userID)):
								twitter.send_direct_message(opponentID, getScreenName(userID, twitter) + " won the game\n" + newGame + "1   2   3   4   5   6   7 ")
								twitter.send_direct_message(userID,"You won the game\n" + newGame + "1   2   3   4   5   6   7")
								deleteGame(userID)
							else:	
								twitter.send_direct_message(opponentID, getScreenName(userID, twitter) + " played in the collumn " + str(collumn) + '\n' + newGame + "1   2   3   4   5   6   7 \n\ntype /connect4 [int] (where [int] is the collumn you want to play in), Example : /connect4 4")
								twitter.send_direct_message(userID,"You played in the collumn " + str(collumn) + '\n' + newGame + "1   2   3   4   5   6   7")
						else:

							twitter.send_direct_message(userID,"It is not your turn yet, you will be notified when your opponent plays")

					else:		

						twitter.send_direct_message(userID,"You entered a collumn that doesn't exist, enter a collumn number between 1 and 7")

				else:

					twitter.send_direct_message(userID,"You are not currently in a game, use /connect4 -challenge @screen_name to challenge someone")

			else:

				twitter.send_direct_message(userID,"If you want to entered an option use the syntax /connect4 -option, use /connect4 -help for more information")			

	else:
		
		twitter.send_direct_message(userID, "You need to add an option to use the /connect4 command, here how to use it \n\n" + help(userID))
		 #If the user simply types /connect4, it defaults to displaying the help message

def challenge(arrayMessage, userID, twitter):

	if (checkUser(userID) == True):
					twitter.send_direct_message(userID,"you can't start a game when you are already in one")
	else:

		if(len(arrayMessage) > 2):
			handle = arrayMessage[2]
			if (handle[0] == '@'):
				scrn_name = handle.lstrip('@')
				challenged = twitter.get_user(scrn_name)
				challenged_ID = challenged.id
				if (checkUser(challenged_ID) == False):
					create_game(userID, challenged_ID)
					try:
						twitter.send_direct_message(str(challenged_ID), "You have been challenged to a game of connect 4 by " + getScreenName(str(userID), twitter) + " type /connect4 [int] (with [int] the number of the collumn you want to play in) Example : /connect4 4\nor type /connect4 -quit if you want to quit\n" + "\n⚪⚪⚪⚪⚪⚪⚪\n⚪⚪⚪⚪⚪⚪⚪\n⚪⚪⚪⚪⚪⚪⚪\n⚪⚪⚪⚪⚪⚪⚪\n⚪⚪⚪⚪⚪⚪⚪\n⚪⚪⚪⚪⚪⚪⚪\n1   2   3   4   5   6   7")
						#this message is an hardcoded initial state of the game
						twitter.send_direct_message(userID,"You have successfully created a game with " + scrn_name)
					except:
						twitter.send_direct_message(userID,"Couldn't send a DM to " + getScreenName(challenged_ID) + ", they probably don't accept strangers direct messages and don't follow this bot")
						deleteGame(userID)

				else:
			
					twitter.send_direct_message(challenged_ID, scrn_name + " is already in a game, wait for them to finish their game or to quit it (with /connect4 -quit)")

			else:
				twitter.send_direct_message(userID,"You didn't input a proper twitter handle proper syntax /connect4 - challenge @screen_name (type /connect4 -help to get more info")
		else:
			twitter.send_direct_message(userID,"You must specify someone twitter handle to challenge when challenging someone")


def create_game(challenger_ID, challenged_ID):

	gameFile = open("game.txt", 'a')
	
	game = str(challenger_ID) + " " + str(challenged_ID) + " 000000000000000000000000000000000000000000 " + '1\n'
	#the game is stored as a string of 42 characted (6*7 characters) 0 means empty, 1 means player one and 2 means player 2

	gameFile.write(game)

def deleteGame(ID):

	gameFile = open("game.txt", 'r')

	games = gameFile.readlines()

	for game in games:

		arrayGame = game.split()
		if (arrayGame[0] == str(ID)):

			deleteLine("game.txt", str(ID))

		elif (arrayGame[1] == str(ID)):

			deleteLine("game.txt", str(arrayGame[0]))

def checkUser(ID):

	gameFile = open("game.txt", 'r')

	games = gameFile.readlines()

	if (len(games) > 0):
		for game in games:

			arrayGame = game.split()
			if (arrayGame[0] == str(ID) or arrayGame[1] == str(ID)):
				return True

	return False
	#Checks every game, if the user has its ID in the database it returns True, meaning it is currently in a game, else it returns False

def get_game(ID):

	gameFile = open("game.txt", 'r')
	games = gameFile.readlines()
	i = 0
	while (i < len(games)):

		arrayGame=games[i].split()
		
		if ((arrayGame[0] == str(ID)) or (arrayGame[1] == str(ID))):

			return arrayGame
					
		i = i + 1

def updateGame(collumn,arrayGame, ID):


	game = arrayGame[2]

	gameMatrix = np.empty(shape=(6,7), dtype = "U42")
	
	for i in range(6):
		for j in range(7):
			gameMatrix[i,j] = game[i*7+j]
	#The game is stored as a string in the file and transformed as a 6*7 matrix, 0 means empty, 1 means a player one token, and 2 a player 2 token (

	if (int(gameMatrix[0,collumn]) > 0):

		return "-1"
	

	else:

		row = 0
		while (row < 5 and gameMatrix[row+1,collumn] == str(0)):
			row = row + 1
			#this while loop check if the lowest tile empty to put the token
		gameMatrix[row,collumn] = arrayGame[3]

		newGame = arrayGame[0] + ' ' + arrayGame[1] + ' '
		newGameText = ""
		#newGameText is the state of the game that will be returned for the user while newGame is the one that will be stored
		for i in range(6):
			for j in range(7):
				newGame = newGame + gameMatrix[i,j]
				if (gameMatrix[i,j] == str(0)):
					newGameText = newGameText + '⚪'
				elif (gameMatrix[i,j] == str(1)):
					newGameText = newGameText + '🔴'
				else:
					newGameText = newGameText + '🔵'
			newGameText = newGameText + '\n'

		if (arrayGame[3] == str(1)):
			newGame = newGame + ' ' + '2'
		else:
			newGame = newGame + ' ' + '1'
		#this stores the current player in the file

		changeLine("game.txt", arrayGame[0], newGame)

		return newGameText
		
def changeLine(myfile,old,new):

	f = open(myfile)
	output = []
	for line in f:
		if (line.startswith(old)):
			output.append(new)
		else:
			output.append(line)
	f.close()
	f = open(myfile, 'w')
	f.writelines(output)
	f.close()

def deleteLine(myfile, st):
	f = open(myfile)
	output = []
	for line in f:
		if not line.startswith(st):
			output.append(line)
	f.close()
	f = open(myfile, 'w')
	f.writelines(output)
	f.close()
	
def help(ID):

	return "The connect4 command accept different option to use it, the option are written with a dash (-), here are the different option:\n\n-challenge (or -c) @screenName : This option starts a game with someone.\nExample : /connect4 -challenge @screenName\nNote that you can only be in one game at a time.\n\n-quit (or -q) : This option allows you to quit a game at any time\nExample : /connect4 -quit\n\n-help (or -h) : This option displays this message\nExample : /connect4 -help\n\nFinally if you are in a game and it is your turn you simply type /connect4 [int], where [int] is the number of the collumn you want to play in, to play\nExample : /connect4 4\n\nAlso to make it quicker you can type /c4 instead of /connect4 for Example :\n/c4 -c @screenName\n/c4 -q\n/c4 -h\n are all valid command."


def getScreenName(ID,twitter):

	user = twitter.get_user(ID)
	return user.screen_name

def isDraw(arrayGame, collumn):

	game = arrayGame[2]

	gameMatrix = np.empty(shape=(6,7), dtype = "U42")
		
	for i in range(6):
		for j in range(7):
			gameMatrix[i,j] = game[i*7+j]
		#The game is stored as a string in the file and transformed as a 6*7 matrix, 0 means empty, 1 means a player one token, and 2 a player 2 token (

	if (int(gameMatrix[0,0]) > 0 and int(gameMatrix[0,1]) > 0 and int(gameMatrix[0,2]) > 0 and int(gameMatrix[0,3]) > 0 and int(gameMatrix[0,4]) > 0 and int(gameMatrix[0,5]) > 0 and int(gameMatrix[0,6]) > 0):

		return True

	else:

		return False

def isWin(arrayGame, ID):

	game = arrayGame[2]

	gameMatrix = np.empty(shape=(6,7), dtype = "U5")
	
	for i in range(6):
		for j in range(7):
			gameMatrix[i,j] = game[i*7+j]
	#The game is stored as a string in the file and transformed as a 6*7 matrix, 0 means empty, 1 means a player one token, and 2 a player 2 token	

	if (arrayGame[0] == ID):
		player = '2'
	else:
		player = '1'

	for row in range(6):
		for collumn in range(4):
			if (gameMatrix[row,collumn] == player and gameMatrix[row,collumn + 1] == player and gameMatrix[row,collumn + 2] == player and gameMatrix[row,collumn + 3] == player):
				return True
	for row in range(3):
		for collumn in range(7):
			if (gameMatrix[row,collumn] == player and gameMatrix[row + 1,collumn] == player and gameMatrix[row + 2,collumn] == player and gameMatrix[row + 3,collumn] == player):
				return True
	for row in range(3):
		for collumn in range(4):
			if (gameMatrix[row,collumn] == player and gameMatrix[row + 1,collumn + 1] == player and gameMatrix[row + 2,collumn + 2] == player and gameMatrix[row + 3,collumn + 3] == player):
				return True
	for row in range(3):
		for collumn in range(4,7):
			if (gameMatrix[row,collumn] == player and gameMatrix[row + 1,collumn - 1] == player and gameMatrix[row + 2,collumn - 2] == player and gameMatrix[row + 3,collumn - 3] == player):
				return True

	return False
