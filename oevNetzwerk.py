#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from operator import itemgetter
import time
import csv

nodeDict = {}
nodeD = {}
edgeList = []
edgeL = []
stationList = []
networkList = []
networkNodeDict = {}

startNode = 'A'
endNode = 'D'

# alle nodes abfuellen mit ID, CoordinateX, CoordinateY, Distance(maximaler Wert), Visited (0), Previous ([startNode])
nodeDict = {'A':[0,0,sys.maxsize,0,[]], 'B':[0,1,sys.maxsize,0,[]], 'C':[1,1,sys.maxsize,0,[]], 'D':[1,2,sys.maxsize,0,[]]}

# alle edges abfuellen mit ID, ID Node From, ID Node To, Weight
edgeList.append(['a','A','B',2])
edgeList.append(['b','A','C',4])
edgeList.append(['c','B','C',13])
edgeList.append(['d','C','D',3])
edgeList.append(['e','B','D',14])

def buildListFromCSV(csvFile):
    with open(csvFile, newline='', encoding='utf-8') as csvfile:
        csvLine = csv.reader(csvfile, delimiter=',', quotechar='"')
        next(csvLine)
        i = 0
        #Schreibt Werte in list
        for row in csvLine:
            tripID = row[6]
            # parent Station nehmen, wenn existiert
            if row[5] != '':
                stopID = row[5]
            else:
                stopID = row[0]
            time = row[7]
            xcoord = row[2]
            ycoord = row[3]
            stationList.append([i,tripID,stopID,time,float(xcoord),float(ycoord)])
            i+=1
    return stationList
    
def exportCSV(filename,csvList,numberCharacter):
    with open(filename, 'w', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',', quotechar='|')
        if numberCharacter == 1:
            for row in csvList:
                csvwriter.writerow([str(row[0])])
        if numberCharacter == 2:
            for row in csvList:
                csvwriter.writerow([str(row[0])]+[str(row[1])])
        if numberCharacter == 3:
            for row in csvList:
                csvwriter.writerow([str(row[0])]+[str(row[1])]+[str(row[2])])
        if numberCharacter == 4:
            for row in csvList:
                csvwriter.writerow([str(row[0])]+[str(row[1])]+[str(row[2])]+[str(row[3])])
        if numberCharacter == 5:
            for row in csvList:
                csvwriter.writerow([str(row[0])]+[str(row[1])]+[str(row[2])]+[str(row[3])]+[str(row[4])])
        if numberCharacter == 6:
            for row in csvList:
                csvwriter.writerow([str(row[0])]+[str(row[1])]+[str(row[2])]+[str(row[3])]+[str(row[4])]+[str(row[5])])
        if numberCharacter == 8:
            for row in csvList:
                csvwriter.writerow([str(row[0])]+[str(row[1])]+[str(row[2])]+[str(row[3])]+[str(row[4])]+[str(row[5])]+[str(row[6])]+[str(row[7])])

 
def buildNetworkEdge(stationList): # Verbindung auch zwischen den Linien
    sorted(stationList, key=itemgetter(1,3))
    lastStopID = ''
    lastTripID = ''
    lastTime = ''
    # Start - Ziel Kombination bilden
    for row in stationList:
        if lastStopID != '' and row[1] == lastTripID:
            startID = lastStopID
            targetID = row[1]+"-"+row[2]
            timeDepart = time.mktime(time.strptime(lastTime, "%H:%M:%S"))
            timeArrival = time.mktime(time.strptime(row[3], "%H:%M:%S"))
            cost = timeArrival - timeDepart
            networkList.append([row[1], startID, targetID, cost])
        lastStopID = row[1]+"-"+row[2]
        lastTripID = row[1]
        lastTime = row[3]
    return networkList
    
def buildNetworkNode(stationList):
    sorted(stationList, key=itemgetter(1,3))
    lastStopID = ''
    lastTripID = ''
    lastTime = ''
    lastX = ''
    lastY = ''
    # alle nodes abfuellen mit ID, CoordinateX, CoordinateY, Distance(maximaler Wert), Visited (0), Previous ([startNode])
    for row in stationList:
        if row[1] != lastTripID:
            # Wenn neuer Trip beginnt, erster Node einfuegen
            networkNodeDict[row[1]+"-"+row[2]] = [row[4],row[5],sys.maxsize,0,[]]
        if lastStopID != '' and row[1] == lastTripID:
            startID = lastStopID
            targetID = row[1]+"-"+row[2]
            networkNodeDict[targetID] = [row[4],row[5],sys.maxsize,0,[]] 
        lastStopID = row[1]+"-"+row[2]
        lastTripID = row[1]
    return networkNodeDict
        

