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
        self.bestHandCalculated = False
        self.handRanking.append(1000)

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
        #print("Player now has $" + str(self.playerMoney))

    def returnAction(self):
        #for now it doesn't utilize the gamestate, though we should implement that
        return self.currentAI.returnAction()
        
    

    def returnBestHand(self, arrayOfCommunityCards):
        # Return Best Hand function
        #   Inputs: The list of community cards
        #   Returns: None
        #   Modifies: self.handRanking[]
        #   
        #   Function will take in the current community cards and construct the best possible hand based on those community cards.
        #   It should be agnostic about how many or few cards there are, because it should never be called except after the player
        #   has been dealt hole cards. Since it will work for any arbitrary amount of cards greater than or equal to 1, it should
        #   always function.

        #DEBUGTEXT
        #print("Here we find the best hand that the player has")
        allCards = arrayOfCommunityCards
        for p in self.holeCards:
            allCards.append(p)
        
        #returns all possible combinations of 5 cards from the seven available.
        if (len(allCards) >= 5):
            #aka we have seen at least the flop
            possibleHands = list(itertools.combinations(allCards, 5))
        else:
            #AKA if we still have only the hole cards, then there is only one possible combination of those two
            possibleHands = list(itertools.combinations(allCards, 2))

        tempHandRanking = [1000] * 6
        for h in possibleHands:
            #for each hand that is possibly the best, evaluate it and give it a ranking
            intHandValue = 0
            intHandStraightedness = self.getStraightedness(h)
            listHandPairedness = self.getPairedness(h)
            listHandSuitedness = self.getSuitedness(h)
            maxSuitedness = max(listHandSuitedness) #This should find the highest suitedness, so we can check if it is 5.
            if (intHandStraightedness==5):
                intHandValue+=64 #set the 7th bit to 1
            if (maxSuitedness==5):
                intHandValue+=32 #set the 6th bit to 1
            if (self.getHighCard(h, 1, 1) == 1): #If the highest card with pairedness >=1 is ace (value 1) then set 5th bit
                intHandValue+=16
            suitednessHistogram = [0] * 4
            for x in listHandSuitedness:
                if x == 1:
                    suitednessHistogram[3]+=1
                elif x == 2:
                    suitednessHistogram[2] += 1
                elif x == 3:
                    suitednessHistogram[1] += 1
                elif x == 4:
                    suitednessHistogram[0] += 1
            if suitednessHistogram[2] == 1:
                #if there is exactly one pair, set the 4th bit
                intHandValue += 8
            if suitednessHistogram[1]==1:
                #if there is exactly one triplet, set the third bit
                intHandValue += 4
            if suitednessHistogram[0]==1:
                #if exactly one quad, set the second bit
                intHandValue+=2
            if suitednessHistogram[3]==1:
                #if there is exactly one card that is a single, all others are paired, set the first bit
                intHandValue+=1

            #THE HAND VALUE SHOULD NOW BE SET AND REPRESENTED BY THE SEVEN LEAST SIGNIFICANT BITS IN THIS INTEGER
            if (intHandValue >=112):
                #at least the 16, 32, and 64 bits are 1
                tempHandRanking[0] = 1
            elif (intHandValue >= 96):
                #at least the 32 and 64 bits are 1
                tempHandRanking[0] = 2
            elif (intHandValue >= 64):
                #at least the 64 bit is 1
                tempHandRanking[0] = 6
            elif (intHandValue >= 32):
                #at least the 32 bit is 1
                tempHandRanking[0] = 5
            elif (intHandValue >= 12):
                #at least the 4 and 8 bits are 1
                tempHandRanking[0] = 4
            elif (intHandValue >= 8):
                #at least the 8 bit is 1
                tempHandRanking[0] = 9
            elif (intHandValue >= 4):
                #at least the 4 bit is 1
                tempHandRanking[0] = 7
            elif (intHandValue >= 2):
                #at least the 2 bit is 1
                tempHandRanking[0] = 3
            elif (intHandValue >= 1):
                #at least the 1 bit is 1
                tempHandRanking[0] = 8
            elif (intHandValue >= 0):
                #all bits are zero, hand is a high card hand
                tempHandRanking[0] = 10
            else:
                #something has gone wrong, the hand loses
                tempHandRanking[0] = 100


            #NOW INITIALIZE OWN BEST HAND VALUE ARRAY, USE THIS NUMBER TO DETERMINE THE FIRST INDEX, THEN GROW IT BY THE KICKERS
            #However, we do not need to build the kicker's list if the hand is strictly weaker than what we already have.
            #E.G., if we already have quads, why build kicker list for a high card hand?

            if (tempHandRanking[0] <= self.handRanking[0]): #If the hand we have is better than or equal to our current hand
                #This block of if statements builds the kicker lists
                if (tempHandRanking[0] == 1 or tempHandRanking[0] == 100):
                    #there are no kickers
                    tempHandRanking[1] == 0
                elif (tempHandRanking[0] == 2):
                    #P1
                    tempHandRanking[1] = self.getHighCard(h, 1, 1) #get the high card from the hand with pairedness 1 and order 1
                elif (tempHandRanking[0] == 3):
                    #P4, P1
                    tempHandRanking[1] = self.getHighCard(h, 4, 1)
                    tempHandRanking[2] = self.getHighCard(h, 1, 1)
                elif (tempHandRanking[0] == 4):
                    #P3, P2
                    tempHandRanking[1] = self.getHighCard(h, 3, 1)
                    tempHandRanking[2] = self.getHighCard(h, 2, 1)
                elif (tempHandRanking[0] == 5):
                    #P1
                    tempHandRanking[1] = self.getHighCard(h, 1, 1)
                elif (tempHandRanking[0] == 6):
                    #P1
                    tempHandRanking[1] = self.getHighCard(h, 1, 1)
                elif (tempHandRanking == 7):
                    #P3, P1, P1
                    tempHandRanking[1] = self.getHighCard(h, 3, 1)
                    tempHandRanking[2] = self.getHighCard(h, 1, 1)
                    tempHandRanking[3] = self.getHighCard(h, 1, 2)
                elif (tempHandRanking == 8):
                    #P2, P2, P1
                    tempHandRanking[1] = self.getHighCard(h, 2, 1)
                    tempHandRanking[2] = self.getHighCard(h, 2, 2)
                    tempHandRanking[3] = self.getHighCard(h, 1, 1)
                elif (tempHandRanking == 9):
                    #P2, P1, P1, P1
                    tempHandRanking[1] = self.getHighCard(h, 2, 1)
                    tempHandRanking[2] = self.getHighCard(h, 1, 1)
                    tempHandRanking[3] = self.getHighCard(h, 1, 2)
                    tempHandRanking[4] = self.getHighCard(h, 1, 3)
                elif (tempHandRanking == 10):
                    #P1, P1, P1, P1, P1
                    tempHandRanking[1] = self.getHighCard(h, 1, 1)
                    tempHandRanking[2] = self.getHighCard(h, 1, 2)
                    tempHandRanking[3] = self.getHighCard(h, 1, 3)
                    tempHandRanking[4] = self.getHighCard(h, 1, 4)
                    tempHandRanking[5] = self.getHighCard(h, 1, 5)

            if (tempHandRanking[0] < self.handRanking[0]):
                #if the new hand is strictly better than the old hand, then replace the old hand
                self.handRanking = tempHandRanking
            elif (tempHandRanking[0] == self.handRanking[0]):
                #if the hands are equal in ranking, decide best by examining kickers
                newHandBetter = False
                for z in range(0, len(tempHandRanking)):
                    #should never overflow because if they have equal base values, the lengths of kicker arrays should be equal
                    if (tempHandRanking[z] < self.handRanking[z]):
                        newHandBetter = True
                #if newHandBetter is still false, then hands are either equal or old hand is better, so do not replace.
                #Otherwise, if newHandBetter is true, then the new hand should replace the old hand.
                if (newHandBetter == True):
                    self.handRanking = tempHandRanking
            elif (tempHandRanking[0] > self.handRanking[0]):
                #If the old hand is strictly better than the new hand, do nothing, stop evaluating this hand
                #We should never get to this statement
                continue
        self.bestHandCalculated = True
            
            
        
    def getStraightedness(self, incomingHand):
        #incoming hands should already be sorted if possible, but we should verify
        
        #sort the incoming hand
        #get the pairedness vector
        #for i = 0 - 10, check i through i+4. Each non empty column adds 1 to the total of that i. Return max
        straightednessVector = [0] * 10
        pairednessVector = self.getPairedness(incomingHand)
        #create an extended vector to detect straightedness A 2 3 4 5
        #add another A to the end to detect 5 4 3 2 A
        pairednessVector.append(pairednessVector[0]) #add a copy of the aces column to the end

        for i in range(0,10): #There are 10 ranges
            for j in range(0,5): #each range covers at most 5 cards
                if (pairednessVector[i+j]>0):
                    
                    straightednessVector[i]+=1 #if the pairedness is one or higher, we have this card, so increment subtotal
        handMaximumStraightedness = max(straightednessVector)
        #RETURN HERE
        return handMaximumStraightedness
        #check the straightedness
        #return Straightedness
        return -1

    def getSuitedness (self, incomingHand):
        #we should return a hisogram of suitedness
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

        pairednessVector = self.getPairedness(incomingHand)

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
            if (intAction == 1 and self.parentPlayer.playerMoney > 0):
                #print("WE WILL RAISE")
                intRaiseAmount = random.randint(1, self.parentPlayer.playerMoney)
                return PlayerAction("R", intRaiseAmount)
                #returnAction = PlayerAction("R", intRaiseAmount)
                #return returnAction
            
            elif (intAction == 2 and self.parentPlayer.playerMoney > 0):
                #print("WE WILL BET")
                intBetAmount = random.randint(1, self.parentPlayer.playerMoney)
                return PlayerAction("B", intBetAmount)

                #returnAction = PlayerAction("B", intBetAmount)
                #return returnAction
            elif (intAction == 3 and self.parentPlayer.playerMoney > 0):
                #print("WE WILL CALL")
                intCallAmount = random.randint(1, self.parentPlayer.playerMoney)
                return PlayerAction("C", intCallAmount)
                #returnAction = PlayerAction("C", intCallAmount)
                #return returnAction
            elif (intAction == 4):
                #print ("WE WILL FOLD")
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
        #print("We did something")
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

            #if the player raises all their money, they shoved and are all in
                if (incPlayer.playerMoney == incAction.actAmt):
                    incPlayer.allIn = True
                
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

                #if this bet is all the player's money, then they are all in
                if (incPlayer.playerMoney == incAction.actAmt):
                    incPlayer.allIn = True
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
    #define a list to store the current players (each game has a unique set of players)
    listOfPlayers = []
    #set player loop (1 to 8, if not specified, pick at random)
    for u in range(0, 8):
        print("I have set player " + str(u))
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


        def collectBets():
            # 1) Loop through players and get actions until allBetsEqual
            #start at (currentDealer+3)%numCurPlayers and loop asking for actions.
            for q in range(0, numCurPlayers):
                #print("Get the action from player and update gamestate")
                #standinForGamestate = []
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
                    #DEBUGTEXT
                    #print("Player action skipped because player all in or out of game")
                    continue


        collectBets()
