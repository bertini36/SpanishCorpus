#! /usr/bin/python
# coding=utf-8

__author__ = "Alberto Pou Quirós"

import sys
import time
import enchant

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.corpus import cess_esp
from nltk import FreqDist
from nltk.corpus import wordnet

from pattern.es import parse
from pattern.es import singularize
from pattern.es import conjugate
from pattern.es import INFINITIVE
from pattern.es import predicative


class SpanishCorpus:

	"""
	Class SpanishCorpus to ease text mining in spanish. 
	The objective of this library is generate a clean corpus of words based on a text in spanish.
	Attributes:
		_text: Original text provided in the initialization
		_tokens: Stores the result of the different filter functions
		_analysis: List of tuples with de lexical analysis result
		_synonyms: List of sets of synonyms of every word in tokens 
		_fdist: Instance of nltk.FreqDist
	The class functions are in the logical order to run
	"""

	word_tag_fd = FreqDist(cess_esp.tagged_words())
	levenshtein_distance = 1

	"""
	@param text: Original text
	@param timeit: True if you want timing the methods
	"""
	def __init__(self, text, timing=False):
		self._text = text
		self._tokens = None
		self._analysis = None
		self._synonyms = None
		self._fdist = None
		self.timing = timing

	@property
	def text(self):
		return self._text
	@text.setter
	def text(self, value):
		self._text = value

	@property
	def tokens(self):
		return self._tokens
	@tokens.setter
	def tokens(self, value):
		self._tokens = value

	@property
	def analysis(self):
		return self._analysis
	@analysis.setter
	def analysis(self, value):
		self._analysis = value

	@property
	def synonyms(self):
		return self._synonyms
	@synonyms.setter
	def synonyms(self, value):
		self._synonyms = value

	@property
	def fdist(self):
		return self._fdist.items()
	@fdist.setter
	def fdist(self, value):
		self._fdist = value

	def timing(method):
		def timed(self, *args, **kwargs):
			if self.timing:
				t_start = time.time()
				result = method(self, *args, **kwargs)
				t_end = time.time()
				print '%r --- %2.2f sec' % (method.__name__.ljust(25, ' '), t_end-t_start)
				return result
			else: result = method(self, *args, **kwargs)
		return timed
	
	"""
	Converts a text into a list of words 
	@return tokens
	"""
	@timing
	def tokenize(self):
		self._tokens = word_tokenize(self._text)
		return self._tokens

	"""
	Minimises words and filters not completely alpha words of tokens
	@return tokens
	"""
	@timing
	def clean(self):
		if not self._tokens: raise Exception('It\'s necessary execute first tokenize')
		self._tokens = [word.lower() for word in self._tokens if word.isalpha() and len(word)>2]
		return self._tokens

	"""
	Filters stopwords of tokens
	@return tokens
	"""
	@timing
	def filterStopwords(self):
		if not self._tokens: raise Exception('It\'s necessary execute first tokenize')
		spanish_stopwords = stopwords.words('spanish')
		self._tokens = [word for word in self._tokens if word not in spanish_stopwords]
		return self._tokens

	"""
	Calculates the Levenshtein's distance between two words
	@params s1, s2: Words to compare 
	@return number of differences
	"""
	@classmethod
	def levenshtein(cls, s1, s2):
		if len(s1) < len(s2): return SpanishCorpus.levenshtein(s2, s1)
		if len(s2) == 0: return len(s1)
		previous_row = range(len(s2) + 1)
		for i, c1 in enumerate(s1):
			current_row = [i + 1]
			for j, c2 in enumerate(s2):
				insertions = previous_row[j + 1] + 1 
				deletions = current_row[j] + 1       
				substitutions = previous_row[j] + (c1 != c2)
				current_row.append(min(insertions, deletions, substitutions))
			previous_row = current_row
		return previous_row[-1]

	"""
	Correct a word using enchant and the dictionary Nltk.cess_esp and the Levenshtein's distance
	@param token: Word to correct
	@return similar_word: Word closest
	"""
	@classmethod
	def correctWord(cls, token):
		suggested = (enchant.Dict('es')).suggest(token)
		if len(suggested) > 0: 
			for similar_word in suggested:
				if SpanishCorpus.levenshtein(token, similar_word) <= SpanishCorpus.levenshtein_distance:
					print u'--> Palabra corregida: {} --> {}'.format(token, similar_word)
					return similar_word
		minimum = sys.maxint
		similar_word = ''
		for word in cess_esp.words():
			lev_dist = SpanishCorpus.levenshtein(token, word)
			if (lev_dist < minimum) or (lev_dist == minimum \
				and len(word) == len(token) and len(similar_word) != len(token)):
				minimum = lev_dist
				similar_word = word
				if lev_dist == 0: break
		if minimum <= SpanishCorpus.levenshtein_distance: 
			print u'--> Palabra corregida: {} --> {}'.format(token, similar_word)
			return similar_word
		else: return None

	"""
	Detects the word's category using Nltk library. 
	@param token: Word to check category
	@param index: Word's index in tokens
	@return category
	"""
	def checkCategoryNltk(self, token, index):
		category = None
		for (wt, _) in SpanishCorpus.word_tag_fd.most_common(): 
			if token == wt[0]:
				category = wt[1].ljust(7, '0')
				if index >= len(self._analysis):
					self._analysis.append([token, category])
				else:
					self._tokens[index] = token
					self._analysis[index] = [token, category]
				break
		return category

	"""
	Detects the word's category using Pattern library (when pattern 
	library does't know the word it says that the word is a noun).
	@param token: Word to check category
	@param index: Word's index in tokens
	@return category
	"""
	def checkCategoryPattern(self, token, index):
		category = parse(token)
		if '/NN' in category: category = 'n'
		elif '/VB' in category: category = 'v'
		elif '/JJ' in category: category = 'a'
		elif '/CC' or '/CS' in category: category = 'c'
		elif '/P' in category: category = 'p'
		else: category = '-'
		if index >= len(self._analysis):
			self._analysis.append([token, category.ljust(7, '0')])
		else:
			self._tokens[index] = token
			self._analysis[index] = [token, category.ljust(7, '0')]
		return category

	"""
	Categorizes lexically a word. Initially it uses Nltk, 
	if it doesn't find the word's category it tries with Pattern library.
	If doesn't work and the word not is a foreign word 
	it tries to correct the word with enchant and cess_esp
	@param token: Word to analize
	@param index: Word's index in tokens
	@param to_correct: Indicates if it will try to correct word 
	"""
	def analizeWord(self, token, index, to_correct):
		category = self.checkCategoryNltk(token, index)
		if not category: 
			category = self.checkCategoryPattern(token, index)
			if to_correct and category == 'n' and any(c in ['a', 'e', 'i', 'o', 'u'] for c in token) \
					and not enchant.Dict("en").check(token) and not enchant.Dict("fr").check(token) \
					and not enchant.Dict("de_DE").check(token):
				new_token = SpanishCorpus.correctWord(token)
				if new_token and new_token != token: 
					self.analizeWord(new_token, index=index, to_correct=False)

	"""
	Returns a list of tuples of lexical analysis of tokens
	@param to_correct: Indicates if it will try to correct twords 
	@return Result of analysis
	"""
	@timing
	def analize(self, to_correct):
		if not self._tokens: raise Exception('It\'s necessary execute first tokenize')
		self._analysis = []
		for i in range(len(self._tokens)):
			token = self._tokens[i]
			self.analizeWord(token, index=i, to_correct=to_correct)
		return self._analysis

	"""
	Filters determinants, pronouns and conjunctions of tokens
	@return tokens
	"""
	@timing
	def cleanPostAnalysis(self):
		if not self._analysis: raise Exception('It\'s necessary execute first analize')
		new_tokens = []
		new_analysis = []
		new_synonyms = []
		for i in range(len(self._tokens)):
			if self._analysis[i][1][0] != 'd' \
					and self._analysis[i][1][0] != 'p' \
					and self._analysis[i][1][0] != 'c':
				new_tokens.append(self._tokens[i])
				new_analysis.append(self._analysis[i])
				if self._synonyms: new_synonyms.append(self.synonyms[i])
		self._tokens = new_tokens
		self._analysis = new_analysis
		self._synonyms = new_synonyms
		if self._fdist: self.calculateFrequencies()
		return self._tokens

	"""
	Singuralizes nouns, conjugates verbs to infinitive and passes adjectives to 
	predicative form in tokens
	@return tokens
	"""
	@timing
	def unifyTokens(self):
		if not self._analysis: raise Exception('It\'s necessary execute first analize')
		for i in range(len(self._tokens)):
			if self._analysis[i][1][0] == 'n':
				self._tokens[i] = singularize(self._tokens[i])
			elif self._analysis[i][1][0] == 'v':
				self._tokens[i] = conjugate(self._tokens[i], INFINITIVE)
			elif self._analysis[i][1][0] == 'a':
				self._tokens[i] = predicative(self._tokens[i])
		return self._tokens

	"""
	Returns a list of sets of synonyms of every word in tokens. Only searchs 
	synonyms of nouns and verbs
	@return synonyms
	"""
	@timing
	def synonymize(self):
		if not self._analysis: raise Exception('It\'s necessary execute first analize')
		self._synonyms = []
		for i in range(len(self._tokens)):
			if self._analysis[i][1][0] == 'n':
				synsets = wordnet.synsets(self._tokens[i], pos=wordnet.NOUN, lang='spa')
			elif self._analysis[i][1][0] == 'v':
				synsets = wordnet.synsets(self._tokens[i], pos=wordnet.VERB, lang='spa')
			else:
				synsets = None
			synonyms = []
			if synsets:
				for j in range(len(synsets)):
					synset = synsets[j].lemma_names('spa')
					for synonym in synset:
						if synonym != self._tokens[i] and synonym not in synonyms: 
							synonyms.append(synonym)
			self._synonyms.append([self._tokens[i], synonyms])
		return self._synonyms

	"""
	Returns a list of tuples where every word in tokens has its frequency
	of occurence
	@return frequencies
	"""
	@timing
	def calculateFrequencies(self):
		if not self._tokens: raise Exception('It\'s necessary execute first tokenize')
		self._fdist = FreqDist(self._tokens)
		return self._fdist.items()

	"""
	Shows the results of the study of corpus
	"""
	def showResults(self):
		print '***************** RESULTS *****************'
		print '1.- Original text: '
		print self._text
		print '*******************************************'
		if self._tokens:
			print '2.- Tokens: '
			print self._tokens
			print '*******************************************'
		if self._analysis:
			print '3.- Analysis: '
			print self._analysis
			print '*******************************************'
		if self._synonyms:
			print '4.- Synonyms: '
			print self._synonyms
			print '*******************************************'
		if self._fdist:
			print '5.- Frecuencies: '
			print self._fdist.items()
			print '*******************************************'