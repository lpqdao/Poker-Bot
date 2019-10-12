import random
import itertools
import time
import numpy
import threading
import multiprocessing
from multiprocessing import Process
#from multiprocessing import shared_memory
import os



def runPokerTable(self, incNumberOfGames, incSharedMemoryName, incSharedEpsilon):
    #connect to existing shared memory
    # newSharedMemoryBlock = shared_memory.SharedMemory(name=incSharedMemoryName)
    #
    # incNumpyArray = numpy.ndarray((4,5), dtype=int, buffer=newSharedMemoryBlock.buf)
    # print(incNumpyArray)
    # incNumpyArray[2,2] = 444
    # print(incNumpyArray)

    #newSharedMemoryBlock = shared_memory.SharedMemory(name=incSharedMemoryName)
    #newSharedEpsilonBlock = shared_memory.SharedMemory(name=incSharedEpsilon)

    #incNumpyArray = numpy.ndarray((4, 5, 5, 7, 4, 5, 10, 9, 14), dtype=numpy.double, buffer=newSharedMemoryBlock.buf)
    #incEpsilonArray = numpy.ndarray((1), dtype=numpy.double, buffer=newSharedEpsilonBlock.buf)

    #print("The shared epsilon should be readable now and it has a value of: " + str(incEpsilonArray[0]))
    #print(incNumpyArray[2, 2])

    #print(newSharedMemoryBlock)
    #newSharedMemoryBlock[2,2] = 444


    class QlearningStateObject:
        #This state object contains the values for each of the dimensions that we use for state comparisons, which are as such:
        # * Max Pairedness (4 states: 1, 2, 3, 4)
        # * Max Suitedness (5 states: 1, 2, 3, 4, 5)
        # * Max Straightedness (5 states: 1, 2, 3, 4, 5)
        # * Pot odds = CurrentMaxBet/CurrentPot (7 states: >0.05, >0.10, >0.25, >0.50, >1.00, >2.00, >4.00)
        # * Gamestage (4 states: Preflop, Flop, Turn, River)
        # * Position (5 states: Dealer, Dealer+1, Dealer+2, Dealer+3, Dealer+4-7)
        # * HandStrength, lower=better (10 states: 0, 1, 2, 3, 4, 5, 6, 7, 8, 9)
        # * %ofTotalMoneyHeld (9 states: <10%, >10%, >15%, >25%, >40%, >60%, >75%, >90%, 100%

        # For each state there are several possible actions
        # * Fold (player folds immediately and is removed from the hand) (One Action: F)
        # * Raise (there are six types of raises) (Six Actions: R0, R1, R2, R3, R4, R5)
        # * Bet (there are seven types of bets) (Seven Actions: B0, B1, B2, B3, B4, B5, B6)
        # All other actions, such as checking, can be considered one of the other actions. For example, checking is the same as betting 0 into a max bet of 0.
        # In the (s,a) array they will be laid out in the order of [F, R0, R1, R2, R3, R4, R5, B0, B1, B2, B3, B4, B5, B6]

        def __init__(self, incD0, incD1, incD2, incD3, incD4, incD5, incD6, incD7):
            self.dim0 = incD0 #pairedness state
            self.dim1 = incD1 #suitedness state
            self.dim2 = incD2 #straightedness state
            self.dim3 = incD3 #pot odds state
            self.dim4 = incD4 #gamestage state
            self.dim5 = incD5 #position state
            self.dim6 = incD6 #hand strength state
            self.dim7 = incD7 #%moneyheld state

        def getDim0(self):
            return self.dim0



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
            self.playerName = ("Random Player " +str(random.randint(0,10000))) # So we can identify the player
            self.gamestate = None
            self.lastPlayerMoney = 0
            self.oldStates = []
            self.oldActions = []

        def addOldState(self, incOldGameState, incOldActionTaken):
            #used for memory since we do not get reward back immediately. There should be no more than four states and actions pushed to this array every game (one for each betting round the player was a part of)
            self.oldStates.append(incOldGameState)
            self.oldActions.append(incOldActionTaken)
            # self.oldStates.append(QlearningStateObject(incOldGameState.getDim0, incOldGameState.dim1, incOldGameState.dim2, incOldGameState.dim3, incOldGameState.dim4, incOldGameState.dim5, incOldGameState.dim6, incOldGameState.dim7))
            # self.oldActions.append(incOldActionTaken)

        def setAI(self):
            print("Someone should have set the AI")

        def constructGamestate(self, incPotOdds, incGamestage, incPlayerPosition, incCommCards):
            #DEBUGTEXT
            #print("Constructing the gamestate for player: " + self.playerName)
            self.copyOfCommCards = incCommCards.copy()
            self.fullCards = incCommCards
            for p in self.holeCards:
                self.fullCards.append(p)
            #get max pairedness for D0
            maxPairedness =  max(self.getPairedness(self.fullCards))
            newDim0 = maxPairedness-1

            #get max suitedness for D1
            maxSuitedness = max(self.getSuitedness(self.fullCards))
            # if (maxSuitedness > 5):
            #     print("Uh OH, HOW DID WE GET SUITEDNESS OF MORE THAN 5? It is: " + str(maxSuitedness))
            # it's because sometimes we check suitedness of more than 5 cards, so we could get a 6 or 7 card flush.
            if (maxSuitedness >= 5):
                maxSuitedness = 4
            newDim1 = maxSuitedness

            #get max straightedness for D2
            maxStraightedness = self.getStraightedness(self.fullCards)
            newDim2 = maxStraightedness-1

            #get pot odds for D3
            maxPotOdds = incPotOdds
            newDim3 = 0
            # * Pot odds = CurrentMaxBet/CurrentPot (7 states: <0.10, >0.10, >0.25, >0.50, >1.00, >2.00, >4.00)

            if (maxPotOdds < 0.10):
                newDim3 = 0
            elif (maxPotOdds > 0.1):
                newDim3 = 1
            elif (maxPotOdds > 0.25):
                newDim3 = 2
            elif (maxPotOdds > 0.5):
                newDim3 = 3
            elif (maxPotOdds > 1.0):
                newDim3 = 4
            elif (maxPotOdds > 2.0):
                newDim3 = 5
            else:
                newDim6 = 6

            #get gamestage for D4
            curGamestate = incGamestage
            newDim4 = curGamestate

            #get player position for D5
            curPlayPosition = incPlayerPosition
            newDim5 = 0
            if (curPlayPosition <= 3): #if we're in position 0 to 3, we're in that state
                newDim5 = curPlayPosition
            else:
                newDim5 = 4 #if we're in any other position, we're in state 4


            #get hand strength for dimension D6
            self.returnBestHand(self.copyOfCommCards) #cal current best hand ranking
            curHandStrength = self.handRanking[0]-1 #set primary rank as vector value
            newDim6 = curHandStrength

            #get percentage money held for state D7
            playerMoneyPercentage = self.playerMoney / 80000
            percentState = 0
            if (playerMoneyPercentage <0.1):
                percentState = 0
            elif (playerMoneyPercentage == 1):
                percentState = 8
            elif (playerMoneyPercentage > 0.9):
                percentState = 7
            elif (playerMoneyPercentage > 0.75):
                percentState = 6
            elif (playerMoneyPercentage > 0.6):
                percentState = 5
            elif (playerMoneyPercentage > 0.4):
                percentState = 4
            elif (playerMoneyPercentage > 0.25):
                percentState = 3
            elif (playerMoneyPercentage > 0.15):
                percentState = 2
            elif (playerMoneyPercentage > 0.1):
                percentState = 1
            newDim7 = percentState
            newGamestate = QlearningStateObject(newDim0, newDim1, newDim2, newDim3, newDim4, newDim5, newDim6, newDim7)

            #here we return the actual gamestate object we have constructed
            return newGamestate

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
            self.allCards = []
            self.allCards[:] = []
            self.allCards = arrayOfCommunityCards.copy()
            #DEBUGTEXT
            #print(len(self.allCards))
            #self.allCards = arrayOfCommunityCards
            for p in self.holeCards:
                self.allCards.append(p)
            #DEBUGTEXT
            #print(len(self.allCards))

            #returns all possible combinations of 5 cards from the seven available.
            if (len(self.allCards) >= 5):
                #aka we have seen at least the flop
                possibleHands = list(itertools.combinations(self.allCards, 5))
            else:
                #AKA if we still have only the hole cards, then there is only one possible combination of those two
                possibleHands = list(itertools.combinations(self.allCards, 2))

            tempHandRanking = [1000] * 6
            #DEBUGTEXT
            # if (len(possibleHands) > 21):
            #     print("WARNING! THERE ARE TOO MANY POSSIBLE HANDS!: " + str(len(possibleHands)))

            for h in possibleHands:
                #for each hand that is possibly the best, evaluate it and give it a ranking
                #print("Hand Length is: " + str(len(h)))
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
                # suitednessHistogram = [0] * 4
                # for x in listHandSuitedness:
                #     if x == 1:
                #         suitednessHistogram[3]+=1
                #     elif x == 2:
                #         suitednessHistogram[2] += 1
                #     elif x == 3:
                #         suitednessHistogram[1] += 1
                #     elif x == 4:
                #         suitednessHistogram[0] += 1
                pairednessHistogram = [0] * 4
                for x in listHandPairedness:
                    if x == 1:
                        pairednessHistogram[3]+=1
                    elif x == 2:
                        pairednessHistogram[2] += 1
                    elif x == 3:
                        pairednessHistogram[1] += 1
                    elif x == 4:
                        pairednessHistogram[0] += 1
                if pairednessHistogram[2] == 1:
                    #if there is exactly one pair, set the 4th bit
                    intHandValue += 8
                if pairednessHistogram[1]==1:
                    #if there is exactly one triplet, set the third bit
                    intHandValue += 4
                if pairednessHistogram[0]==1:
                    #if exactly one quad, set the second bit
                    intHandValue+=2
                if pairednessHistogram[3]==1:
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


            #DEBUGTEXT
            # incHandLength = len(incomingHand)
            # if (incHandLength > 5):
            #     print("WARNING! SUITEDNESS HAND LENGTH IS: " + str(incHandLength) + " in game: " + str(j))


            for h in incomingHand:
                if (h.suit=="S"):
                    suitednessVector[0]+=1
                elif (h.suit=="C"):
                    suitednessVector[1]+=1
                elif (h.suit == "D"):
                    suitednessVector[2] += 1
                elif (h.suit == "H"):
                    suitednessVector[3] += 1

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
        def returnAction(self, incGamestate):
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
                    #intRaiseAmount = random.randint(1, self.parentPlayer.playerMoney+1)
                    #What type of raise will it be?
                    strSubRaiseType = ""
                    intRaiseType = random.randint(0, 5)

                    if (intRaiseType == 0):
                        strSubRaiseType = "R0"
                    elif (intRaiseType == 1):
                        strSubRaiseType = "R1"
                    elif(intRaiseType == 2):
                        strSubRaiseType = "R2"
                    elif (intRaiseType == 3):
                        strSubRaiseType = "R3"
                    elif (intRaiseType == 4):
                        strSubRaiseType = "R4"
                    elif (intRaiseType == 5):
                        strSubRaiseType = "R5"
                    else:
                        strSubRaiseType = "R0"

                    return PlayerAction("R", 0, strSubRaiseType)
                    #returnAction = PlayerAction("R", intRaiseAmount)
                    #return returnAction

                elif (intAction == 2 and self.parentPlayer.playerMoney > 0):
                    #print("WE WILL BET")
                    #intBetAmount = random.randint(1, self.parentPlayer.playerMoney+1)

                    strSubBetType = ""
                    intBetType = random.randint(0, 7)

                    if (intBetType == 0):
                        strSubRaiseType = "B00"
                    elif (intBetType == 1):
                        strSubRaiseType = "B05"
                    elif(intBetType == 2):
                        strSubRaiseType = "B10"
                    elif (intBetType == 3):
                        strSubRaiseType = "B20"
                    elif (intBetType == 4):
                        strSubRaiseType = "B50"
                    elif (intBetType == 5):
                        strSubRaiseType = "BHP"
                    elif (intBetType == 6):
                        strSubRaiseType = "BFP"
                    else:
                        strSubRaiseType = "B0"


                    return PlayerAction("B", 0, strSubBetType)

                    #returnAction = PlayerAction("B", intBetAmount)
                    #return returnAction
                elif (intAction == 3 and self.parentPlayer.playerMoney > 0):
                    #print("WE WILL CALL")
                    intCallAmount = random.randint(1, self.parentPlayer.playerMoney+1)
                    #return PlayerAction("C", intCallAmount)
                    return PlayerAction("B", 0, "B00") # This returns a min bet, also known as a call, but it will fold if the bet cannot be made
                    #returnAction = PlayerAction("C", intCallAmount)
                    #return returnAction
                elif (intAction == 4):
                    #print ("WE WILL FOLD")
                    return PlayerAction("F", 0, "F")
                    #returnAction = PlayerAction("F", 0)
                    #return returnAction
                else:
                    return PlayerAction("F", 0, "F")
            elif (self.name == "Player"):
                #INSERT PLAYER CODE ACTIONS @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
                #for now we just fold, because we have nothing
                returnAction = PlayerAction("F", 0, "F")

                #playerEpsilon = 0.9
                #playerEpsilon = incEpsilonArray[0]


                #player epsilon should be global and in shared memory as a double
                #it should start at 1, meaning we explore 100% of the time (pick randomly)
                #every updated state should decrease epsilon by 0.0000095 such that after 100,000 state visits, it is at 5% exploration rate
                #do not go below 5% exploration rate

                #generate a random double between 0 and 1.
                #If the number is larger than epsilon, then we pick the greedy move, otherwise we pick a random move



                # This is the state we are in
                self.dim0 = incGamestate.dim0
                self.dim1 = incGamestate.dim1
                self.dim2 = incGamestate.dim2
                self.dim3 = incGamestate.dim3
                self.dim4 = incGamestate.dim4
                self.dim5 = incGamestate.dim5
                self.dim6 = incGamestate.dim6
                self.dim7 = incGamestate.dim7

                dim8Width = 14
                self.dim8 = 0


                self.epsilonTest = random.random()  # generate random float between 0 and 1

                self.intActionWeWillTake = 0 #this by default folds if we don't change it

                #DEBUGTEST
                #print("Epsilon test/Epsilon = " + str(self.epsilonTest) + "\\" + str(playerEpsilon))
                if (self.epsilonTest > playerEpsilon):
                    #print("WE DO THE GREEDY ACTION")
                    # HERE WE DO THE GREEDY ACTION!
                    # In the (s,a) array they will be laid out in the order of [F, R0, R1, R2, R3, R4, R5, B0, B1, B2, B3, B4, B5, B6]
                    actionWithMaxValue = 0
                    maxValueFound = 0.00
                    for sa in range(0, dim8Width):
                        if (incNumpyArray[self.dim0, self.dim1, self.dim2, self.dim3, self.dim4, self.dim5, self.dim6, self.dim7, sa] > maxValueFound):
                            actionWithMaxValue = sa
                            maxValueFound = incNumpyArray[self.dim0, self.dim1, self.dim2, self.dim3, self.dim4, self.dim5, self.dim6, self.dim7, sa]
                    self.intActionWeWillTake = actionWithMaxValue

                else:
                    #print("WE EXPLORE WITH A RANDOM ACTION!")
                    self.intActionWeWillTake = random.randint(0,14)


                #NOW WE ACTUALLY RETURN THE APPROPRIATE ACTION
                if (self.intActionWeWillTake == 0):
                    # print("We do the action")
                    return PlayerAction("F", 0, "F")
                elif (self.intActionWeWillTake == 1):
                    #print("WE DO THE ACTION")
                    return PlayerAction("R", 0, "R0")
                elif (self.intActionWeWillTake == 2):
                    #print("WE DO THE ACTION")
                    return PlayerAction("R", 0, "R1")
                elif (self.intActionWeWillTake == 3):
                    #print("WE DO THE ACTION")
                    return PlayerAction("R", 0, "R2")
                elif (self.intActionWeWillTake == 4):
                    #print("WE DO THE ACTION")
                    return PlayerAction("R", 0, "R3")
                elif (self.intActionWeWillTake == 5):
                    #print("WE DO THE ACTION")
                    return PlayerAction("R", 0, "R4")
                elif (self.intActionWeWillTake == 6):
                    #print("WE DO THE ACTION")
                    return PlayerAction("R", 0, "R5")
                elif (self.intActionWeWillTake == 7):
                    #print("WE DO THE ACTION")
                    return PlayerAction("B", 0, "B00")
                elif (self.intActionWeWillTake == 8):
                    #print("WE DO THE ACTION")
                    return PlayerAction("B", 0, "B05")
                elif (self.intActionWeWillTake == 9):
                    #print("WE DO THE ACTION")
                    return PlayerAction("B", 0, "B10")
                elif (self.intActionWeWillTake == 10):
                    #print("WE DO THE ACTION")
                    return PlayerAction("B", 0, "B20")
                elif (self.intActionWeWillTake == 11):
                    #print("WE DO THE ACTION")
                    return PlayerAction("B", 0, "B50")
                elif (self.intActionWeWillTake == 12):
                    #print("WE DO THE ACTION")
                    return PlayerAction("B", 0, "BHP")
                elif (self.intActionWeWillTake == 13):
                    #print("WE DO THE ACTION")
                    return PlayerAction("B", 0, "BFP")



                #Check the state that we are in,


                return returnAction

                #INSERT PLAYER CODE ACTIONS @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
            elif (self.name == "Grace-Player"):
                #INSERT PLAYER CODE ACTIONS @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
                #for now we just fold, because we have nothing
                returnAction = PlayerAction("F", 0, "F")

                playerEpsilon = 0.9
                playerEpsilon = incEpsilonArray[0]


                #player epsilon should be global and in shared memory as a double
                #it should start at 1, meaning we explore 100% of the time (pick randomly)
                #every updated state should decrease epsilon by 0.0000095 such that after 100,000 state visits, it is at 5% exploration rate
                #do not go below 5% exploration rate

                #generate a random double between 0 and 1.
                #If the number is larger than epsilon, then we pick the greedy move, otherwise we pick a random move



                # This is the state we are in
                self.dim0 = incGamestate.dim0
                self.dim1 = incGamestate.dim1
                self.dim2 = incGamestate.dim2
                self.dim3 = incGamestate.dim3
                self.dim4 = incGamestate.dim4
                self.dim5 = incGamestate.dim5
                self.dim6 = incGamestate.dim6
                self.dim7 = incGamestate.dim7

                #dim8Width = 14
                dim8Width=0
                self.dim8 = 0


                self.epsilonTest = random.random()  # generate random float between 0 and 1

                self.intActionWeWillTake = 0 #this by default folds if we don't change it

                #DEBUGTEST
                #print("Epsilon test/Epsilon = " + str(self.epsilonTest) + "\\" + str(playerEpsilon))
                if (self.epsilonTest > playerEpsilon):
                    #print("WE DO THE GREEDY ACTION")
                    # HERE WE DO THE GREEDY ACTION!
                    # In the (s,a) array they will be laid out in the order of [F, R0, R1, R2, R3, R4, R5, B0, B1, B2, B3, B4, B5, B6]
                    actionWithMaxValue = 0
                    maxValueFound = 0.00
                    for sa in range(0, dim8Width):
                        actionWithMaxValue=sa
                        #if (incNumpyArray[self.dim0, self.dim1, self.dim2, self.dim3, self.dim4, self.dim5, self.dim6, self.dim7, sa] > maxValueFound):
                            #actionWithMaxValue = sa
                    maxValueFound = incNumpyArray[self.dim0, self.dim1, self.dim2, self.dim3, self.dim4, self.dim5, self.dim6, self.dim7, sa]
                    self.intActionWeWillTake = actionWithMaxValue

                else:
                    #print("WE EXPLORE WITH A RANDOM ACTION!")
                    self.intActionWeWillTake = random.randint(0,14)


                #NOW WE ACTUALLY RETURN THE APPROPRIATE ACTION
                if (self.intActionWeWillTake == 0):
                    # print("We do the action")
                    return PlayerAction("F", 0, "F")
                elif (self.intActionWeWillTake == 1):
                    #print("WE DO THE ACTION")
                    return PlayerAction("R", 0, "R0")
                elif (self.intActionWeWillTake == 2):
                    #print("WE DO THE ACTION")
                    return PlayerAction("R", 0, "R1")
                elif (self.intActionWeWillTake == 3):
                    #print("WE DO THE ACTION")
                    return PlayerAction("R", 0, "R2")
                elif (self.intActionWeWillTake == 4):
                    #print("WE DO THE ACTION")
                    return PlayerAction("R", 0, "R3")
                elif (self.intActionWeWillTake == 5):
                    #print("WE DO THE ACTION")
                    return PlayerAction("R", 0, "R4")
                elif (self.intActionWeWillTake == 6):
                    #print("WE DO THE ACTION")
                    return PlayerAction("R", 0, "R5")
                elif (self.intActionWeWillTake == 7):
                    #print("WE DO THE ACTION")
                    return PlayerAction("B", 0, "B00")
                elif (self.intActionWeWillTake == 8):
                    #print("WE DO THE ACTION")
                    return PlayerAction("B", 0, "B05")
                elif (self.intActionWeWillTake == 9):
                    #print("WE DO THE ACTION")
                    return PlayerAction("B", 0, "B10")
                elif (self.intActionWeWillTake == 10):
                    #print("WE DO THE ACTION")
                    return PlayerAction("B", 0, "B20")
                elif (self.intActionWeWillTake == 11):
                    #print("WE DO THE ACTION")
                    return PlayerAction("B", 0, "B50")
                elif (self.intActionWeWillTake == 12):
                    #print("WE DO THE ACTION")
                    return PlayerAction("B", 0, "BHP")
                elif (self.intActionWeWillTake == 13):
                    #print("WE DO THE ACTION")
                    return PlayerAction("B", 0, "BFP")



                #Check the state that we are in,


                return returnAction

                #INSERT PLAYER CODE ACTIONS @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


            else:
                #DO RANDOM ACTIONS
                #returnAction = PlayerAction("F", 0)
                #return returnAction
                return PlayerAction("F", 0, "F")


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
            self.smallBlind = 10
            self.bigBlind = 2 * self.smallBlind
            self.currentDealer = 0
            self.listOfPlayers = incListOfPlayers
            self.roundPlayerBets = [0] * 8
            self.currentRound = Round()

        def setNewRound(self, incRound):
            del(self.currentRound)
            self.currentRound = None
            self.currentRound = incRound

        def implementAction(self, incAction, incPlayer, incPlayerIndex):
            #print("We did something")
            incAct = incAction.actAction
            newSubAct = incAction.actSub
            if (incAct == "R"):
                #player will raise, check how much
                intPlayerRaiseAmount = 0
                if (newSubAct == "R0"):
                    #We have a min raise, so raise by 2x currentMaxBet, bet cannot be 0.
                    intPlayerRaiseAmount = max(((self.currentRound.maximumBet)*2), (self.bigBlind * 2))
                elif (newSubAct == "R1"):
                    #The new raise is 2x min raise
                    intPlayerRaiseAmount = max(((self.currentRound.maximumBet)*4), (self.bigBlind * 2))
                elif (newSubAct == "R2"):
                    #The new raise is 4x min raise
                    intPlayerRaiseAmount = max(((self.currentRound.maximumBet)*8), (self.bigBlind * 2))
                elif (newSubAct == "R3"):
                    #the new raise is 8x min raise
                    intPlayerRaiseAmount = max(((self.currentRound.maximumBet)*16), (self.bigBlind * 2))
                elif (newSubAct == "R4"):
                    #The new raise is all in! Player shoves!
                    intPlayerRaiseAmount = self.listOfPlayers[incPlayerIndex].playerMoney
                else:
                        # We have a nonspecific raise, which are always min raises
                        intPlayerRaiseAmount = max(((self.currentRound.maximumBet)*2), (self.bigBlind * 2))

                if (self.listOfPlayers[incPlayerIndex].playerMoney >= intPlayerRaiseAmount): #Check to see if the player has enough money
                    #print("Player " + str(incPlayerIndex+1) + "\\" + str(len(listOfPlayers)) + " has $" + str(incPlayer.playerMoney) + " and is wagering $" + str(intPlayerRaiseAmount))
                    #if player raised (like from 200 to 500) deduct what they currently have in pot and add total amount (they added +300)
                    #self.currentRound.currentPot += incAction.actAmt - self.currentRound.tempPlayerBets[incPlayerIndex]

                    #DEBUG
                    #if (intPlayerRaiseAmount > 80000):
                        #print("WARNING! LINE 514! PLAYER RAISING OVER 80k! IN GAME: " + str(i) + " AND ROUND: " + str(j))
                    self.currentRound.currentPot += intPlayerRaiseAmount #If I have enough money, put it in the pot
                    #DEBUGTEXT
                    #print("The pot is increased by: $" + str(intPlayerRaiseAmount))
                    #player's money is incremented by previous bet amount minus new raised amount (should be negative)

                    #Change the player's money
                    #self.listOfPlayers[incPlayerIndex].playerMoney += (self.currentRound.tempPlayerBets[incPlayerIndex] - incAction.actAmt)
                    #DEBUG
                    #if (intPlayerRaiseAmount < 0):
                        #print("WARNING! LINE 524! PLAYER RAISING NEGATIVE AMOUNT!")
                    self.listOfPlayers[incPlayerIndex].playerMoney -= intPlayerRaiseAmount
                    #DEBUGTEXT
                    #print("Player's money is increased by: $" + str(self.currentRound.tempPlayerBets[incPlayerIndex]) + " - $" + str(incAction.actAmt) + " for a total of: " + str(self.currentRound.tempPlayerBets[incPlayerIndex] - incAction.actAmt))
                    #replace what they bet with their new maximum bet
                    self.currentRound.tempPlayerBets[incPlayerIndex] = intPlayerRaiseAmount
                    self.currentRound.maximumBet = intPlayerRaiseAmount

                else:
                    #the player didn't have enough money for their action, action invalid, they fold.
                    #player is inactive for the remainder of the round
                    #DEBUGTEXT
                    #print("Player tried to raise with insufficient funds and is folded.")
                    #print("ILLEGAL RAISE, PLAYER FOLDED")

                    self.listOfPlayers[incPlayerIndex].inactive = True
                    #player no longer has any bet standing in this hand
                    self.currentRound.tempPlayerBets[incPlayerIndex] = 0;

                #if the player raises all their money, they shoved and are all in
                if (self.listOfPlayers[incPlayerIndex].playerMoney == 0):
                    self.listOfPlayers[incPlayerIndex].allIn = True

            elif (incAct == "B"):
                intPlayerBetAmount = 0
                if (newSubAct == "B00"):
                    # We have a min bet, so bet the current bet, even if it is 0.
                    intPlayerBetAmount = (self.currentRound.maximumBet) * 1
                elif (newSubAct == "B05"):
                    # The new bet is 5% of the player's money to lowest integer
                    intPlayerBetAmount = (self.listOfPlayers[incPlayerIndex].playerMoney) // 0.05
                elif (newSubAct == "B10"):
                    # The new bet is 10% of the player's money to lowest integer
                    intPlayerBetAmount = (self.listOfPlayers[incPlayerIndex].playerMoney) // 0.10
                elif (newSubAct == "B20"):
                    # The new bet is 20% of the player's money to lowest integer
                    intPlayerBetAmount = (self.listOfPlayers[incPlayerIndex].playerMoney) // 0.20
                elif (newSubAct == "B50"):
                    # The new bet is 50% of the player's money to lowest integer
                    intPlayerBetAmount = (self.listOfPlayers[incPlayerIndex].playerMoney) // 0.50
                elif (newSubAct == "BHP"):
                    # The new bet is 50% of the current pot
                    intPlayerBetAmount = (self.currentRound.currentPot) // 2
                elif (newSubAct == "BFP"):
                    # The new bet is 100% of the current pot
                    intPlayerBetAmount = (self.currentRound.currentPot)
                else:
                    #min bet
                    intPlayerBetAmount = (self.currentRound.maximumBet) * 1

                #check if the player has enough money
                if ((self.listOfPlayers[incPlayerIndex].playerMoney >= intPlayerBetAmount) and ((self.currentRound.maximumBet == 0) or (intPlayerBetAmount == currentRound.maximumBet))):
                    #if player has enough money, and the amount is = the max bet or is the first bet, then implement it

                    #DEBUGTEXT
                    #print("Player " + str(incPlayerIndex+1) + "\\" + str(len(listOfPlayers)) + " bets by: $" + str(intPlayerBetAmount) + "/ $" + str(self.listOfPlayers[incPlayerIndex].playerMoney))

                    #increase the pot
                    self.currentRound.currentPot += intPlayerBetAmount
                    #DEBUG
                    #if (intPlayerBetAmount > 80000):
                        #print("WARNING! LINE 584! PLAYER BETTING OVER 80k!")

                    #increase player bet amount + deduct their bet from their money
                    self.listOfPlayers[incPlayerIndex].playerMoney -= incAction.actAmt
                    #incPlayer.playerMoney -= intPlayerBetAmount
                    #debug
                    #if (intPlayerBetAmount < 0):
                        #print("WARNING! LINE 591! PLAYER BETTING A NEGATIVE AMOUNT")

                    self.currentRound.tempPlayerBets[incPlayerIndex] += intPlayerBetAmount

                    #set the new maximum bet if this is a new bet
                    if(self.currentRound.maximumBet == 0):
                        self.currentRound.maximumBet = intPlayerBetAmount

                    #if this bet is all the player's money, then they are all in
                    #if (incPlayer.playerMoney == 0):
                    if (self.listOfPlayers[incPlayerIndex].playerMoney == 0):
                        self.listOfPlayers[incPlayerIndex].allIn = True
                else:
                    #player is inactive for the remainder of the round because they made an illegal move
                    self.listOfPlayers[incPlayerIndex].inactive = True
                    #DEBUGTEXT
                    #print("Player tried to bet too much, they are folded")
                    #player no longer has any bet standing in this hand
                    self.currentRound.tempPlayerBets[incPlayerIndex] = 0;
            elif (incAct == "C"):
                #if the player has enough money and the amount they entered is exactly equal to the maximum bet
                if ((self.listOfPlayers[incPlayerIndex].playerMoney >= incAction.actAmt) and (incAction.actAmt >= self.currentRound.maximumBet)):
                    #DEBUGTEXT
                    #print("Player CALLS with: $" + str(incAction.actAmt) + "/ $" + str(self.listOfPlayers[incPlayerIndex].playerMoney))
                    self.currentRound.currentPot += self.currentRound.maximumBet
                    #DEBUG
                    #print("WARNING! LINE 616! PLAYER USINGT CALL FUNCTIONALITY!")
                    #increase the player bet ammount and deduct their bet from their money
                    self.listOfPlayers[incPlayerIndex].playerMoney -= self.currentRound.maximumBet
                    self.currentRound.tempPlayerBets[incPlayerIndex] += self.currentRound.maximumBet

                    #max bet doesn't change in a call, so skip that
                elif (self.listOfPlayers[incPlayerIndex].playerMoney < self.currentRound.maximumBet):
                    #the player doesn't have enough to cover the max bet but is calling
                    ## PERFECT SIDEPOTS LATER
                    #DEBUGTEXT
                    #print("PLAYER IS CALLING WITH LESS THAN THE MAXIMUM BET")
                    #print("WARNING! LINE 627! PLAYER USING DEPRICATED CALL FUNCTIONALITY!")
                    self.currentRound.currentPot += self.listOfPlayers[incPlayerIndex].playerMoney
                    self.currentRound.tempPlayerBets[incPlayerIndex] += self.listOfPlayers[incPlayerIndex].playerMoney
                    self.listOfPlayers[incPlayerIndex].playerMoney = 0
                    self.listOfPlayers[incPlayerIndex].allIn = True
                else:
                    #player is inactive for the remainder of the round
                    print("ILLEGAL CALL, PLAYER FOLDED")
                    self.listOfPlayers[incPlayerIndex].inactive = True
                    #player no longer has any bet standing in this hand
                    self.currentRound.tempPlayerBets[incPlayerIndex] = 0;
            elif (incAct == "F"):
                #player is inactive for the remainder of the round
                #DEBUGTEXT
                #print("Player folds!")
                #incPlayer.inactive = True
                self.listOfPlayers[incPlayerIndex].inactive = True
                #print("Player " + str(incPlayerIndex+1) + "\\" + str(len(listOfPlayers)) + " folds with a stack of $" + str(incPlayer.playerMoney))
                #player no longer has any bet standing in this hand
                self.currentRound.tempPlayerBets[incPlayerIndex] = 0;
            else:
                #unknown or invalid action, player folds.
                #player is inactive for the remainder of the round
                #DEBUGTEXT
                #print("PLAYER FOLDS FOR UNKNOWN REASONS!")
                #incPlayer.inactive = True
                self.listOfPlayers[incPlayerIndex].inactive = True
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
        subRaises = ["R0","R1","R2","R3","R4","R5"]
        subBets = ["B00","B05", "B10", "B20", "B50", "BFP", "BHP"]

        #Raises: Min-raise, 2x Min, 4x Min, 8x Min, All in
        #Bets: Min Bet(call, or check if 0), 5% (of Stack), 10%, 20%, 50%, Pot Side Bet, Half Pot
        # R = Raise, should have a corresponding amount
        # B = Bet, should have a corresponding amount, a check is a bet of 0
        # C = Call, corresponding amount = unknown. Player can call with max(currentMaxBet, playerMoney) but if they don't have enough money, they only get the sidepot
        # F = Fold, corresponding amount = 0

        def __init__(self, incAction, incAmt, incSubAction):
            if (incAction in self.actions):
                self.actAction = incAction
                self.actAmt = incAmt
                self.actSub = incSubAction
                self.actIntValue = 0
                self.setPlayerActionInt()

            else:
                self.actAction = "F"
                self.actAmt = 0
                self.actSub = "F"
                self.actIntValue = 0
        def setPlayerActionInt(self):
            if(self.actAction=="F"):
                self.actIntValue = 0
            elif(self.actAction=="R"):
                #check subraises
                if(self.actSub == "R0"):
                    self.actIntValue = 1
                elif (self.actSub == "R1"):
                    self.actIntValue = 2
                elif (self.actSub == "R2"):
                    self.actIntValue = 3
                elif (self.actSub == "R3"):
                    self.actIntValue = 4
                elif (self.actSub == "R4"):
                    self.actIntValue = 5
                elif (self.actSub == "R5"):
                    self.actIntValue = 6
            elif(self.actAction =="B"):
                if (self.actSub == "B00"):
                    self.actIntValue = 7
                elif (self.actSub == "B05"):
                    self.actIntValue = 8
                elif (self.actSub == "B10"):
                    self.actIntValue = 9
                elif (self.actSub == "B20"):
                    self.actIntValue = 10
                elif (self.actSub == "B50"):
                    self.actIntValue = 11
                elif (self.actSub == "BHP"):
                    self.actIntValue = 12
                elif (self.actSub == "BFP"):
                    self.actIntValue = 13
            else:
                self.actIntValue = 0
                #we fold because we got passed some BS
    #Initialize the new tournament


    #how many games
    numGames = incNumberOfGames

    #how many rounds per game
    numRoundsPerGame = 30

    simulationOutputString = ""

    #DEBUG
    start = time.time()
    strFinalResults1 = "RESULTS: \n LearnerBot1 Scores: "
    strFinalResults2 = "RESULTS: \n LearnerBot2 Scores: "
    strFinalResults3 = "RESULTS: \n LearnerBot4 Scores: "
    #start the games +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    for i in range(0, numGames):
        #define a list to store the current players (each game has a unique set of players)
        listOfPlayers = []
        listOfPlayers[:] = []
        #set player loop (1 to 8, if not specified, pick at random)
        #listOfPlayers.append(Player("Player"))
        listOfPlayers.append(Player("Grace-Player"))
        listOfPlayers[0].playerName = "LearnerBot1"
        #listOfPlayers.append(Player("Player"))
        listOfPlayers.append(Player("Grace-Player"))
        listOfPlayers[1].playerName = "LearnerBot2"
        listOfPlayers[2].playerName="LearnerBot3"
        listOfPlayers[3].playerName= "LearnerBot4"
        for u in range(0, 6):
            #print("I have set player " + str(u))
            #create 8 players, ALL RANDOM FOR NOW
            listOfPlayers.append(Player("Random"))
        random.shuffle(listOfPlayers) #shuffle the list of players so the learning bots aren't always in the same initial position
        currentGame = Game(listOfPlayers)

        #start the rounds ----------------------------------------------------------------------------------------
        #DEBUGTEXT
        #print("\n\nBEGIN GAME NUMBER: " + str(i+1))
        #simulationOutputString += ("\n\nBEGIN GAME NUMBER: " + str(i+1))
        for j in range(0, numRoundsPerGame):
            currentRound = Round()
            #DEBUGTEXT
            #print("\n Begin round number: " + str(j))

            #currentGame.setNewRound(currentRound)
            currentGame.setNewRound(Round())
            curGamestage = 0

            #start the game

            #set all the variable
            tempPlayerBets = [0] * 8

            #tempPlayerBets[:] = []

            #create new deck
            #d = Deck() # new deck created
            #deal the cards // randomly select cards from the deck and give them to a player.
            #set the blinds
            numCurPlayers = len(currentGame.listOfPlayers)
            #currentGame.listOfPlayers[(currentGame.currentDealer+1)%numCurPlayers].modMoney(-currentGame.smallBlind)
            currentGame.listOfPlayers[(currentGame.currentDealer+1)%numCurPlayers].playerMoney -= currentGame.smallBlind
            currentGame.currentRound.tempPlayerBets[(currentGame.currentDealer+1)%numCurPlayers]+=currentGame.smallBlind
            currentGame.currentRound.currentPot +=(currentGame.smallBlind)
            #simulationOutputString += ("\nAdding a small blind of: $" + str(currentGame.smallBlind) + " and a big blind of: $" + str(currentGame.bigBlind))
            currentGame.listOfPlayers[(currentGame.currentDealer+2)%numCurPlayers].playerMoney -= currentGame.bigBlind
            currentGame.currentRound.tempPlayerBets[(currentGame.currentDealer+2)%numCurPlayers]+=currentGame.bigBlind
            currentGame.currentRound.currentPot +=(currentGame.bigBlind)

            for p in currentGame.listOfPlayers:
                if (p.inactive == False):
                    p.drawCards(currentGame.currentRound.deck)
                    p.lastPlayerMoney = p.playerMoney

            #d.printRemainingDeck() #Prints the remaining cards

            #deduct blinds
    ##        numCurPlayers = len(currentGame.listOfPlayers)
    ##        if(currentGame.listOfPlayers[(currentGame.currentDealer+1)%numCurPlayers].playerMoney>0):
    ##            currentGame.listOfPlayers[(currentGame.currentDealer+1)%numCurPlayers].modMoney(-currentGame.smallBlind)
    ##            currentGame.currentRound.tempPlayerBets[(currentGame.currentDealer+1)%numCurPlayers]+=currentGame.smallBlind
    ##            currentGame.currentRound.currentPot +=(currentGame.smallBlind)
    ##
    ##        if(currentGame.listOfPlayers[(currentGame.currentDealer+2)%numCurPlayers].playerMoney>0):
    ##            currentGame.listOfPlayers[(currentGame.currentDealer+2)%numCurPlayers].modMoney(-currentGame.bigBlind)
    ##            currentGame.currentRound.tempPlayerBets[(currentGame.currentDealer+2)%numCurPlayers]+=currentGame.bigBlind
    ##            currentGame.currentRound.currentPot +=(currentGame.bigBlind)





            def collectBets():
                # 1) Loop through players and get actions until allBetsEqual
                #start at (currentDealer+3)%numCurPlayers and loop asking for actions.
                numActivePlayers = 0
                for z in range(0, numCurPlayers):
                    if (currentGame.listOfPlayers[z].inactive == False and currentGame.listOfPlayers[z].allIn == False):
                        numActivePlayers += 1
                for q in range(0, numCurPlayers):
                    #DEBUGTEXT
                    #print("Get the action from player and update gamestate")
                    #standinForGamestate = []
                    if ((currentGame.listOfPlayers[(q+currentGame.currentDealer+3)%numCurPlayers].inactive == False) and (currentGame.listOfPlayers[q].allIn == False) and (numActivePlayers > 1)):
                        #if (numActivePlayers == 1):
                        #    #if there is only one player, break out of the loop
                        #    break
                        #DEBUGTEXT
                        #print("Player " + str((q + 1+currentGame.currentDealer+3)%numCurPlayers) + "\\" + str(numCurPlayers) + "'s action is implemented!")
                        #newPlayerAction = p.currentAI.returnAction(standinForGamestate)
                        #ask for the action, give current gamestate including cards, pot size, bets, stack sizes, etc.
                        #newPlayerAction = currentGame.listOfPlayers[(q+currentGame.currentDealer+3)%numCurPlayers].currentAI.returnAction(standinForGamestate)

                        #First we construct the gamestate for a particular player (if they are not a random player) then we pass it to them so they can make their move.

                        #we do this in the loop because each player's bet can affect the pot odds for future players
                        calcPotOdds = currentGame.currentRound.maximumBet / currentGame.currentRound.currentPot
                        #DEBUGTEXT
                        #print("Asking the player to generate their gamestate passing in an array of community cards of length: " + str(len(currentGame.currentRound.communityCards)))
                        currentPlayerGamestate = currentGame.listOfPlayers[(q+currentGame.currentDealer+3)%numCurPlayers].constructGamestate(calcPotOdds, curGamestage, ((q+currentGame.currentDealer+3)%numCurPlayers), currentGame.currentRound.communityCards.copy())

                        newPlayerAction = currentGame.listOfPlayers[(q+currentGame.currentDealer+3)%numCurPlayers].currentAI.returnAction(currentPlayerGamestate)
                        #print("Implement the action from the player")
                        currentPlayer = currentGame.listOfPlayers[(q+currentGame.currentDealer+3)%numCurPlayers]
                        #implement the action in the game engine // If the action is invalid, the player folds
                        currentGame.implementAction(newPlayerAction, currentPlayer, currentGame.listOfPlayers.index(currentPlayer))

                        #I did an action, so if this is a player (Q learning) and not a random bot, then I need to record the action
                        if (currentGame.listOfPlayers[(q+currentGame.currentDealer+3)%numCurPlayers].currentAI.name == "Player"):
                            #Then this is a learning player, so we should update the list of Q action pairs it's been in
                            currentGame.listOfPlayers[(q + currentGame.currentDealer + 3) % numCurPlayers].addOldState(currentPlayerGamestate, newPlayerAction.actIntValue)
                            #currentGame.listOfPlayers[(q + currentGame.currentDealer + 3) % numCurPlayers].oldStates.append(currentPlayerGamestate)
                            #currentGame.listOfPlayers[(q + currentGame.currentDealer + 3) % numCurPlayers].oldActions.append(newPlayerAction.actIntValue)
                        if (currentGame.listOfPlayers[
                            (q + currentGame.currentDealer + 3) % numCurPlayers].currentAI.name == "Grace-Player"):
                            # Then this is a learning player, so we should update the list of Q action pairs it's been in
                            currentGame.listOfPlayers[(q + currentGame.currentDealer + 3) % numCurPlayers].addOldState(
                                currentPlayerGamestate, newPlayerAction.actIntValue)
                            # currentGame.listOfPlayers[(q + currentGame.currentDealer + 3) % numCurPlayers].oldStates.append(currentPlayerGamestate)
                            # currentGame.listOfPlayers[(q + currentGame.currentDealer + 3) % numCurPlayers].oldActions.append(newPlayerAction.actIntValue)

                        #this updates the gamestate for the next player before it loops
                    else:
                        #DEBUGTEXT
                        #print("Player " + str((q + 1+currentGame.currentDealer+3)%numCurPlayers) + "'s action skipped because player all in or out of game or is last player left" + " -- All In: " + str(currentGame.listOfPlayers[(q+currentGame.currentDealer+3)%numCurPlayers].allIn) + " -- Folded: " + str(currentGame.listOfPlayers[(q+currentGame.currentDealer+3)%numCurPlayers].inactive) + " -- Num Players: " + str(numActivePlayers))
                        continue


            collectBets()
            if (len(listOfPlayers) == 1):
                # if there is exactly one player left, give them the pot and break out of the round
                listOfPlayers[0].playerMoney += currentRound.currentPot
                currentRound.currentPot = 0
                break
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
            curGamestage = 1 #at post flop gamestage
            #DEBUGTEXT
            #currentGame.currentRound.printCommunityCards()

            collectBets()
            if (len(listOfPlayers) == 1):
                # if there is exactly one player left, give them the pot and break out of the round
                listOfPlayers[0].playerMoney += currentRound.currentPot
                currentRound.currentPot = 0
                break
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
            curGamestage = 2 # at the post turn gamestage
            #DEBUGTEXT
            #currentGame.currentRound.printCommunityCards()

            collectBets()
            if (len(listOfPlayers) == 1):
                # if there is exactly one player left, give them the pot and break out of the round
                listOfPlayers[0].playerMoney += currentRound.currentPot
                currentRound.currentPot = 0
                break
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
            curGamestage = 3 #at the post river gamestage
            #DEBUGTEXT
            #currentGame.currentRound.printCommunityCards()

            #collect new betting round.
            collectBets()
            if (len(listOfPlayers) == 1):
                # if there is exactly one player left, give them the pot and break out of the round
                listOfPlayers[0].playerMoney += currentRound.currentPot
                currentRound.currentPot = 0
                break

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
                    currentHighestRank = 0

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

                    if (currentHighestRank == -1):
                        #no player was ever active, so give the money to a random person
                        currentWinner[0] = 0


            #Add the pot to the money of whichever player has the highest.
            numWinners = len(currentWinner)
            perPlayerPot = currentGame.currentRound.currentPot // numWinners
            #print("Resolving the game with " + str(numWinners) + " winners.")
            for y in currentWinner:
                #give the split pot to all players splitting it
                #DEBUG
                #if (perPlayerPot > 80000):
                    #print("WARNING! LINE 986! AWARDING OUT OF BOUNDS POT!")
                currentGame.listOfPlayers[y].playerMoney += perPlayerPot
                currentGame.listOfPlayers[y].allIn = False


            #print("Awarding a pot value of $" + str(perPlayerPot) + " with " + str(numWinners) + " winners!")
            #simulationOutputString += ("\n The total pot value is: $" + str(currentGame.currentRound.currentPot))
            #simulationOutputString += ("\nAwarding a pot value of $" + str(perPlayerPot) + " with " + str(numWinners) + " winners!")
            #print("Round resolved!")
            currentRound.currentPot = 0  # RESET THE POT TO NOTHING





            #set all players to not inactive and not all in
            #If a player has no more money left, remove them from the list of players for this game
            for p in currentGame.listOfPlayers:
                p.inactive = False
                p.allIn = False

                #money has been awarded, so if this is a player (Q learning) bot, then update Q states using the old
                # state/action pairs that were saved in the player

                #if (currentGame.listOfPlayers[(q+currentGame.currentDealer+3)%numCurPlayers].currentAI.name == "Player"):
                if (p.currentAI.name == "Player"):
                    #we are a Q learning bot
                    calculatedReward = p.playerMoney - p.lastPlayerMoney
                    #this is the money they have now, minus the money they had at the start of the round
                    #this is positive if they won money, negative if they lost money

                    intNumStatesExamined = 0
                    #DEBUGTEXT
                    #print("The length is: " + str(len(p.oldStates)))

                    for sapair in reversed(range(0, len(p.oldStates))):
                        #print("")
                        #print(type(p.oldStates[sapair]))
                        #print(p.oldStates[sapair])

                        dim0 = p.oldStates[sapair].dim0
                        dim1 = p.oldStates[sapair].dim1
                        dim2 = p.oldStates[sapair].dim2
                        dim3 = p.oldStates[sapair].dim3
                        dim4 = p.oldStates[sapair].dim4
                        dim5 = p.oldStates[sapair].dim5
                        dim6 = p.oldStates[sapair].dim6
                        dim7 = p.oldStates[sapair].dim7
                        dim8 = p.oldActions[sapair] #this should be the integer action value

                        #get the old state, and the old action using the integer index "sapair"
                        #it is counting down in reverse order, so newest actions first, oldest last
                        #the decay for each action should be 0.6^x where x is the number of actions back it was, less 1
                        #thus the first action should get full value, second should get 0.6, third 0.36, etc

                        currentQsa = incNumpyArray[dim0, dim1, dim2, dim3, dim4, dim5, dim6, dim7, dim8]
                        foundMaxQsa = 0.00

                        #FIND THE MAX EXPECTED VALUE FOR ALL ACTIONS IN THAT STATE
                        actionWithMaxValue = 0

                        for actForState in range(0, 14):
                            if (incNumpyArray[dim0, dim1, dim2, dim3, dim4, dim5, dim6, dim7, actForState] > foundMaxQsa):
                                actionWithMaxValue = actForState
                                foundMaxQsa = incNumpyArray[dim0, dim1, dim2, dim3, dim4, dim5, dim6, dim7, actForState]

                        newQsa = currentQsa + (0.05)*( ((calculatedReward * (0.6 ** intNumStatesExamined))) + (0.9 * foundMaxQsa) - currentQsa) #this decays the reward, the further back we go

                        incNumpyArray[dim0, dim1, dim2, dim3, dim4, dim5, dim6, dim7, dim8] = (newQsa)
                        #We just updated a Q(s,a), so we should decrease epsilon, as long as it doesn't go below the minimum
                        if(incEpsilonArray[0] > 0.05):
                            incEpsilonArray[0] -= 0.0000095 #At this rate, we should reach epsilon of 5% after 100,000 updates to the policy.
                            #EPSILON DECAY

                        intNumStatesExamined += 1
                    #now that I have looped through all the states and updated the Q values, erase the old states!
                    p.oldStates.clear()
                    p.oldActions.clear()

                if (p.currentAI.name == "Grace-Player"):
                    #we are a Q learning bot
                    calculatedReward = p.playerMoney - p.lastPlayerMoney
                    #this is the money they have now, minus the money they had at the start of the round
                    #this is positive if they won money, negative if they lost money

                    intNumStatesExamined = 0
                    #DEBUGTEXT
                    #print("The length is: " + str(len(p.oldStates)))

                    for sapair in reversed(range(0, len(p.oldStates))):
                        #print("")
                        #print(type(p.oldStates[sapair]))
                        #print(p.oldStates[sapair])

                        dim0 = p.oldStates[sapair].dim0
                        dim1 = p.oldStates[sapair].dim1
                        dim2 = p.oldStates[sapair].dim2
                        dim3 = p.oldStates[sapair].dim3
                        dim4 = p.oldStates[sapair].dim4
                        dim5 = p.oldStates[sapair].dim5
                        dim6 = p.oldStates[sapair].dim6
                        dim7 = p.oldStates[sapair].dim7
                        dim8 = p.oldActions[sapair] #this should be the integer action value

                        #get the old state, and the old action using the integer index "sapair"
                        #it is counting down in reverse order, so newest actions first, oldest last
                        #the decay for each action should be 0.6^x where x is the number of actions back it was, less 1
                        #thus the first action should get full value, second should get 0.6, third 0.36, etc

                        currentQsa = incNumpyArray[dim0, dim1, dim2, dim3, dim4, dim5, dim6, dim7, dim8]
                        foundMaxQsa = 0.00

                        # FIND THE MAX EXPECTED VALUE FOR ALL ACTIONS IN THAT STATE
                        actionWithMaxValue = 0

                        for actForState in range(0, 14):
                            #if (incNumpyArray[
                             #   dim0, dim1, dim2, dim3, dim4, dim5, dim6, dim7, actForState] > foundMaxQsa):
                            actionWithMaxValue = actForState
                            foundMaxQsa = incNumpyArray[dim0, dim1, dim2, dim3, dim4, dim5, dim6, dim7, actForState]

                        newQsa = currentQsa + (0.05) * (((calculatedReward * (0.6 ** intNumStatesExamined))) + (
                                    0.9 * foundMaxQsa) - currentQsa)  # this decays the reward, the further back we go

                        incNumpyArray[dim0, dim1, dim2, dim3, dim4, dim5, dim6, dim7, dim8] = (newQsa)
                        # We just updated a Q(s,a), so we should decrease epsilon, as long as it doesn't go below the minimum
                        if (incEpsilonArray[0] > 0.05):
                            incEpsilonArray[
                                0] -= 0.0000095  # At this rate, we should reach epsilon of 5% after 100,000 updates to the policy.
                            # EPSILON DECAY

                        intNumStatesExamined += 1
                        # now that I have looped through all the states and updated the Q values, erase the old states!
                    p.oldStates.clear()
                    p.oldActions.clear()



                if (p.playerMoney <= 0):
                    #remove them for the remainder of rounds, (they will be added back into the next game)
                    #simulationOutputString += ("\nRemoving a player who has: $" + str(p.playerMoney))
                    currentGame.listOfPlayers.remove(p)
            #print("Current Game's list of players length: " + str(len(currentGame.listOfPlayers)))

            #If only one player left in the list of players, break out of the loop and end the game
            if (len(currentGame.listOfPlayers) == 1):
                #DEBUGTEXT
                #print("Game over with one player having all the money!")
                #print(str(currentGame.listOfPlayers[0].playerMoney))
                #simulationOutputString += ("\n\nGame over with one player having all the money!")
                #simulationOutputString += ("\nThe player has: $" + str(currentGame.listOfPlayers[0].playerMoney))
                #we have arrived at a winner, they have all the chips! No need to play more rounds, break out of the loop!
                break
            #print("J is: " + str(j))

            #DEBUG MONEY COUNT
            # moneyCheck = 0
            # for player in currentGame.listOfPlayers:
            #     moneyCheck += player.playerMoney
            # print("Total Game Money for round: " + str(j) + " is $" + str(moneyCheck))


            #simulationOutputString += ("J is: " + str(j) + ", ")
            if (j == (numRoundsPerGame-1)):
                #print the list of players and their money.
                outputString = ""
                outputSum = 0
                # for player in currentGame.listOfPlayers:
                #     outputString = (outputString +"\nPlayer X finishes the rounds with: $")
                #     outputString = (outputString + str(player.playerMoney))
                #     outputSum += player.playerMoney
                # simulationOutputString += ("\nTotal Game Money: $" + str(outputSum))
                #print("Total Game Money: $" + str(outputSum))

                #simulationOutputString += outputString
                #print(outputString)
            #last part of resolving is to increment the dealer
            currentGame.currentDealer = (currentGame.currentDealer + 1)%numCurPlayers
            currentGame.currentRound.currentPot = 0
            currentWinner[:] = [] #delete the winner list
        #this is code inside the game, but outside the round
        intLearnBotCount1 = 0
        intLearnBotCount2 = 0
        for activePlayer in currentGame.listOfPlayers:
            if (activePlayer.playerName == "LearnerBot1"):
                strFinalResults1 += ("$" + str(activePlayer.playerMoney) + ", ")
                intLearnBotCount1 += 1
            elif (activePlayer.playerName == "LearnerBot2"):
                strFinalResults2 += ("$" + str(activePlayer.playerMoney) + ", ")
                intLearnBotCount2 += 1
        if intLearnBotCount1 == 0:
            strFinalResults1 += "$0, "
        if intLearnBotCount2 == 0:
            strFinalResults2 += "$0, "
    print(strFinalResults1)
    print(strFinalResults2)
    #HERE IS THE END OF THIS GAME

    #print accumulated output
    print(simulationOutputString)

    #DEBUG -- Below lines are for debug purposes
    #print("DONE!")
    end = time.time()
    print(end - start)