##        # 1) Loop through players and get actions until allBetsEqual
##        #start at (currentDealer+3)%numCurPlayers and loop asking for actions.
##        for q in range(0, numCurPlayers):
##            print("Get the action from player and update gamestate")
##            #standinForGamestate = []
##            if ((currentGame.listOfPlayers[q].inactive == False) and (currentGame.listOfPlayers[q].allIn == False)):
##                #newPlayerAction = p.currentAI.returnAction(standinForGamestate)
##                #ask for the action, give current gamestate including cards, pot size, bets, stack sizes, etc.
##                #newPlayerAction = currentGame.listOfPlayers[(q+currentGame.currentDealer+3)%numCurPlayers].currentAI.returnAction(standinForGamestate)
##                newPlayerAction = currentGame.listOfPlayers[(q+currentGame.currentDealer+3)%numCurPlayers].currentAI.returnAction() 
##                #print("Implement the action from the player")
##                currentPlayer = currentGame.listOfPlayers[(q+currentGame.currentDealer+3)%numCurPlayers]
##                #implement the action in the game engine // If the action is invalid, the player folds
##                currentGame.implementAction(newPlayerAction, currentPlayer, currentGame.listOfPlayers.index(currentPlayer))
##                #this updates the gamestate for the next player before it loops
##            else:
##                #DEBUGTEXT
##                print("Player action skipped because player all in or out of game")
##                continue
        #now that we have looped through all players, we should then check if all players who are not inactive or all-in
        #have made the same bet. If they have not, then we should repeat the betting round until such time as they have.
            
                

            
        #flop revealed // Draw three cards
        for f in range(0,3):
            currentGame.currentRound.communityCards.append(currentGame.currentRound.deck.drawACard())
        currentGame.currentRound.resetBets()
        #DEBUGTEXT
        #currentGame.currentRound.printCommunityCards()

        collectBets()
