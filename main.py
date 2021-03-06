import os
import random
import re
import json
import sys
import pickle
import tkinter

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
        updateText('Direction not recongnized.')
    if movementValue == True or (isLocked(movementIndex, 'Direction') == False):
        updateText('Moving ' + movementIndex.replace('_',' ') + '.')
        for direction in movementDirection:
            if direction in posDirections:
                for i in range(0,3):
                    playerData['location'][i] += posDirections[direction][i]
            if direction in negDirections:
                for i in range(0,3):
                    playerData['location'][i] -= negDirections[direction][i]
        updateText(openRoom(playerData['location'],'Name') + '\n' + openRoom(playerData['location'],'Description'))
    elif movementValue == False:
        updateText('Something is blocking the way.')
    elif isLocked(movementIndex, 'Direction'):
        updateText(openRoom(playerData['location'],'Direction')[movementIndex]['Locked']['LockMessage'])

def inspect():
    if commandInput[1] == 'at':
        commandInput.remove(commandInput[1])
    try:
        updateText(openRoom(playerData['location'],'Inspect')[commandInput[1]])
    except KeyError:
        updateText('You can\'t seem to find a'+grammarAn(commandInput[1])+'.')

def isLocked(lockObject, lockType):
    try:
        if 'Locked' in openRoom(playerData['location'],lockType)[lockObject]:
            hasKeyItem = [x for x in inventoryData if x['UUID'] == openRoom(playerData['location'],lockType)[lockObject]['Locked']['KeyItem']]
            if hasKeyItem:
                return False
            else:
                return True
        else:
            return False
    except TypeError:
        pass

def openContainer():
    itemlist=''
    couter=1
    try:
        if isLocked(commandInput[1], 'Containers'):
            updateText(openRoom(playerData['location'],'Containers')[commandInput[1]]['Locked']['LockMessage'])
        else:
            if commandInput[1]=='the':
                commandInput.remove(commandInput[1])
            #put each item that is not in the players inventory into a list
            validItems = uuidCompare(openRoom(playerData['location'],'Containers')[commandInput[1]]['Items'], inventoryData)
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
            updateText('Inside the '+commandInput[1]+' you find '+itemlist+'.')
    except KeyError:
        updateText('You can\'t seem to find a'+grammarAn(commandInput[1])+'.')

def getItem():
    #get item from container
    if commandInput[2]=='from':
        commandInput.remove(commandInput[2])
    if isLocked(commandInput[2],'Containers'):
        updateText(openRoom(playerData['location'],'Containers')[commandInput[2]]['Locked']['LockMessage'])
    try:
        getItem = [x for x in openRoom(playerData['location'],'Containers')[commandInput[2]]['Items'] if x['Name'] == commandInput[1]]
        if len(uuidCompare(getItem, inventoryData)) != 0:
            inventoryData.append(getItem[0])
            updateText('You pick up the '+commandInput[1]+'.')
        else:
            updateText('You already have the ' + commandInput[1] + '.')
    except KeyError:
        updateText('You can\'t seem to find a' + grammarAn(commandInput[2]) + '.')
    except IndexError:
        updateText('You can\'t seem to find a'+grammarAn(commandInput[1]+' in the '+commandInput[2]+'.'))

def uuidCompare(list1, list2):
    sameItems = []
    validItems = list1
    for item in list1:
        for otherItem in list2:
            if item['UUID'] == otherItem['UUID']:
                sameItems.append(item)
    for item in sameItems:
        validItems.remove(item)
    return validItems

def openRoom(loc, var):
    roomfile=''
    for num in range(0,3):
        roomfile=roomfile+str(hex(loc[num])[2:])
    try:
        with open(roomfile+'.json','r') as f:
            roomdata = json.load(f)
            return roomdata[var]
    except FileNotFoundError:
        updateText('ERR: room file '+roomfile+'.json does not exist')

def quitGame():
    pickle.dump(playerData,open('playerData.pkl','wb'))
    pickle.dump(inventoryData,open('inventoryData.pkl','wb'))
    root.destroy()
    sys.exit('Quiting...')

commandslist = {'move':movePlayer, 'go':movePlayer, 'quit':quitGame,'exit':quitGame, 'inspect':inspect, 'look':inspect, 'open':openContainer, 'get':getItem}

def updateText(string):
    output['text']=string

def playerEntry(event):
    global commandInput
    commandInput=entry.get().casefold().split(' ')
    entry.delete(0,len(entry.get()))
    for item in commandInput:
        if item=="the":
            commandInput.remove(item)
    try:
        commandaction = commandslist[commandInput[0].lower()]
    except KeyError:
        updateText('Command not recognized')
    try:
        commandaction()
    except UnboundLocalError:
        pass

if __name__ == '__main__':
    commandInput=[]
    try:
        playerData = pickle.load(open('playerData.pkl','rb'))
    except FileNotFoundError:
        print('Player data not found')
    try:
        inventoryData = pickle.load(open('inventoryData.pkl','rb'))
    except FileNotFoundError:
        print('Inventory data not found')
    
    root = tkinter.Tk() 
    entry = tkinter.Entry(root)
    output = tkinter.Label(root,text=openRoom(playerData['location'],'Name') + '\n' + openRoom(playerData['location'],'Description'))
    output.pack()
    entry.pack()
    root.bind('<Return>', playerEntry) 
    root.mainloop() 