#runPokerTable()

simStart = time.time()
numThreads = 14
threadList = []
# for y in range(0, numThreads):
#     threadList.append(threading.Thread(target=runPokerTable))
#     threadList[y].start()
#
#
# for thread in threadList:
#     thread.join()

def info(title):
    print(title)
    print('module name: ', __name__)
    if hasattr(os, 'getppid'): #if we are allowed to get the parent process ID, get and print it
        print('parent process:', os.getppid())
    print('process id:', os.getpid())


testnpArray = numpy.zeros((4,5), dtype=int)

#construct the gigantic array
fullSAArray = numpy.zeros((4, 5, 5, 7, 4, 5, 10, 9, 14), dtype=numpy.double)

#this is the global learning rate for epsilon greedy learning
globalEpsilon = numpy.zeros((1), dtype=numpy.double)
globalEpsilon[0] = 1.00

#this should be shared memory
#sharedMemoryBlock = multiprocessing.shared_memory.SharedMemory(create=True, size=testnpArray.nbytes)

#create the gigantic block of shared memory
#fullSharedStateArray = multiprocessing.shared_memory.SharedMemory(create=True, size=fullSAArray.nbytes)

#this is the shared epsilon memory
#sharedEpsilon = multiprocessing.shared_memory.SharedMemory(create=True, size=globalEpsilon.nbytes)

