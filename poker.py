import random

class Player:

    def __init__(self):
        self.playerMoney = 10000
        self.holeCards = [] #create a list of for cards
        self.handRanking = [] #create a list to store the ints for hand rankings
        self.inactive = False
        #self.currentAI = (INSERT AN AI OBJECT)

    def setAI(self):
        print("Someone should have set the AI")

    def setCards(self, incCard1, incCard2):
        self.holeCards[:] = [] #empty old hole cards.
        self.holeCards.append(incCard1)
        self.holeCards.append(incCard2)

    def drawCards(self, incDeck):
        #incCard1 = random.choice(incDeck.cards)
        #incDeck.cards.remove(incCard1)
        #incCard2 = random.choice(incDeck.cards)
        #incDeck.cards.remove(incCard2)

        incCard1 = incDeck.drawACard()
        incCard2 = incDeck.drawACard()

        self.setCards(incCard1, incCard2)
        #print("I drew cards: " + incCard1.value + incCard1.suit + ", " + incCard2.value + incCard2.suit)

    def modMoney(self, amount):
        self.playerMoney += amount
        print("Player now has $" + str(self.playerMoney))
        
    
    
class Card:
    suits = ["S", "C", "D", "H"]
    values = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]


    def __init__(self, incSuit, incValue):
        if (incSuit in Card.suits):
            self.suit = incSuit
        else:
            self.suit = "S"
            print("ERROR ASSIGNING CARD SUIT")
        if (incValue in Card.values):
            self.value = incValue
        else:
            self.value = "A"
            print("ERROR ASSIGNING CARD VALUE")
        
class Deck:

    suits = ["S", "C", "D", "H"]
    values = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]

    def __init__(self):
        self.cards = []
        for s in Deck.suits:
            for v in Deck.values:
                self.cards.append(Card(s, v))
        #print("Deck has been initialized")

    def randomizeDeck():
        print("randomized")
    #insert Code to randomize the order of the deck

    def drawACard(self):
        drawnCard = random.choice(self.cards)
        self.cards.remove(drawnCard)
        return drawnCard

    def printRemainingDeck(self):
        for x in self.cards:
            print(x.value + x.suit + ", ")




class Game:
    def __init__(self, incListOfPlayers):
        self.listOfPlayers = []
        self.smallBlind = 5
        self.bigBlind = 2 * self.smallBlind
        self.currentDealer = 0
        self.listOfPlayers = incListOfPlayers
        self.roundPlayerBets = [0] * 8
        self.currentRound = Round()

    def setNewRound(self, incRound):
        self.currentRound = incRound

    def implementAction(self, incAction):
        print("We did something")
        #Here is where we take the action sent to us by the player, implement it into the game


    def getGameState(self):
        #Here we should have some code to return a gamestate class. Maybe the game itself? Maybe we delete this function and just pass the game
        # TBD
        return 0


        

class Round:
    def __init__(self):
        self.tempPlayerBets = [0] * 8
        self.currentPot = 0
        self.deck = Deck()
        self.communityCards = []

    def incrementPot(self, incomingBet):
        self.currentPot += incomingBet

    def resetBets(self):
        self.tempPlayerBets[:] = []
        self.tempPlayerBets = [0] * 8

    def printCommunityCards(self):
        print("Printing community cards: ")
        stringX = ""
        for x in self.communityCards:
            stringX += x.value + x.suit +" "
        print(stringX)

    

class playerAction:
    actions = ["R", "B", "C", "F"]
    # R = Raise, should have a corresponding amount
    # B = Bet, should have a corresponding amounr
    # C = Check, corresponding amount = 0
    # F = Fold, corresponding amount = 0

    def __init__(self, incAction, incAmt):
        if (incAction in actions):
            self.actAction = incAction
            self.actAmt = incAmt
        else:
            self.actAction = "F"
            self.actAmt = 0
    
        