def nextStep(eList):
    edgeTempList=[]
    lastNode = ''
    # start node finden und Distance auf 0, Visited auf 1
    for node in nodeDict:
        # start node setzten
        if node == startNode and nodeDict[node][3]==0:
            nodeDict[node][2]=0
            nodeDict[node][3]=1
            break
        # alle nodes, die besucht wurden
        if nodeDict[node][3]==1:
            for edge in eList:
                # edges, die einen besuchten node enthalten in edgeTempList schreiben
                if edge[1]==node or edge[2]==node:
                    # edges, die an einen unbesuchten node grenzen
                    if nodeDict[edge[1]][3]==0 or nodeDict[edge[2]][3]==0:
                        # wenn from to nodes in edges stimmen sonst die node-Bezeichnungen getauscht werden, ausserdem Distance-Wert = Distance in node + Weight in edge
                        if edge[1]==node:
                            edgeTempList.append([edge[0],edge[1],edge[2],(edge[3]+nodeDict[edge[1]][2])])
                        else:
                            edgeTempList.append([edge[0],edge[2],edge[1],(edge[3]+nodeDict[edge[2]][2])])
    # edges in edgeTempList sortieren nach Weight und To-Wert in Node aktualisieren
    if not edgeTempList == [] :
        sortedTempList = sorted(edgeTempList, key=itemgetter(3))
        nodeDict[sortedTempList[0][2]][2]=sortedTempList[0][3]
        nodeDict[sortedTempList[0][2]][3]=1
        if not nodeDict[sortedTempList[0][1]][4] == []:
            # fuer alle bisherigen vor-nodes
            i=0
            for n in nodeDict[sortedTempList[0][1]][4]:
                nodeDict[sortedTempList[0][2]][4].append(nodeDict[sortedTempList[0][1]][4][i])
                i+=1
        nodeDict[sortedTempList[0][2]][4].append(sortedTempList[0][1])
        lastNode = (sortedTempList[0][2])
    return(lastNode)
    
def nextStep2(eList):
    edgeTempList=[]
    lastNode = ''
    # start node finden und Distance auf 0, Visited auf 1
    for node in networkListNode:
        # start node setzten
        if node == startNode and networkListNode[node][3]==0:
            networkListNode[node][2]=0
            networkListNode[node][3]=1
            #break
        # alle nodes, die besucht wurden
        if networkListNode[node][3]==1:
            for edge in eList:
                # edges, die einen besuchten node enthalten in edgeTempList schreiben
                if edge[1]==node or edge[2]==node:
                    # edges, die an einen unbesuchten node grenzen
                    if networkListNode[edge[1]][3]==0 or networkListNode[edge[2]][3]==0:
                        # wenn from to nodes in edges stimmen sonst die node-Bezeichnungen getauscht werden, ausserdem Distance-Wert = Distance in node + Weight in edge
                        if edge[1]==node:
                            edgeTempList.append([edge[0],edge[1],edge[2],(edge[3]+networkListNode[edge[1]][2])])
                        else:
                            edgeTempList.append([edge[0],edge[2],edge[1],(edge[3]+networkListNode[edge[2]][2])])
    # edges in edgeTempList sortieren nach Weight und To-Wert in Node aktualisieren
    if not edgeTempList == [] :
        sortedTempList = sorted(edgeTempList, key=itemgetter(3))
        networkListNode[sortedTempList[0][2]][2]=sortedTempList[0][3]
        networkListNode[sortedTempList[0][2]][3]=1
        if not networkListNode[sortedTempList[0][1]][4] == []:
            # fuer alle bisherigen vor-nodes
            i=0
            for n in networkListNode[sortedTempList[0][1]][4]:
                networkListNode[sortedTempList[0][2]][4].append(networkListNode[sortedTempList[0][1]][4][i])
                i+=1
        networkListNode[sortedTempList[0][2]][4].append(sortedTempList[0][1])
        lastNode = (sortedTempList[0][2])
    return(lastNode)

stopList = buildListFromCSV('tempStopTrip_small.csv')
networkListEdge = buildNetworkEdge(stopList)
networkListNode = buildNetworkNode(stopList)
exportCSV('tempNetwork.csv',networkListEdge,4)
newList=[]
#for e in networkListNode:
#    newList.append([e,networkListNode[e]])

startNode = '1.TA.1-1-B-j18-1.1.H-8500010P' #'1.TA.1-1-A-j18-1.1.H-8503000P'
endNode = '1.TA.1-1-A-j18-1.1.H-8502114P' #'1.TA.1-1-A-j18-1.1.H-8500309P'
'''
Da es mehrere gleiche Nodes bei den Umsteigepunkten gibt, braucht es auch mehrere Edges
Ort der Umsteigepunkte kann mit einer List seen überprüft werden, da braucht es neuen edge
'''

while (networkListNode[endNode][3]==0):
    lastNode=nextStep2(networkListEdge)
cost = networkListNode[endNode][2]
way = networkListNode[endNode][4]
way.append(lastNode)
print("Kosten: "+str(cost))
print("Weg: "+str(way))



'''
startNode = 'A'
endNode = 'D'
print(nodeDict)
while (nodeDict[endNode][3]==0):
    lastNode=nextStep(edgeList)
    #print(nodeDict['D'])
cost = nodeDict[endNode][2]
way = nodeDict[endNode][4]
way.append(lastNode)
print("Kosten: "+str(cost))
print("Weg: "+str(way))
'''



 
    
    
