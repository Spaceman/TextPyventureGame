import os
import random
import re
import json
import sys
import pickle
inventoryData = []
# Location is a list of hex [North South, East West, Up Down]
playerData = {'health':100,'location':[0x7F,0x7F,0x7F]}
posDirections = {'north':[0x01,0x00,0x00], 'east':[0x00,0x01,0x00], 'up':[0x00,0x00,0x01]}
negDirections = {'south':[0x01,0x00,0x00], 'west':[0x00,0x01,0x00], 'down':[0x00,0x00,0x01]}

def grammarAn(string):
    #If the word starts with a vowel, a -> an
    vowels=['a','e','i','o','u']
    if vowels.count(string[0]):
        return('n '+string)
    else:
        return(' '+string)

def movePlayer():
    #if the direction is longer than 1 word, merge
    if len(commandInput)>2:
        movementDirection = [commandInput[1], commandInput[2]]
        movementIndex = commandInput[1] + '_' + commandInput[2]
    else:
        movementDirection = [commandInput[1]]
        movementIndex = commandInput[1]
    try:
        #the value from the json
        movementValue = openRoom(playerData['location'],'Direction')[movementIndex]
    except KeyError:
        print('Direction not recongnized.')     
    if movementValue == True:
        print('Moving ' + movementIndex.replace('_',' ') + '.')
        for direction in movementDirection:
            if direction in posDirections:
                for i in range(0,3):
                    playerData['location'][i] += posDirections[direction][i]
            if direction in negDirections:
                for i in range(0,3):
                    playerData['location'][i] -= negDirections[direction][i]
        print(openRoom(playerData['location'],'Name') + '\n' + openRoom(playerData['location'],'Description'))
        #TODO: actually update player location and read title & description
    elif movementValue == False:
        print('Something is blocking the way.')

def inspect():
    if commandInput[1] == 'at':
        commandInput.remove(commandInput[1])
    try:
        print(openRoom(playerData['location'],'Inspect')[commandInput[1]])
    except KeyError:
        print('You can\'t seem to find a'+grammarAn(commandInput[1])+'.')

def isLocked(lockContainer):
    if 'Locked' in openRoom(playerData['location'],'Containers')[lockContainer]:
        keyItem = [x for x in inventoryData if x['UUID'] == openRoom(playerData['location'],'Containers')[lockContainer]['Locked']['KeyItem']]
        if keyItem:
            return False
        else:
            return True
    else:
        return False

def openContainer():
    itemlist=''
    couter=1
    if isLocked(commandInput[1]):
        print(openRoom(playerData['location'],'Containers')[commandInput[1]]['Locked']['LockMessage'])
    else:
        try:
            if commandInput[1]=='the':
                commandInput.remove(commandInput[1])
            #put each item that is not in the players inventory into a list
            validItems = [x for x in openRoom(playerData['location'],'Containers')[commandInput[1]]['Items'] if x not in inventoryData]
            #If the list is empty
            if len(validItems) == 0:
                itemlist+='nothing'
            else:
                for item in validItems:
                    if len(validItems)==couter:
                        #if there is one item or is the last item in the list
                        itemlist+='a'+grammarAn(item['Name'])
                    else: 
                        itemlist+='a'+grammarAn(item['Name'])+', and '
                    couter+=1
            print('Inside the '+commandInput[1]+' you find '+itemlist+'.')
        except KeyError:
            print('You can\'t seem to find a'+grammarAn(commandInput[1])+'.')

def openRoom(loc, var):
    roomfile=''
    for num in range(0,3):
        roomfile=roomfile+str(hex(loc[num])[2:])
    with open(roomfile+'.json','r') as f:
        roomdata = json.load(f)
        return roomdata[var]

def quitGame():
    pickle.dump(playerData,open('playerData.pkl','wb'))
    pickle.dump(inventoryData,open('inventoryData.pkl','wb'))
    sys.exit('Quiting...')

def getItem():
    #get item from container
    if commandInput[2]=='from':
        commandInput.remove(commandInput[2])
    if isLocked(commandInput[2]):
        print(openRoom(playerData['location'],'Containers')[commandInput[2]]['Locked']['LockMessage'])
    else:
        try:
            inventoryData.append([x for x in openRoom(playerData['location'],'Containers')[commandInput[2]]['Items'] if x['Name'] == commandInput[1]][0])
            print('You pick up the '+commandInput[1]+'.')
        except KeyError:
            print('You can\'t seem to find a'+grammarAn(commandInput[2])+'.')
        except IndexError:
            print('You can\'t seem to find a'+grammarAn(commandInput[1]+' in the '+commandInput[2]+'.'))

commandslist = {'move':movePlayer, 'go':movePlayer, 'quit':quitGame,'exit':quitGame, 'inspect':inspect, 'look':inspect, 'open':openContainer, 'get':getItem}

if __name__ == '__main__':
    try:
        playerData = pickle.load(open('playerData.pkl','rb'))
    except FileNotFoundError:
        print('Player data not found')
    try:
        inventoryData = pickle.load(open('inventoryData.pkl','rb'))
    except FileNotFoundError:
        print('Inventory data not found')

    print(openRoom(playerData['location'],'Name') + '\n' + openRoom(playerData['location'],'Description'))

    while True:
        try:
            commandInput=input('>>> ').casefold().split(' ')
            for item in commandInput:
                if item=="the":
                    commandInput.remove(item)
        except KeyboardInterrupt:
             quitGame()
        try:
            commandaction = commandslist[commandInput[0].lower()]
        except KeyError:
            print('Command not recoginized.')
        commandaction()