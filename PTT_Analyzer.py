#!/usr/bin/env python
import sqlite3
import operator
import os

con = sqlite3.connect('PTT_Parser.db')
c = con.cursor()

# authorDict:
#   key (string): author
#   value (dict): dict:
#	key (string): board
#	value (int): count

authorDict = {}

for row in c.execute('SELECT * FROM BAP'):
    board = row[1]
    author = row[2]
    dic = authorDict.setdefault(author, {})
    dic[board] = dic.get(board, 0) + 1

#for k,v in authorDict.items():
#    print(k, v)

# corrDict: dict
#   key(pair of string): (brd1, brd2) with brd1 < brd2
#   value: count

corrDict = {}
for author, boardDict in authorDict.items():
    boardList = boardDict.items()
    brdNum = len(boardList)
    if brdNum == 1: continue
    for i in range(0, brdNum-1):
	for j in range(i+1, brdNum):
	    brdA = boardList[i][0]
	    brdB = boardList[j][0]
	    addWeight = min(boardList[i][1] , boardList[j][1])
	    if brdA > brdB:
		brdB, brdA = (brdA, brdB)
	    corrDict[(brdA, brdB)] = corrDict.get((brdA, brdB),0) + addWeight

#for k, v in corrDict.items():
#    print(k, v)
sortedCorr = sorted(corrDict.items(), key=operator.itemgetter(1))
for elem in sortedCorr:
    print(elem)

def addToRecDict(ba, bb, cnt, recDict):
    dic = recDict.setdefault(ba, {})
    dic[bb] = dic.get(bb, 0) + cnt
    dic = recDict.setdefault(bb, {})
    dic[ba] = dic.get(ba, 0) + cnt

recDict = {}
for brdP, count in corrDict.items():
    addToRecDict(brdP[0], brdP[1], count, recDict)

#for k, v in recDict.items():
#    print(k)
#    print(v)

# Compute average indegree for every node
nBrd = len(recDict.items())
avgDeg = {}
for k, v in recDict.items():
    s = 0
    for i in v.values():
	s += i
    avgDeg[k] = float(s) / nBrd

if not os.path.exists('data'):
    os.makedirs('data')

for brd in recDict:
    outputList = []
    for k, v in recDict[brd].items():
	outputList.append( (v/(1+avgDeg[k]), v, k.encode('utf8')) )
    outputList.sort(reverse=True)

    fh = open('data/' + brd.encode('utf8') + '.data', 'w')
    fh.write('board\tdegree\tnordegree\n')
    for tup in outputList:
	fh.write(tup[2]+'\t'+str(tup[1])+'\t'+str(tup[0])+'\n')

#    for k,v in recDict[brd].items():
#	fh.write(k.encode('utf8') + '\t' + str(v) +
#	'\t' + str(v / avgDeg[k]) + '\n')

