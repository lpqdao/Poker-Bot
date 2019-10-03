import random
import itertools

class Player:

    def __init__(self, typeOfAI):
        self.playerMoney = 10000
        self.holeCards = [] #create a list of for cards
        self.handRanking = [] #create a list to store the ints for hand rankings
        self.inactive = False
        self.allIn = False
        self.currentAI = PlayerAI(self, typeOfAI)

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

    def returnAction(self):
        #for now it doesn't utilize the gamestate, though we should implement that
        return self.currentAI.returnAction()

    

    def returnBestHand(self, arrayOfCommunityCards):
        print("Here we find the best hand that the player has")
        allCards = arrayOfCommunityCards
        for p in player.holeCards:
            allCards.append(p)
        
        #returns all possible combinations of 5 cards from the seven available.
        if (len(allCards) >= 5):
            #aka we have seen at least the flop
            possibleHands = list(itertools.combinations(allCards, 5))
        else:
            #AKA if we still have only the hole cards, then there is only one possible combination of those two
            possibleHands = list(itertools.combinations(allCards, 2))

        for h in possibleHands:
            #for each hand that is possibly the best, evaluate it and give it a ranking
            intHandStraightedness = getStraightedness(h)
        
        
    def getStraightedness(self, incomingHand):
        #incoming hands should already be sorted if possible, but we should verify
        
        #sort the incoming hand
        #check the straightedness
        #return Straightedness
        return 0

    def getSuitedness (self, incomingHand):
        #we should return a histogram of suitedness
        #declare a list/tuple with four slots
        suitednessVector = [0] * 4
        #iterate through each of the 5 cards in the incoming hand
        for h in incomingHand:
            if (h.suit=="S"):
                suitednessVector[0]+=1
            elif (h.suit=="C"):
                suitednessVector[1]+=1
            elif (h.suit == "D"):
                suitednessVector[1] += 1
            elif (h.suit == "H"):
                suitednessVector[1] += 1
        return suitednessVector

        #for each card, increment the first element if spades, second if clubs, third if diamonds, fourth if hearts
        #return the list with the histogram
        return 0

    def getPairedness (self, incomingHand):
        #We should return a histogram of pairedness
        #declare a list/tuple with 13 slots
        pairednessVector = [0] * 13
        #iterate through each of the cards and increment the histogram bucket for each card (2 - A) -> (13 - 1)
        for h in incomingHand:
            if (h.value=="A"):
                pairednessVector[0] +=1
            elif (h.value=="K"):
                pairednessVector[1]+=1
            elif (h.value == "Q"):
                pairednessVector[2] += 1
            elif (h.value == "J"):
                pairednessVector[3] += 1
            elif (h.value == "T"):
                pairednessVector[4] += 1
            elif (h.value == "9"):
                pairednessVector[5] += 1
            elif (h.value == "8"):
                pairednessVector[6] += 1
            elif (h.value == "7"):
                pairednessVector[7] += 1
            elif (h.value == "6"):
                pairednessVector[8] += 1
            elif (h.value == "5"):
                pairednessVector[9] += 1
            elif (h.value == "4"):
                pairednessVector[10] += 1
            elif (h.value == "3"):
                pairednessVector[11] += 1
            elif (h.value == "2"):
                pairednessVector[12] += 1

        #return the histogram
        return pairednessVector

    def getHighCard(self, incomingHand, incPairedness, incOrder):
        #this should return the value of the value of the highest card matching the requested degree, -1 if no matches
        #Example: Incoming hand: {K, K, Q, Q, 5}, pairedness = 3, order = 1 --> -1 (none)
        #Example: Incoming hand: {K, K, Q, Q, 5}, pairedness = 2, order = 1 --> 2 (king)
        #Example: Incoming hand: {K, K, Q, Q, 5}, pairedness = 2, order = 2 --> 3 (queen)
        #Example: Incoming hand: {K, K, K, Q, 5}, pairedness = 3, order = 1 --> 2 (king) 
        #Example: Incoming hand: {K, K, K, Q, 5}, pairedness = 3, order = 2 --> -1 (none)

        pairednessVector = getPairedness(incomingHand)

        currentOrder = 0
        for c in range(0, 13):
            if (pairednessVector[c] >= incPairedness):
                currentOrder+=1
            if (currentOrder == incOrder):
                #return one more than i (if i = 0, we're on ace, so return value 1
                return c+1


        return -1

        

    #We now have all 7 cards in one list. Need to evaluate max pairedness, straightedness, and suitedness
    

