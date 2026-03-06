import nashpy
import numpy as np
import random
#Grant Zhong 33143242

#choice of location is completely random with selected probability for the safe location
def completeRandom(n,n2chance):

    n1 = 0
    n2 = 0
    
    for i in range(n):
        #choose location randomly 
        num = random.random()   
        if num > n2chance:
            n1 += 1
        else:
            n2 += 1
    
    return n1, n2

#model for when the player only picks safe
def allsafemodel(repeats,n,choice,noPlayer,x,y,n2chance):
    player = []
    otherPlayer = []
    
    #repeat x amount of time
    for j in range(repeats):
        playerLoot = 0
        otherPlayerLoot = 0

        #add loot for each player for n interations
        for i in range(n):
            n1, n2 = choice(noPlayer,n2chance)
            playerLoot += y
            otherPlayerLoot += x + n2 * y

        player.append(round(playerLoot,1))
        otherPlayer.append(round(otherPlayerLoot/noPlayer,1))

    return (player,round(sum(player)/len(player),1)), (otherPlayer,round(sum(otherPlayer)/len(otherPlayer),1))

#model for when the player only goes to the risky location
def allriskmodel(repeats,n,choice,noPlayer,x,y,n2chance):
    player = []
    otherPlayer = []
    
    #repeat x amount of time
    for j in range(repeats):
        playerLoot = 0
        otherPlayerLoot = 0

        #add loot for each player after n interations
        for i in range(n):
            n1, n2 = choice(noPlayer,n2chance)
            playerLoot += x/(n1 + 1)
            otherPlayerLoot += x*n1 /(n1 + 1) + n2 * y

        player.append(round(playerLoot,1))
        otherPlayer.append(round(otherPlayerLoot/noPlayer,1))

    return (player,round(sum(player)/len(player),1)), (otherPlayer,round(sum(otherPlayer)/len(otherPlayer),1))

#model for when player descicions is completely random
def completerandommodel(repeats,n,choice,noPlayer,x,y,n2chance):
    player = []
    otherPlayer = []

    #do this x amount of times
    for j in range(repeats):
        playerLoot = 0
        otherPlayerLoot = 0

        #iterate through a game
        for i in range(n):
            n1, n2 = choice(noPlayer,n2chance)
            pChoice1, pChoice2 = choice(1,0.5)

            #if player goes to risky location
            if pChoice1 == 1:
                playerLoot += x/(n1 + 1)
                otherPlayerLoot += x*n1 /(n1 + 1) + n2 * y
            
            #if player goes to safe location
            if pChoice2 == 1:
                playerLoot += y
                otherPlayerLoot += x + n2 * y

        player.append(round(playerLoot,1))
        otherPlayer.append(round(otherPlayerLoot/noPlayer,1))

    return (player,round(sum(player)/len(player),1)), (otherPlayer,round(sum(otherPlayer)/len(otherPlayer),1))

#model where player follows which location performed the best last iteration
def followlootmodel(repeats,n,choice,noPlayer,x,y, n2Chance):
    player = []
    otherPlayer = []
    
    #repeat this x times
    for j in range(repeats):

        playerLoot = 0
        otherPlayerLoot = 0

        #first iteration
        n1, n2 = choice(noPlayer,n2Chance)
        playerLoot += y
        otherPlayerLoot += x + n2 * y
        prevxloot = x/n1
        
        #for the rest of the game
        for i in range(1,n):
            #if risky location has more loot than safe
            if prevxloot > y:
                n1, n2 = choice(noPlayer,n2Chance)
                playerLoot += x/(n1 + 1)
                otherPlayerLoot += x*n1 /(n1 + 1) + n2 * y
                prevxloot = x/n1

            #if safe has more loot than risky
            else:
                n1, n2 = choice(noPlayer,n2Chance)
                playerLoot += y
                otherPlayerLoot += x + n2 * y
                prevxloot = x/n1

        player.append(round(playerLoot,1))
        otherPlayer.append(round(otherPlayerLoot/noPlayer,1))

    return (player,round(sum(player)/len(player),1)), (otherPlayer,round(sum(otherPlayer)/len(otherPlayer),1))

#perform all the models and give a result in a touple
#touple with first element containing the average loot for each iteration
#second element contains a selected amount of games loot for each model
def montecarlosim(repeats,noLootrun,choice,noPlayer,x,y,n2chance,noResults):
    #perform model for each type of player choice
    asp, asop = allsafemodel(repeats,noLootrun,choice,noPlayer,x,y,n2chance)
    arp, arop = allriskmodel(repeats,noLootrun,choice,noPlayer,x,y,n2chance)
    crp, crop = completerandommodel(repeats,noLootrun,choice,noPlayer,x,y,n2chance)
    flp, flop = followlootmodel(repeats,noLootrun,choice,noPlayer,x,y,n2chance)

    #store the average score 
    score = []
    score.append((asp[1], asop[1]))
    score.append((arp[1], arop[1]))
    score.append((crp[1], crop[1]))
    score.append((flp[1], flop[1]))

    #store individual results
    results = []
    results.append([])
    results.append([])
    results.append([])
    results.append([])
    #store up to a certain number of completed games
    for i in range(noResults):
        results[0].append((asp[0][i],asop[0][i]))
        results[1].append((arp[0][i],arop[0][i]))
        results[2].append((crp[0][i],crop[0][i]))
        results[3].append((flp[0][i],flop[0][i]))
    
    return score, results

