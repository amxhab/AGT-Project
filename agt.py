from cmath import inf
from dataclasses import dataclass
import random
import time
import itertools
import os
import json

numOfTraits = 16
numOfAdvertisers = 16

max_val_of_traits = 10

valuations_vector = {}
valuations_vector_unknown = {}

#Randomize desirable traits for advertisers
def createDesirableTraits():
    return [1 if random.random() > 0.5 else 0 for i in range(0, numOfTraits)]

#Valuation Function for Advertisers
def valuation(j, desirableTraits, stateOfNature):
    val = 0
    for i in range(0, numOfTraits):
        if stateOfNature[i] == '?':
            val += valuations_vector_unknown[j][i]
        elif stateOfNature[i] == desirableTraits[i]:
            val += valuations_vector[j][i]
    return val

def createAdvertisers():
    advertisers = {}
    for i in range(0,numOfAdvertisers):
        advertisers[i] = createDesirableTraits()
    return advertisers

def greedyAlgorithm(currStateOfNature, currSignaling, unRevealTraits, advertisers, remainingAdvertisers):
    newUnReveal = []
    l = len(unRevealTraits)
    if l == 1:
        return currStateOfNature, newUnReveal
    for i in range(0, int(l/2)):
        sxy = -inf
        sx = -inf
        sy = -inf
        chosenX = -1
        chosenY = -1
        for a in range (0, len(unRevealTraits)):
            for b in range(a+1, len(unRevealTraits)):
                x = unRevealTraits[a]
                y = unRevealTraits[b]
                sumOfx = 0
                sumOfy = 0
                for adv in remainingAdvertisers:
                    xState = [currSignaling[i] if i!=x else currStateOfNature[i] for i in range(0,numOfTraits)]
                    yState = [currSignaling[i] if i!=y else currStateOfNature[i] for i in range(0,numOfTraits)]
                    xyState =  [currSignaling[i] if i!=y and i!=x else currStateOfNature[i] for i in range(0,numOfTraits)]
                    sumOfx += valuation(adv, advertisers[adv],xState) - valuation(adv, advertisers[adv],xyState)
                    sumOfy += valuation(adv, advertisers[adv],yState) - valuation(adv, advertisers[adv],xyState)
                if max(sumOfx,sumOfy) > sxy:
                    sxy = max(sumOfx,sumOfy)
                    sx = sumOfx
                    sy = sumOfy
                    chosenX = x
                    chosenY = y
        unRevealTraits.remove(chosenX)
        unRevealTraits.remove(chosenY)
        if sx > sy:
            currSignaling[chosenX] = currStateOfNature[chosenX]
            newUnReveal.append(chosenY)
        else:
            currSignaling[chosenY] = currStateOfNature[chosenY]
            newUnReveal.append(chosenX)
    return currSignaling, newUnReveal

def greedyAlgorithmPrivate(currStateOfNature, currSignalingDict, unRevealTraitsDict, advertisers, remainingAdvertisers):
    newUnRevealDict = {i:[] for i in range(0, numOfAdvertisers)}
    l = len(unRevealTraitsDict[remainingAdvertisers[0]])
    if l == 1:
        return  {i:currStateOfNature for i in range(0,numOfAdvertisers)}, None

    for adv in remainingAdvertisers:
        unRevealTraits = unRevealTraitsDict[adv]
        currSignaling = currSignalingDict[adv]
        for i in range(0, int(l/2)):
            sxy = -inf
            sx = -inf
            sy = -inf
            chosenX = -1
            chosenY = -1
            for a in range (0, len(unRevealTraits)):
                for b in range(a+1, len(unRevealTraits)):
                    x = unRevealTraits[a]
                    y = unRevealTraits[b]
                    xState = [currSignaling[i] if i!=x else currStateOfNature[i] for i in range(0,numOfTraits)]
                    yState = [currSignaling[i] if i!=y else currStateOfNature[i] for i in range(0,numOfTraits)]
                    xyState =  [currSignaling[i] if i!=y and i!=x else currStateOfNature[i] for i in range(0,numOfTraits)]
                    sumOfx = valuation(adv, advertisers[adv],xState) - valuation(adv, advertisers[adv],xyState)
                    sumOfy = valuation(adv, advertisers[adv],yState) - valuation(adv, advertisers[adv],xyState)
                    if max(sumOfx,sumOfy) > sxy:
                        sxy = max(sumOfx,sumOfy)
                        sx = sumOfx
                        sy = sumOfy
                        chosenX = x
                        chosenY = y
            unRevealTraits.remove(chosenX)
            unRevealTraits.remove(chosenY)
            if sx > sy:
                currSignaling[chosenX] = currStateOfNature[chosenX]
                newUnRevealDict[adv].append(chosenY)
            else:
                currSignaling[chosenY] = currStateOfNature[chosenY]
                newUnRevealDict[adv].append(chosenX)
        currSignalingDict[adv] = currSignaling

    return currSignalingDict, newUnRevealDict 