#this is the test one
#newNumpyArray = numpy.ndarray(testnpArray.shape, dtype=testnpArray.dtype, buffer=sharedMemoryBlock.buf)

#this is the real one
#fullNumpyArray = numpy.ndarray(fullSAArray.shape, dtype=fullSAArray.dtype, buffer=fullSharedStateArray.buf)

#this is the epsilon share linking
#epsilonArray = numpy.ndarray(globalEpsilon.shape, dtype=globalEpsilon.dtype, buffer=sharedEpsilon.buf)

#newNumpyArray[:] = testnpArray[:] #copy the array

#fullNumpyArray[:] = fullSAArray[:] #copies the array

#epsilonArray[:] = globalEpsilon[:] #copy the value (which should be 1)
#print("The next print should just have 1.00000")
#print(epsilonArray)

#sharedMemoryName = sharedMemoryBlock.name

#sharedFullStateArrayName = fullSharedStateArray.name

#sharedEpsilonName = sharedEpsilon.name



#newNumpyArray[2, 2] = 555
#update the list
#print(newNumpyArray)
#this should print the list

#print(sharedMemoryName)


#create the shared memory outside of the process

#spawn all the processes

#they should all have access to this memory block from within the processes




if __name__ == '__main__':
    info('main line')
    for y in range(0, numThreads):
        #threadList.append(Process(target=runPokerTable, args=(("PokerTable " + str(y)), 1000, sharedFullStateArrayName, sharedEpsilonName)))
        threadList[y].start()


for process in threadList:
    process.join()


    simEnd = time.time()
    print("Simulation time:" + str(simEnd - simStart))


#del(sharedMemoryBlock)