##        # Repeat 1
##        # 1) Loop through players and get actions until allBetsEqual
##        #start at (currentDealer+3)%numCurPlayers and loop asking for actions.
##        for q in range(0, numCurPlayers):
##            print("Get the action from player and update gamestate")
##            #standinForGamestate = []
##            if ((currentGame.listOfPlayers[q].inactive == False) and (currentGame.listOfPlayers[q].allIn == False)):
##                #newPlayerAction = p.currentAI.returnAction(standinForGamestate)
##                #ask for the action, give current gamestate including cards, pot size, bets, stack sizes, etc.
##                #newPlayerAction = currentGame.listOfPlayers[(q+currentGame.currentDealer+3)%numCurPlayers].currentAI.returnAction(standinForGamestate)
##                newPlayerAction = currentGame.listOfPlayers[(q+currentGame.currentDealer+3)%numCurPlayers].currentAI.returnAction() 
##                #print("Implement the action from the player")
##                currentPlayer = currentGame.listOfPlayers[(q+currentGame.currentDealer+3)%numCurPlayers]
##                #implement the action in the game engine // If the action is invalid, the player folds
##                currentGame.implementAction(newPlayerAction, currentPlayer, currentGame.listOfPlayers.index(currentPlayer))
##                #this updates the gamestate for the next player before it loops
##            else:
##                #DEBUGTEXT
##                print("Player action skipped because player all in or out of game")
##                continue

        # Turn revealed
        currentGame.currentRound.communityCards.append(currentGame.currentRound.deck.drawACard())
        currentGame.currentRound.resetBets()
        #DEBUGTEXT
        #currentGame.currentRound.printCommunityCards()

        collectBets()