#define a list to store the players
listOfPlayers = []
#Initialize the new tournament

#how many games
numGames = 10

#how many rounds per game
numRoundsPerGame = 4

#set player loop (1 to 8, if not specified, pick at random)
for i in range(0, 8):
    print("I have set player " + str(i))
    #create 8 players
    listOfPlayers.append(Player())


#start the games +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
for i in range(0, numGames):
    currentGame = Game(listOfPlayers)
    
    #start the rounds ----------------------------------------------------------------------------------------
    print("BEGIN GAME NUMBER: " + str(i))
    for j in range(0, numRoundsPerGame):
        currentRound = Round()
        currentGame.setNewRound(currentRound)
        
        #start the game

        #set all the variable
        tempPlayerBets = [0] * 8
            
        #tempPlayerBets[:] = []
            
        #create new deck
        #d = Deck() # new deck created
        #deal the cards // randomly select cards from the deck and give them to a player.
        for p in currentGame.listOfPlayers:
            if (p.inactive == False):
                p.drawCards(currentGame.currentRound.deck)
                
        #d.printRemainingDeck() #Prints the remaining cards
        
        #deduct blinds
        numCurPlayers = len(currentGame.listOfPlayers)
        if(currentGame.listOfPlayers[(currentGame.currentDealer+1)%numCurPlayers].playerMoney>0):
            currentGame.listOfPlayers[(currentGame.currentDealer+1)%numCurPlayers].modMoney(-currentGame.smallBlind)
            currentGame.currentRound.tempPlayerBets[(currentGame.currentDealer+1)%numCurPlayers]+=currentGame.smallBlind
            
        if(currentGame.listOfPlayers[(currentGame.currentDealer+2)%numCurPlayers].playerMoney>0):
            currentGame.listOfPlayers[(currentGame.currentDealer+2)%numCurPlayers].modMoney(-currentGame.bigBlind)
            currentGame.currentRound.tempPlayerBets[(currentGame.currentDealer+2)%numCurPlayers]+=currentGame.bigBlind
            
        # 1) Loop through players and get actions until allBetsEqual
        #start at (currentDealer+3)%numCurPlayers and loop asking for actions.
        for q in range(0, 8):
            print("Get the action from player and update gamestate")
            #if q.inactive = False
            #playerAction = listOfPlayers[(q+currentDealer+3)%8].getAction(currentGamestate) #ask for the action, give current gamestate including cards, pot size, bets, stack sizes, etc

            #print("Implement the action from the player")
            #currentGame.implementAction(playerAction) #implement the action in the game engine // If the action is invalid, the player folds
            #this updates the gamestate for the next player before it loops
                

            
        #flop revealed // Draw three cards
        for f in range(0,3):
            currentGame.currentRound.communityCards.append(currentGame.currentRound.deck.drawACard())
        currentGame.currentRound.resetBets()
        currentGame.currentRound.printCommunityCards()

        # Repeat 1

        # Turn revealed
        currentGame.currentRound.communityCards.append(currentGame.currentRound.deck.drawACard())
        currentGame.currentRound.resetBets()
        currentGame.currentRound.printCommunityCards()

        # repeat 1

        # river revealed
        currentGame.currentRound.communityCards.append(currentGame.currentRound.deck.drawACard())
        currentGame.currentRound.resetBets()
        currentGame.currentRound.printCommunityCards()

        #repeat 1
            
        #resolve round + award money
        #This should be the code that evaluates the strength of each player's hand, awards money to winner
        #Assign all players a reward equal to the amount of money they won - the amount of money they bet
        
        #If a player has no more money left, remove them from the list of players for this game
        
        #If only one player left in the list of players, break out of the loop andend the game
        if (len(currentGame.listOfPlayers) == 1):
            break
        
        #last part of resolving is to increment the dealer
        currentGame.currentDealer = (currentGame.currentDealer + 1)%numCurPlayers

    #HERE IS THE END OF THIS GAME
