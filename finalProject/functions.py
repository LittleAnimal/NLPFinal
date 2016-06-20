from linggle_api import linggleit
from sqlite import bncTag
from itertools import izip
from operator import itemgetter
import re
import en
import math
import copy

# prep_list is a list, use prep_list.count('prep') to check whether prep is in list, 0 is null, 1 is prep
prep_list = []
findlen = 5

###############################################################################################
# 
# Name: Main Function
# Programmer: TiYu - Chou
# Time: 2016/06/14
# 
###############################################################################################

# main function 
def checkGramma(text):

	# Step0: initialize preposition list
	getPrep()


	print '---------------------------------  preposition list  ---------------------------------'
	print ', '.join(prep_list)
	print '--------------------------------------------------------------------------------------'

	print '----------------------------------  input sentence  ----------------------------------'
	print  text
	print '--------------------------------------------------------------------------------------'

	# Step1: cut words and get tags
	inputsentence, wordInfo = getwordInfo(text)

	print '-------------------------------------  wordInfo  -------------------------------------'
	print ' '.join([str(i) for i in wordInfo])
	print '--------------------------------------------------------------------------------------'

	# Step2: construct linggle search words
	searchwords = wordsPacket(wordInfo)

	print '------------------------------------  search key  ------------------------------------'
	print '\n'.join([str(i) for i in searchwords])
	print '--------------------------------------------------------------------------------------'

	# Step3: get appearance times from linggles
	appearance = getFrequency(searchwords)

	print '---------------------------------  suggestion list  ----------------------------------'
	print '\n'.join([str(i) for i in appearance])
	print '--------------------------------------------------------------------------------------'

	# Change the words
	newresult = changeWords(inputsentence, appearance)

	print '----------------------------------  change result  -----------------------------------'
	print newresult
	print '--------------------------------------------------------------------------------------'

	return newresult, appearance


###############################################################################################
#
# Step 1: input sentences and return cut words and their tags
#
###############################################################################################

# step 1's root function
def getwordInfo(text):
	words_all = text.strip().split(' ')

	tags_all = bncTag(words_all)
	wordInfo = []
	for word, tag, index in izip(words_all, tags_all, range(len(words_all))):
		if tag.startswith('n'):
			word = en.noun.singular(word)
		elif tag.startswith('v') and word!='is' and word!='are' and word!='been':
			word = en.verb.present(word)

		wordInfo.append((word, tag, index))
	return words_all, wordInfo

#  make prep list
def getPrep():
	for line in file('prep.txt'):
		if line[-1] == '\n':
			prep_list.append(line[:-1])
		else: 
			prep_list.append(line)


###############################################################################################
# 
# Step 2: input words and return the key words of each three words
# 
###############################################################################################

# step 2's root function
def wordsPacket(wordInfo):
	# first:  find preposition in the sentence
	keywords = [calLCRC(wordInfo, i) for i in range(len(wordInfo)) if prep_list.count(wordInfo[i][0]) > 0]
	# second: for each word find a pair for them
	keywords2 =  [ calRPair(wordInfo, i) for i in range(len(wordInfo)-1) \
		if prep_list.count(wordInfo[i][0]) == 0 and (wordInfo[i][1].startswith('a') or wordInfo[i][1].startswith('n') \
			or wordInfo[i][1].startswith('v')) and( wordInfo[i][0]!='is' or wordInfo[i][0]!='are' or wordInfo[i][0]!='been')]
	return keywords + keywords2

# find left and right the closest n, v, adj words
def calLCRC(wordInfo, num):
	LC = [ (word, index) for word, wordTag, index in wordInfo[:num] if wordTag.startswith('a') or wordTag.startswith('n') or wordTag.startswith('v')]
	RC = [ (word, index) for word, wordTag, index in wordInfo[(num+1):] if wordTag.startswith('a') or wordTag.startswith('n') or wordTag.startswith('v')\
		or wordTag.startswith('U')]
	if len(LC) == 0 :
		LC.append(('', (-1, -1)))
	if len(RC) == 0 :
		RC.append(('', (-1, -1)))
	return (LC[-1], (wordInfo[num][0], wordInfo[num][2]), RC[0])

# find two words for a pair
def calRPair(wordInfo, num):
	RC = [ (word, index) for word, wordTag, index in wordInfo[(num+1):(num+1+findlen)] \
		if wordTag.startswith('a') or wordTag.startswith('n') or wordTag.startswith('v') or wordTag.startswith('U')]
	if len(RC) == 0:
		RC.append(('', (-1. -1)))
	return ((wordInfo[num][0], wordInfo[num][2]), '', RC[0])


###############################################################################################
# 
# Step 3: input pairs and return the score of linggle
# 
###############################################################################################

# step 3's root function
def getFrequency(searchwords):
	# print 'start getFrequency'

	print '--------------------------------  get linggle result  --------------------------------'
	

	results = []
	for items in searchwords:

		if items[0][0] == '' or items[2][0] == '':
			continue
		else:

			res = linggleit(items[0][0]+' ?prep. '+items[2][0])
			res2 = linggleit(items[0][0] + ' prep.')
			
			total = sum([freq for word, freq in res])
			total2 = sum([freq for word, freq in res2])

			res = [ (word, float(freq)/total) for word, freq in res]
			res2 = [ (word, float(freq)/total2) for word, freq in res2]

			if total2 / total > 1000:
				res_all = res2
			else:
				res_all = sorted(res+res2, key=itemgetter(1), reverse=True)

			print res_all[:5]

			if items[1] is '': 
				for x in res:
					if x[0] == items[0][0] + ' ' + items[2][0]:
						break
					else:
						results.append((x[0].split(' '), [items[0][0], items[2][0]], [items[0][1], items[2][1]],  x[1]))
						break
			else: 
			# check if the highest prep is items[1][0], then the word is right
				for x in res_all:
					if x[0] == items[0][0] + ' ' + items[1][0] + ' ' + items[2][0]:
						break
					else:
						txt = '{:.4f}'.format(x[1])
						results.append((x[0].split(' '),[items[0][0], items[1][0], items[2][0]], [items[0][1], items[1][1], items[2][1]],txt))
						break
	print '--------------------------------------------------------------------------------------'
	return results


###############################################################################################
# 
# Other function
# 
###############################################################################################
def changeWords(words, changeInfo):
	# print 'start ChangeWords:'

	results = copy.copy(words) # copy with pass by value

	for info in changeInfo:
		# print info
		# print len(info[2])
		# print len(info[0])

		if len(info[2]) == 3 and len(info[0]) == 3:
			# use wrong prep (RT)
			if info[2][2]-info[2][0] == 2:
				results.remove(info[1][1])
				results[info[2][0]] = words[info[2][0]] + ' ' + info[0][1]
			else:
				results[info[2][1]] = info[0][1]
		elif len(info[2]) == 2 and len(info[0]) == 3:
			# shoule add prep (MT)
			results[info[2][0]] = words[info[2][0]] + ' ' + info[0][1]

		elif len(info[2]) == 3 and len(info[0]) == 2:
			# remove prep (UT)
			if info[0][0]==info[1][0] and info[0][1]==info[1][2]:
				results.remove(info[1][1])
			else:
				if info[2][2]-info[2][0] == 2:
					results.remove(info[1][1])
					results[info[2][0]] = words[info[2][0]] + ' ' + info[0][1]
				else:
					results[info[2][1]] = info[0][1]

		elif len(info[2]) == 2 and len(info[0]) == 2:
			results[info[2][0]] = words[info[2][0]] + ' ' + info[0][1]

	newWords = ' '.join(results)
	return newWords