##        # repeat 1
##        # 1) Loop through players and get actions until allBetsEqual
##        #start at (currentDealer+3)%numCurPlayers and loop asking for actions.
##        for q in range(0, numCurPlayers):
##            print("Get the action from player and update gamestate")
##            #standinForGamestate = []
##            if ((currentGame.listOfPlayers[q].inactive == False) and (currentGame.listOfPlayers[q].allIn == False)):
##                #newPlayerAction = p.currentAI.returnAction(standinForGamestate)
##                #ask for the action, give current gamestate including cards, pot size, bets, stack sizes, etc.
##                #newPlayerAction = currentGame.listOfPlayers[(q+currentGame.currentDealer+3)%numCurPlayers].currentAI.returnAction(standinForGamestate)
##                newPlayerAction = currentGame.listOfPlayers[(q+currentGame.currentDealer+3)%numCurPlayers].currentAI.returnAction() 
##                #print("Implement the action from the player")
##                currentPlayer = currentGame.listOfPlayers[(q+currentGame.currentDealer+3)%numCurPlayers]
##                #implement the action in the game engine // If the action is invalid, the player folds
##                currentGame.implementAction(newPlayerAction, currentPlayer, currentGame.listOfPlayers.index(currentPlayer))
##                #this updates the gamestate for the next player before it loops
##            else:
##                #DEBUGTEXT
##                print("Player action skipped because player all in or out of game")
##                continue

        # river revealed
        currentGame.currentRound.communityCards.append(currentGame.currentRound.deck.drawACard())
        currentGame.currentRound.resetBets()
        #DEBUGTEXT
        #currentGame.currentRound.printCommunityCards()

        #collect new betting round.
        collectBets()