#Return top half bidders + winning bid and second bid
def getTopHalf(remaining, bids):
    half = int(len(remaining)/2)
    toSort = [(bids[i], i) for i in remaining]
    toSort.sort(key=lambda x: x[0], reverse=True)
    
    newRemaining = toSort[:half]
    return toSort[0][0], toSort[1][0], [x[1] for x in newRemaining]

def optimal(currStateOfNature, currSignaling, unRevealTraits, advertisers, remainingAdvertisers, bids):
    newUnReveal = []
    l = len(unRevealTraits)
    maxPaying = -inf
    maxBidding = -inf
    last_standing = -1
    maxSignaling = currSignaling
    for traits in itertools.combinations(unRevealTraits, int(l/2)):
        signaling = [currSignaling[i] if i not in traits else currStateOfNature[i] for i in range(0,numOfTraits)]
        newBids = {}
        for adv in remainingAdvertisers:
            newBids[adv] = max(bids[adv], valuation(adv, advertisers[adv], signaling))
        bidding, paying, newReamainingAdvertisers = getTopHalf(remainingAdvertisers, newBids)
        if len(newReamainingAdvertisers) != 1:
            _,_, bidding, paying, last = optimal(currStateOfNature, signaling, [i for i in unRevealTraits if i not in traits], advertisers, newReamainingAdvertisers, newBids)
        else:
            last = newReamainingAdvertisers[0]
        if paying > maxPaying:
            maxPaying = paying
            maxBidding = bidding
            maxSignaling = signaling
            last_standing = last
            newUnReveal = [i for i in unRevealTraits if i not in traits]

    return maxSignaling, newUnReveal, maxBidding, maxPaying, last