class PlayerAI:
    def __init__(self, parentPlayer, incName):
        self.name = incName
        self.parentPlayer = parentPlayer

    #this will need to ultimately have access to the gamestate, either by adding it to the playerAI or directly as 
    def returnAction(self):
        if (self.name == "Default"):
            #for now just tries to bet 0
            return PlayerAction("B", 0)
            #returnAction = PlayerAction("B", 0)
            #return returnAction
        elif (self.name == "Random"):
            #CODE FOR RANDOM ACTIONS
            intAction = random.randint(1,5)
            if (intAction == 1):
                print("WE WILL RAISE")
                intRaiseAmount = random.randint(1, self.parentPlayer.playerMoney)
                return PlayerAction("R", intRaiseAmount)
                #returnAction = PlayerAction("R", intRaiseAmount)
                #return returnAction
            
            elif (intAction == 2):
                print("WE WILL BET")
                intBetAmount = random.randint(1, self.parentPlayer.playerMoney)
                return PlayerAction("B", intBetAmount)

                #returnAction = PlayerAction("B", intBetAmount)
                #return returnAction
            elif (intAction == 3):
                print("WE WILL CALL")
                intCallAmount = random.randint(1, self.parentPlayer.playerMoney)
                return PlayerAction("C", intCallAmount)
                #returnAction = PlayerAction("C", intCallAmount)
                #return returnAction
            elif (intAction == 4):
                print ("WE WILL FOLD")
                return PlayerAction("F", 0)
                #returnAction = PlayerAction("F", 0)
                #return returnAction
            else:
                return PlayerAction("F", 0)
        elif (self.name == "Player"):
            #INSERT PLAYER CODE ACTIONS @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            #for now we just fold, because we have nothing
            #returnAction = PlayerAction("F", 0)
            #return returnAction
            returnAction = PlayerAction("F", 0)

            #INSERT PLAYER CODE ACTIONS @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
        else:
            #DO RANDOM ACTIONS
            #returnAction = PlayerAction("F", 0)
            #return returnAction
            return PlayerAction("F", 0)
        
    
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

    def randomizeDeck(self):
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

    def implementAction(self, incAction, incPlayer, incPlayerIndex):
        print("We did something")
        incAct = incAction.actAction
        if (incAct == "R"):
            if (incPlayer.playerMoney >= incAction.actAmt):
                #if player raised (like from 200 to 500) deduct what they currently have in pot and add total amount (they added +300)
                self.currentRound.currentPot += incAction.actAmt - self.currentRound.tempPlayerBets[incPlayerIndex]
                #player's money is incremented by previous bet amount minus new raised amount (should be negative)
                self.listOfPlayers[incPlayerIndex].playerMoney += (self.currentRound.tempPlayerBets[incPlayerIndex] - incAction.actAmt)
                #replace what they bet with their new maximum bet
                self.currentRound.tempPlayerBets[incPlayerIndex] = incAction.actAmt
                self.currentRound.maximumBet = incAction.actAmt
            else:
                #the player didn't have enough money for their action, action invalid, they fold.
                #player is inactive for the remainder of the round
                incPlayer.inactive = True
                #player no longer has any bet standing in this hand
                self.CurrentRound.tempPlayerBets[incPlayerIndex] = 0;
                
        elif (incAct == "B"):
            if ((incPlayer.playerMoney >= incAction.actAmt) and ((self.currentRound.maximumBet == 0) or (incAction.actAmt == currentRound.maximumBet))):
                #if player has enough money, and the amount is >= the max bet or is the first bet, then implement it

                #increase the pot
                self.currentRound.currentPot += incAction.actAmt

                #increase player bet amount + deduct their bet from their money
                self.listOfPlayers[incPlayerIndex].playerMoney -= incAction.actAmt
                self.currentRound.tempPlayerBets[incPlayerIndex] += incAction.actAmt
                
                #set the new maximum bet if this is a new bet
                if(self.currentRound.maximumBet == 0):
                    self.currentRound.maximumBet = incAction.actAmt
            else:
                #player is inactive for the remainder of the round
                incPlayer.inactive = True
                #player no longer has any bet standing in this hand
                self.currentRound.tempPlayerBets[incPlayerIndex] = 0;
        elif (incAct == "C"):
            #if the player has enough money and the amount they entered is exactly equal to the maximum bet
            if ((incPlayer.playerMoney >= incAction.actAmt) and (incAction.actAmt >= self.currentRound.maximumBet)):
                self.currentRound.currentPot += self.currentRound.maximumBet

                #increase the player bet ammount and deduct their bet from their money
                self.listOfPlayers[incPlayerIndex].playerMoney -= self.currentRound.maximumBet
                self.currentRound.tempPlayerBets[incPlayerIndex] += self.currentRound.maximumBet

                #max bet doesn't change in a call, so skip that
            elif (incPlayer.playerMoney < self.currentRound.maximumBet):
                #the player doesn't have enough to cover the max bet but is calling
                ## PERFECT SIDEPOTS LATER
                self.currentRound.currentPot += incPlayer.playerMoney
                self.currentRound.tempPlayerBets[incPlayerIndex] += incPlayer.playerMoney
                incPlayer.playerMoney = 0
                incPlayer.allIn = True
            else:
                #player is inactive for the remainder of the round
                incPlayer.inactive = True
                #player no longer has any bet standing in this hand
                self.currentRound.tempPlayerBets[incPlayerIndex] = 0;
        elif (incAct == "F"):
            #player is inactive for the remainder of the round
            incPlayer.inactive = True
            #player no longer has any bet standing in this hand
            self.currentRound.tempPlayerBets[incPlayerIndex] = 0;
        else:
            #unknown or invalid action, player folds.
            #player is inactive for the remainder of the round
            incPlayer.inactive = True
            #player no longer has any bet standing in this hand
            self.currentRound.tempPlayerBets[incPlayerIndex] = 0;            
                
                
                
            
        #switch(incAction.actAction) 
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
        #current betting round's (not hand's) maximum bet
        self.maximumBet = 0

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

    

