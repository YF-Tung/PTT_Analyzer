#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import sqlite3
import requests
import time

reload(sys)
sys.setdefaultencoding('utf-8')
con = sqlite3.connect('PTT_Parser.db')
c = con.cursor()

START_PAGE = 1
if len(sys.argv) > 1:
    START_PAGE = int(sys.argv[1])
    print('Starting from page %d' % START_PAGE)

#c.execute('DELETE FROM BoardAuthorPair')

freqDict = {} # (board, author) -> count


MAX_PAGE = -1 #default value

lines = requests.get('https://www.ptt.cc/bbs/ALLPOST/index.html').text.split()
target = u'/bbs/ALLPOST/index' # byte string
for line in lines:
	print(line)
	line = unicode(line) # unicode string
	if line.find(target) > -1:
		lpos = line.find('index') + 5
		rpos = line.find('.html')
		if rpos - lpos < 2: continue # not the target
		MAX_PAGE = int(line[lpos:rpos]) + 1
		print("Total", MAX_PAGE, "pages.")
		break

# reset MAX_PAGE to 3 (to avoid overuse)
#MAX_PAGE = 3

for i in range(START_PAGE, MAX_PAGE):
	print('Getting page', i, 'out of', MAX_PAGE, '...')
	sys.stdout.write('\r')
	sys.stdout.flush()
	txt = requests.get('https://www.ptt.cc/bbs/ALLPOST/index' + str(i) + '.html').text
	
	
	board = "_default_"
	author = "_default_"
	
	lines = txt.split('\n')
	for line in lines:
		line = line.strip()
		#print(line)
		if line.startswith('<a href'): #update board
			lpos = line.rfind('(') + 1
			rpos = line.rfind(')')
			board = line[lpos:rpos]
			#print ('board:', board)
		if line.startswith('<div class="author"'): #update author, then add count to freqDict
			lpos = line.find('>') + 1
			rpos = line.rfind('<')
			author = line[lpos:rpos]
#			freqDict[(board, author)] = freqDict.get((board, author), 0) + 1
			c.execute('''INSERT INTO BoardAuthorPair (board, author)
					VALUES ( ?, ?)''', (board, author) )
			#print('author:', author)
			#print('Find a pair: (board =', board, ', author = ', author)
	
	#txtArr.append(txt)
	con.commit()
	time.sleep(1)
	
	
#for k in freqDict:
#	print(k,'-->', freqDict[k])
#
#print('------------------------------------------------')
#for k in freqDict:
#	for k2 in freqDict:
#		if k[1] == k2[1] and k[0] < k2[0]:
#			print("Association between", k[0], 'and', k2[0], 'found. Count:', freqDict[k], 'x', freqDict[k2])
#

con.commit()
