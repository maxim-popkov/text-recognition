#!/usr/bin/python
# -*- coding: utf-8 -*-
from nltk.corpus import reuters
import nltk  
import sys, re, operator

class WordStats(object):
	"""docstring for WordStats"""
	def __init__(self):
		super(WordStats, self).__init__()
		self.idf = 0
		self.txts = {}
		self.categories = {}
		self.word = ''

	def addText(self,txtId, stats, categories='None'):
		#check (comment this for best perfomance)
		if txtId not in self.txts:
			self.txts[txtId] = stats
			self.addIdf(1)
			self.addCategory(categories, stats)
		else:
			self.txts[txtId] +=stats

	def addIdf(self, idf):
		self.idf = self.idf + idf

	def addCategory(self, categories, tf):
		for category in categories:
			if category not in self.categories:
				self.categories[category] = tf
			else:
				self.categories[category] += tf

	def __str__(self):
		return self.__unicode__()

	def __unicode__(self):
		result = '\nWord: ' + self.word
		result += '\nTxts: ' + str(self.txts)
		result += '\nIDF: ' + str(self.idf)
		result += '\nCategories: ' + str(self.categories)
		return result

class Spider(object):
	"""Class Spider: Read info from sources, and compute stats"""
	def __init__(self):
		super(Spider, self).__init__()
		self.wordsStatDict = {}
		self.topWords = set([])
		self.activeCategories = []
		self.classifier = None

	def computeStats(self, categories):
		files = batchReadReuters('training', categories)
		for file_name in files:
			raw_txt = readFromFile('/home/dales3d/nltk_data/corpora/reuters/' + file_name)
			fileCategories = reuters.categories(file_name)
			#for cat in categories:
			#	if cat not in self.activeCategories:
			#		self.activeCategories.append(cat)
			self.activeCategories = categories

			words = extractWords(raw_txt)
			keywords = meter(words)
			for word in keywords:
				if word not in self.wordsStatDict:
					self.wordsStatDict[word] = WordStats()	
				w_stat = self.wordsStatDict[word] 
				w_stat.word = word
				w_stat.addText(file_name,keywords[word], fileCategories)
	
	def getCategoryTop(self, category):
		words = {}
		for word in self.wordsStatDict:
			for cat in self.wordsStatDict[word].categories:
				if category == cat:
					words[word] = self.wordsStatDict[word].categories[category] # / self.wordsStatDict[word].idf 
		sorted_x = sorted(words.iteritems(), key=operator.itemgetter(1), reverse=True)
		for word in sorted_x[:100]:
			self.topWords.add(word[0])
		return self.topWords

	def collectTopWords(self):
		"""Collect for each category its top words and append to entire result"""
		for category in self.activeCategories:
			self.getCategoryTop(category)
	
	def getCatLen(self):
		return len(reuters.categories())

	def getFileFeatures(self, file_name):
		raw_txt = readFromFile('/home/dales3d/nltk_data/corpora/reuters/' + file_name)
		words = extractWords(raw_txt)
		keywords = meter(words)
		# ###Test IDF
		# for word in keywords:
		# 	if word in self.wordsStatDict:
		# 		#print word
		# 		keywords[word] = keywords[word] / self.wordsStatDict[word].idf 
		# ###
		sorted_x = sorted(keywords, key=lambda key: keywords[key], reverse=True)
		features = {}
		for word in self.topWords:
			features[word] = (word in sorted_x)
		return features

	def train(self):
		training_set = []
		print self.activeCategories
		for category in self.activeCategories:
			files = reuters.fileids(category)
			for fi in files:
				training_set.append((self.getFileFeatures(fi),category))
		self.classifier = nltk.NaiveBayesClassifier.train(training_set)
		
	def test(self, testFile):
		####test/15618
		test_feat = self.getFileFeatures(testFile)
		print test_feat
		result = self.classifier.classify(test_feat)
		# self.classifier.labels()
		# self.classifier.most_informative_features()
	 # 	probs = self.classifier.prob_classify(test_feat)
		# for sample in probs.samples():
		# 	print sample + " " + "%.3f"%(probs.prob(sample))
		return result

	def testCategories(self, categories):
		files = batchReadReuters('test', categories)
		results = []
		for testFile in files:
			result = self.test(testFile)
			results.append((testFile,result))
		return results			


	def __str__(self):
		return self.__unicode__()

	def __unicode__(self):
		result = ''
		for word in self.wordsStatDict:
			result += '\n----------- '+word+' ----------------'
			result += str(self.wordsStatDict[word])
		result += str(len(self.wordsStatDict))
		return result

def computePercent(results, category):
	match = 0
	for fileId, result in results:
		if result == category:
			match = match + 1
	return 100.0 * match / len(results)

def batchRead():
	#STUB
	files = reuters.fileids()
	tags = ['training','test']
	training_files = []

	for file_name in files:
		entry = file_name.strip().split('/', 2)
		if len(entry) != 2:
			continue
		element, value = entry[0], entry[1]
		if element == 'training':
			training_files.append(file_name)
	return training_files

def batchReadReuters(collection, categories):
	#STUB
	files = reuters.fileids(categories)
	tags = ['training','test']
	training_files = []

	for file_name in files:
		entry = file_name.strip().split('/', 2)
		if len(entry) != 2:
			continue
		element, value = entry[0], entry[1]
		if element == collection:
			training_files.append(file_name)
	return training_files
	
def readFromFile(sourceFile):
	"""Read .srt file and return string"""
	with open(sourceFile,"r") as f_in:
		txt = ""
		txt = f_in.read()
		f_in.close()

	return txt
	
def extractWords(sourceTxt):
	"""Extract words from string and return words array"""
	words = [] 
	pattern = r'[^\W\d]+'
	words.extend(re.findall(pattern,sourceTxt.lower(),re.U))

	return words 

def meter(wordsList):
	"""Meter count words in wordsList and return dict with stats"""
	keywords = {}
	for word in wordsList:
		if word not in keywords:
			keywords[word] = 1
		else:
			keywords[word] += 1
	return keywords

def writeToFile(outFile, keywords):
	"""writeToFile"""
	with open(outFile,"w") as f_out:
		result = ""

		sorted_x = sorted(keywords.iteritems(), key=operator.itemgetter(1), reverse=True)
		result = "There are " + str(len(keywords)) + " unique words in file '" + "\n"
	 #   result += "There are " + str(len(words_list)) + " words in file '" + input_file + "'" + "\n"
		for item in sorted_x:
			result += item[0] + " | " + str(item[1]) + "\n"
		f_out.write(result)
		f_out.close()

def categorizeReuters(sourceFile):
	"""return categories array (tuple [txtName, category])"""
	txt = readFromFile(sourceFile)
	
def save_classifier(classifier):
   f = open('my_classifier.pickle', 'wb')
   pickle.dump(classifier, f, -1)
   f.close()

def load_classifier():
   f = open('my_classifier.pickle', 'rb')
   classifier = pickle.load(f)
   f.close()
   return classifier

#from nltk.corpus import reuters
#reuters.categories('training/9865')
#['barley', 'corn', 'grain', 'wheat']
#reuters.fileids()
#['test/14826', 'test/14828', 'test/14829', 'test/14832', ...]