class PlayerAction:
    actions = ["R", "B", "C", "F"]
    # R = Raise, should have a corresponding amount
    # B = Bet, should have a corresponding amount, a check is a bet of 0
    # C = Call, corresponding amount = unknown. Player can call with max(currentMaxBet, playerMoney) but if they don't have enough money, they only get the sidepot
    # F = Fold, corresponding amount = 0

    def __init__(self, incAction, incAmt):
        if (incAction in self.actions):
            self.actAction = incAction
            self.actAmt = incAmt
        else:
            self.actAction = "F"
            self.actAmt = 0
    
        

#Initialize the new tournament

#how many games
numGames = 10

#how many rounds per game
numRoundsPerGame = 4




#start the games +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
for i in range(0, numGames):
    #define a list to store the current players
    listOfPlayers = []
    #set player loop (1 to 8, if not specified, pick at random)
    for i in range(0, 8):
        print("I have set player " + str(i))
        #create 8 players, ALL RANDOM FOR NOW
        listOfPlayers.append(Player("Random"))
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
        for q in range(0, numCurPlayers):
            print("Get the action from player and update gamestate")
            standinForGamestate = []
            if ((currentGame.listOfPlayers[q].inactive == False) and (currentGame.listOfPlayers[q].allIn == False)):
                #newPlayerAction = p.currentAI.returnAction(standinForGamestate)
                #ask for the action, give current gamestate including cards, pot size, bets, stack sizes, etc.
                #newPlayerAction = currentGame.listOfPlayers[(q+currentGame.currentDealer+3)%numCurPlayers].currentAI.returnAction(standinForGamestate)
                newPlayerAction = currentGame.listOfPlayers[(q+currentGame.currentDealer+3)%numCurPlayers].currentAI.returnAction() 
                #print("Implement the action from the player")
                currentPlayer = currentGame.listOfPlayers[(q+currentGame.currentDealer+3)%numCurPlayers]
                #implement the action in the game engine // If the action is invalid, the player folds
                currentGame.implementAction(newPlayerAction, currentPlayer, currentGame.listOfPlayers.index(currentPlayer))
                #this updates the gamestate for the next player before it loops
            else:
                print("Player action skipped because player all in or out of game")
                

            
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


        #set all players to not inactive and not all in
        #If a player has no more money left, remove them from the list of players for this game
        for p in currentGame.listOfPlayers:
            p.inactive = False
            p.allIn = False
            if (p.playerMoney <= 0):
                currentGame.listOfPlayers.remove(p)
        
        #If only one player left in the list of players, break out of the loop and end the game
        if (len(currentGame.listOfPlayers) == 1):
            break
        
        #last part of resolving is to increment the dealer
        currentGame.currentDealer = (currentGame.currentDealer + 1)%numCurPlayers

    
    #HERE IS THE END OF THIS GAME
    #There should be some code here to collect the final state of the game, such as the amount of money held by each player (could be 80,000 by 1, 0 by the rest, etc)
    #INSERT SOME CODE TO DELETE THE CURRENT GAME