def auction():

    expirment = {}
    e_greedy = {}
    e_greedy_private = {}
    e_optimal = {}

    #Create Expirement Data
    for i in range(0,numOfAdvertisers):
        valuations_vector[i] = [int(random.random()*(max_val_of_traits+1)) for j in range(0, numOfTraits)]
        valuations_vector_unknown[i] = [int(random.random()*(2*(valuations_vector[i][j]+1)/3)) for j in range(0, numOfTraits)]
    currStateOfNature = createDesirableTraits()
    advertisers = createAdvertisers()
    currSignaling = ['?' for i in range(0, numOfTraits)]
    unRevealTraits = [i for i in range(0,numOfTraits)]
    advertisersBids = {i:0 for i in range(0,numOfAdvertisers)}
    remainingAdvertisers = [i for i in range(0,numOfAdvertisers)]

    #Greedy Public Test
    startTime = time.time()
    stage = 0
    while len(remainingAdvertisers) > 1:
        currSignaling, unRevealTraits = greedyAlgorithm(currStateOfNature, currSignaling, unRevealTraits, advertisers, remainingAdvertisers)
        
        stage+=1
        for adv in remainingAdvertisers:
            advertisersBids[adv] = max(advertisersBids[adv], valuation(adv, advertisers[adv], currSignaling))
        bidding, paying, remainingAdvertisers = getTopHalf(remainingAdvertisers, advertisersBids)
    time_took = time.time() - startTime

    e_greedy["time"] = time_took
    e_greedy["revenue"] = paying
    adv = remainingAdvertisers[0]
    e_greedy["welfare"] = valuation(adv, advertisers[adv], currStateOfNature) - paying
    e_greedy["winning_bid"] = bidding

    #Refresh Results
    currSignalingDict = {j:['?' for i in range(0, numOfTraits)] for j in range(0,numOfAdvertisers)}
    unRevealTraitsDict = {j:[i for i in range(0,numOfTraits)] for j in range(0, numOfAdvertisers)}
    advertisersBids = {i:0 for i in range(0,numOfAdvertisers)}
    remainingAdvertisers = [i for i in range(0,numOfAdvertisers)]

    #Greedy Private Test
    startTime = time.time()
    stage = 0
    while len(remainingAdvertisers) > 1:
        currSignalingDict, unRevealTraitsDict = greedyAlgorithmPrivate(currStateOfNature, currSignalingDict, unRevealTraitsDict, advertisers, remainingAdvertisers)
        
        stage+=1
        for adv in remainingAdvertisers:
            advertisersBids[adv] = max(advertisersBids[adv], valuation(adv, advertisers[adv], currSignalingDict[adv]))
        bidding, paying, remainingAdvertisers = getTopHalf(remainingAdvertisers, advertisersBids)
    time_took = time.time() - startTime

    e_greedy_private["time"] = time_took
    e_greedy_private["revenue"] = paying
    adv = remainingAdvertisers[0]
    e_greedy_private["welfare"] = valuation(adv, advertisers[adv], currStateOfNature) - paying
    e_greedy_private["winning_bid"] = bidding

    #Refresh Results
    currSignaling = ['?' for i in range(0, numOfTraits)]
    unRevealTraits = [i for i in range(0,numOfTraits)]
    advertisersBids = {i:0 for i in range(0,numOfAdvertisers)}
    remainingAdvertisers = [i for i in range(0,numOfAdvertisers)]

    #Optimal Public Test
    startTime = time.time()
    _,_, bidding, paying, last = optimal(currStateOfNature, currSignaling, unRevealTraits, advertisers, remainingAdvertisers, advertisersBids)
    time_took = time.time() - startTime

    e_optimal["time"] = time_took
    e_optimal["revenue"] = paying
    e_optimal["welfare"] = valuation(last, advertisers[last], currStateOfNature) - paying
    e_optimal["winning_bid"] = bidding

    #Second Price Test
    e_reg_second_price = {}

    for adv in remainingAdvertisers:
        advertisersBids[adv] = valuation(adv, advertisers[adv], currStateOfNature)

    toSort = [(advertisersBids[i], i) for i in range(0, numOfAdvertisers)]
    toSort.sort(key=lambda x: x[0], reverse=True)
    paying = toSort[1][0]
    bidding = toSort[0][0]

    e_reg_second_price["revenue"] = paying
    e_reg_second_price["welfare"] = bidding - paying
    e_reg_second_price["winning_bid"] = bidding

    expirment["greedy"] = e_greedy
    expirment["greedy_private"] = e_greedy_private
    expirment["optimal"] = e_optimal
    expirment["second_price_auction"] = e_reg_second_price

    return expirment

def append_csv_line(write, obj):
    lst = []
    lst.append(str(obj["greedy"]["time"]))
    lst.append(str(obj["greedy"]["revenue"]))
    lst.append(str(obj["greedy"]["welfare"]))
    lst.append(str(obj["greedy"]["winning_bid"]))
    lst.append(str(obj["greedy_private"]["time"]))
    lst.append(str(obj["greedy_private"]["revenue"]))
    lst.append(str(obj["greedy_private"]["welfare"]))
    lst.append(str(obj["greedy_private"]["winning_bid"]))
    lst.append(str(obj["optimal"]["time"]))
    lst.append(str(obj["optimal"]["revenue"]))
    lst.append(str(obj["optimal"]["welfare"]))
    lst.append(str(obj["optimal"]["winning_bid"]))
    lst.append(str(obj["second_price_auction"]["revenue"]))
    lst.append(str(obj["second_price_auction"]["welfare"]))
    lst.append(str(obj["second_price_auction"]["winning_bid"]))
    return write + ','.join(lst) + '\n'

#Convert json file to csv
def result_to_csv(start, end):
    write = "greedy_time,greedy_revenue,greedy_welfare,greedy_bid,private_time,private_revenue,private_welfare,private_bid,optimal_time,optimal_revenue,optimal_welfare,optimal_bid,second_revenue,second_welfare,second_bid\n"
    for i in range(start, end+1):
        if os.path.isfile(f"result{i}.json"):
            with open(f"result{i}.json") as json_file:
                data = json.load(json_file)
            for obj in data:
                write = append_csv_line(write, obj)
    
    with open("test.csv", 'w') as outfile:
        outfile.write(write)

NUM_OF_TEST = 100
if __name__ == '__main__':

    data = []
    for i in range(0, NUM_OF_TEST):
        print(f"Starting Test {i+1}")
        data.append(auction())
    
    with open("result.json", 'w') as outfile:
            json.dump(data, outfile, indent=4)





