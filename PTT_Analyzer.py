#!/usr/bin/env python
import sqlite3
import operator
import os
import numpy

con = sqlite3.connect('PTT_Parser.db')
c = con.cursor()

# boardDict:
#   key (string): board
#   value (dict): 3-element list
#       dict:
#	    key (string): author
#	    value (int): count
#       list: TF, then TF*IDF
#       int: articleNumber
boardDict = {}

authorSet = set()

for row in c.execute('SELECT * FROM BAP LIMIT 1000'):
    board = row[1]
    author = row[2]
    tpl = boardDict.setdefault(board, [{}, [], 0])
    dic = tpl[0]
    dic[author] = dic.get(author, 0) + 1
    authorSet.add(author)
    tpl[2] += 1

authorList = list(authorSet)
authorNum = len(authorList)

#TF
for brd in boardDict:
    dic = boardDict[brd][0]
    TF = boardDict[brd][1]
    artNum = boardDict[brd][2]
    for i in range(authorNum):
        TF.append( float(dic.get(authorList[i], 0)) / artNum )

#IDF
IDF = []
boardNumF = float(len(boardDict))
for aut in authorList:
    cnt = 0
    for tpl in boardDict.values():
        if aut in tpl[0]: #author wrote some in the board
            cnt += 1
    IDF.append( boardNumF / cnt )

#TF -> TF*IDF
for tpl in boardDict.values():
    TF = tpl[1]
    result = TF
    for i in range(len(result)):
        result[i] *= IDF[i]
    nrm = numpy.linalg.norm(result)
    result = [ x / nrm for x in result ]


# Example: 'travel' to others
print('travel' in boardDict)

myDic = {} #board to cosine
for brd in boardDict:
    if brd == 'travel': continue
    myDic[brd] = numpy.dot(boardDict[brd][1], boardDict['travel'][1])
print(myDic)

myList = []
for k,v in myDic.items():
    myList.append( (v,k) )
myList.sort(reverse=True)
for tpl in myList:
    if not tpl[0] == 0:
        print(tpl[1], '\t', tpl[0])



