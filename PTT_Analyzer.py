#!/usr/bin/env python
import sqlite3
import operator
import os
import numpy
from math import log

__limit__ = 10000
# 3000 for performance issue
# -1 for no limit
# up to about 100,000

con = sqlite3.connect('PTT_Parser.db')
c = con.cursor()

# boardDict:
#   key (string): board
#   value (dict): 3-element list
#       dict:
#	    key (string): author
#	    value (int): count
#       dict: TF, then TF*IDF (autIdx to float)
#       int: articleNumber
boardDict = {}

authorSet = set()

selectSql = 'SELECT * FROM BAP'
if __limit__ > 0: selectSql += " LIMIT " + str(__limit__)
for row in c.execute(selectSql):
    board = row[1]
    author = row[2]
    lst = boardDict.setdefault(board, [{}, {}, 0])
    lst[0][author] = lst[0].get(author, 0) + 1
    authorSet.add(author)
    lst[2] += 1

authorList = list(authorSet)
authorNum = len(authorList)

#TF
for brd in boardDict:
    dic = boardDict[brd][0]
    TF = boardDict[brd][1]
    artNum = boardDict[brd][2]
    for i in range(authorNum):
        if authorList[i] in dic:
            TF[i] = TF.get(i, 0) + 1
#            TF.append( float(dic.get(authorList[i], 0)) / artNum )


#IDF
IDF = []
boardNumF = float(len(boardDict))
for aut in authorList:
    cnt = 0
    for tpl in boardDict.values():
        if aut in tpl[0]: #author wrote some in the board
            cnt += 1
    IDF.append( log(boardNumF / cnt) )

#TF -> TF*IDF
for tpl in boardDict.values():
    for i in tpl[1]:
        tpl[1][i] *= IDF[i]
#    TF = tpl[1]
#    result = TF
#    for i in range(len(result)):
#        result[i] *= IDF[i]
    nrm = numpy.linalg.norm(list(tpl[1].values()))
#    result = [ x / nrm for x in result ]
#    tpl[1] = result
    for i in tpl[1]:
        tpl[1][i] /= nrm


# Example: 'travel' to others
cnt = 0
total = len(boardDict)
for brdBase in boardDict:
    cnt += 1
    print(str(cnt) + '/' + str(total) + '\t' + brdBase + ":")

    myDic = {} #board to cosine
    for brd in boardDict:
        if brd == brdBase: continue
#        myDic[brd] = numpy.dot(boardDict[brd][1], boardDict[brdBase][1])
        myDic[brd] = 0
        for i in boardDict[brd][1]:
            if i in boardDict[brdBase][1]:
                myDic[brd] += boardDict[brd][1][i] * boardDict[brdBase][1][i]

    myList = []
    for k,v in myDic.items():
        myList.append( (v,k) )
    myList.sort(reverse=True)
    for tpl in myList:
        if not tpl[0] == 0:
            print('\t', tpl[1], '\t', tpl[0])