##        #repeat 1
##                # 1) Loop through players and get actions until allBetsEqual
##        #start at (currentDealer+3)%numCurPlayers and loop asking for actions.
##        for q in range(0, numCurPlayers):
##            print("Get the action from player and update gamestate")
##            #standinForGamestate = []
##            if ((currentGame.listOfPlayers[q].inactive == False) and (currentGame.listOfPlayers[q].allIn == False)):
##                #newPlayerAction = p.currentAI.returnAction(standinForGamestate)
##                #ask for the action, give current gamestate including cards, pot size, bets, stack sizes, etc.
##                #newPlayerAction = currentGame.listOfPlayers[(q+currentGame.currentDealer+3)%numCurPlayers].currentAI.returnAction(standinForGamestate)
##                newPlayerAction = currentGame.listOfPlayers[(q+currentGame.currentDealer+3)%numCurPlayers].currentAI.returnAction() 
##                #print("Implement the action from the player")
##                currentPlayer = currentGame.listOfPlayers[(q+currentGame.currentDealer+3)%numCurPlayers]
##                #implement the action in the game engine // If the action is invalid, the player folds
##                currentGame.implementAction(newPlayerAction, currentPlayer, currentGame.listOfPlayers.index(currentPlayer))
##                #this updates the gamestate for the next player before it loops
##            else:
##                #DEBUGTEXT
##                print("Player action skipped because player all in or out of game")
##                continue
            
        #resolve round + award money
        #This should be the code that evaluates the strength of each player's hand, awards money to winner
        #Assign all players a reward equal to the amount of money they won - the amount of money they bet
        currentHighestRank = -1
        currentWinner = []
        currentWinner.append(-1)
        for w in range(0, len(currentGame.listOfPlayers)):
            if (currentGame.listOfPlayers[w].inactive == False):
                #if the player is in the hand and hasn't folded

                if (currentGame.listOfPlayers[w].bestHandCalculated == False):
                    #if the hand has never been calculated, calculate it, passing in the current community cards
                    currentGame.listOfPlayers[w].returnBestHand(currentGame.currentRound.communityCards)
                    
                if (currentWinner[0] == -1):
                    #if this is the first hand looked at, it's by default the highest so far
                    currentWinner[0] = w
                #else compare the hands
                elif (currentGame.listOfPlayers[w].handRanking[0] < currentGame.listOfPlayers[currentWinner[0]].handRanking[0]):
                    #if the current player's hand is strictly better than the old best hand, replace the old best hand
                    currentWinner[0] = w
                elif (currentGame.listOfPlayers[w].handRanking[0] == currentGame.listOfPlayers[currentWinner[0]].handRanking[0]):
                    #if the base hand scores of each player are exactly the same then iterate through kicker arrays to find winner
                    tieDetected = True
                    for k in range(0, len(currentGame.listOfPlayers[w].handRanking)):
                        #lengths should be the same since main value is the same
                        if (currentGame.listOfPlayers[currentWinner[0]].handRanking[k] < currentGame.listOfPlayers[w].handRanking[k]):
                            #if the current winner beats the new hand on any tiebreaker, then we continue, because the old hand wins
                            #print("old hand wins")
                            tieDetected = False
                            pass
                        elif (currentGame.listOfPlayers[currentWinner[0]].handRanking[k] > currentGame.listOfPlayers[w].handRanking[k]):
                            #if the new hand wins, then we replace the old hand
                            currentWinner[0] = w
                            tieDetected = False
                            #continue
                        
                            
                    #if we made it through the loop and didn't break the tie, then they are tied, so they split the pot.
                    if (tieDetected == True):
                        currentWinner.append(w)
                    
                            
                        
                    #Else if the main rankings are a tie, iterate through the kicker arrays to find winner.
                    
                    


                #Add the pot to the money of whichever player has the highest.
                numWinners = len(currentWinner)
                perPlayerPot = currentGame.currentRound.currentPot // numWinners
                for y in currentWinner:
                    #give the split pot to all players splitting it
                    currentGame.listOfPlayers[y].playerMoney += perPlayerPot

                print("Round resolved!")
                


        #set all players to not inactive and not all in
        #If a player has no more money left, remove them from the list of players for this game
        for p in currentGame.listOfPlayers:
            p.inactive = False
            p.allIn = False
            if (p.playerMoney <= 0):
                #remove them for the remainder of rounds, (they will be added back into the next game)
                currentGame.listOfPlayers.remove(p)
        print("Current Game's list of players length: " + str(len(currentGame.listOfPlayers)))
        
        #If only one player left in the list of players, break out of the loop and end the game
        if (len(currentGame.listOfPlayers) == 1):
            print("Game over with one player having all the money!")
            #we have arrived at a winner, they have all the chips! No need to play more rounds, break out of the loop!
            break
        print("J is: " + str(j))
        if (j == (numRoundsPerGame-1)):
            #print the list of players and their money.
            outputString = ""
            for player in currentGame.listOfPlayers:
                outputString = (outputString +"Player X finishes the rounds with: $")
                outputString = (outputString + str(player.playerMoney))

            print(outputString)
        #last part of resolving is to increment the dealer
        currentGame.currentDealer = (currentGame.currentDealer + 1)%numCurPlayers

    
    #HERE IS THE END OF THIS GAME
    #There should be some code here to collect the final state of the game, such as the amount of money held by each player (could be 80,000 by 1, 0 by the rest, etc)
    #INSERT SOME CODE TO DELETE THE CURRENT GAME