#model to calculate  the nash equilbruim of a state
#requires the probability of going to the risky location for both prefer safe and prefer risk
def gametheorymodel(noPlayer,x,y,preferrisk,prefersafe):

    #calculate number of people in each location
    r1 = round(preferrisk * noPlayer)
    r2 = noPlayer - r1
    s1 = round(prefersafe * noPlayer)
    s2 = noPlayer - s1

    #set up the game matrix
    player = np.array([
        [x/(r1 + 1), x/(s1 + 1)],
        [y, y]
        ])
    otherplayer = np.array([
        [(x * r1/(r1+1) + r2*y)/noPlayer, (x * s1/(s1+1)+ s2*y)/noPlayer],
        [(x+r2*y)/noPlayer, (x+s2*y)/noPlayer]
    ])
    
    #calculate nash equilbrium
    game = nashpy.Game(player, otherplayer) 
    nash = game.support_enumeration()
    ver = game.vertex_enumeration()

    return game, list(nash), list(ver)

#monte carlo transition matrix
Game = np.array([
    [0.6,0.1,0.1,0.2],
    [0.3,0.1,0.3,0.3],
    [0.3,0.1,0.5,0.1],
    [0.3,0.2,0.4,0.1]
    ])

#calculate loot earned at that state
def calcLoot(state, noPlayer, x, y, preferrisk, prefersafe):
    #calculate number of people in location
    r1 = round(preferrisk * noPlayer)
    r2 = noPlayer - r1
    s1 = round(prefersafe * noPlayer)
    s2 = noPlayer - s1

    #calculate loot for the state
    #risky | risky
    if state == 0:
        return (x/(r1 + 1),(x * r1/(r1+1) + r2*y)/noPlayer)
    #safe | risky
    elif state == 1:
        return (y, (x+r2*y)/noPlayer)
    #risky | safe
    elif state == 2:
        return (x/(s1 + 1), (x * s1/(s1+1)+ s2*y)/noPlayer)
    #safe | safe
    else:
        return (y, (x+s2*y)/noPlayer)

#uses monte carlo to play the game any amount of time
def simulateGame(game, length, iter, noPlayer, x, y, preferrisk, prefersafe, start, numresults):
    
    results = []
    for i in range(iter):

        #store path and loot
        path = []
        totalLoot = [0,0]
        location = start
        #start game
        for j in range(length):

            #get probability for that location and random number
            curr = game[location]
            rand = random.random()

            #compare random number with probability to find location to land at.
            #Calculate loot and store the location. 
            #risky | risky
            if rand < curr[0]:
                loot = calcLoot(0,noPlayer, x, y, preferrisk, prefersafe)
                state = 0
            #risky | safe
            elif rand < curr[1] + curr[0]:
                loot = calcLoot(1, noPlayer, x, y, preferrisk, prefersafe)
                state = 1
            #safe | risky
            elif rand < curr[2] + curr[1] + curr[0]:
                loot = calcLoot(2, noPlayer, x, y, preferrisk, prefersafe)  
                state = 2
            #safe | safe
            else:
                loot = calcLoot(3, noPlayer, x, y, preferrisk, prefersafe)
                state = 3

            # store location and add everything up
            location = state
            path.append(state)
            newLoot = [totalLoot[0] + loot[0], totalLoot[1] + loot[1]]
            totalLoot = newLoot
        #store the results
        results.append((totalLoot, path))

    #calculate advantage of the players and the average score of every run
    player = 0
    otherplayer = 0
    pa = 0
    opa = 0
    draw = 0
    for i in range(len(results)):
        #add up score
        player += results[i][0][0]
        otherplayer += results[i][0][1]
        #calculate win
        if results[i][0][0] > results[i][0][1]:
            pa += 1
        elif results[i][0][0] == results[i][0][1]:
            draw += 1
        else:
            opa += 1
    #average it out for each run
    player = player/len(results)
    otherplayer = otherplayer/len(results)

    return (player, otherplayer), (pa,draw,opa), results[0:numresults]


print(montecarlosim(1000,3,completeRandom,99,20,1,0.75,8))
print(gametheorymodel(99,50,1,0.9,0.1))
print(np.linalg.matrix_power(Game,10))
print(simulateGame(Game,3,1000,99,50,1,0.75,0.25,1,8))

