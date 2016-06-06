# -*- coding: UTF-8 -*-

from __future__ import unicode_literals

import sys
import time
import enchant

from nltk import FreqDist
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords, cess_esp, wordnet

from pattern.es import parse, singularize, conjugate, INFINITIVE, predicative


class SpanishCorpus:
    """
    Class SpanishCorpus to ease text mining in spanish.
    The objective of this library is generate a clean corpus of words based on a text in spanish.
    Attributes:
        _text: Original text provided in the initialization
        _tokens: Stores the result of the different filter functions
        _analysis: List of tuples with de lexical analysis result
        _corrected_words: List of corrected words
        _synonyms: List of sets of synonyms of every word in tokens
        _fdist: Instance of nltk.FreqDist
        _timing: True if you want to timing the methods
    The class functions are in the logical order to run
    """

    word_tag_fd = FreqDist(cess_esp.tagged_words())
    levenshtein_distance = 1

    def __init__(self, text, timing=False):
        """
        :param text: Original text
        :param timing: True if you want timing the methods
        """
        self._text = text
        self._tokens = None
        self._analysis = None
        self._corrected_words = {}
        self._synonyms = None
        self._fdist = None
        self._timing = timing

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

    @property
    def corrected_words(self):
        return self._corrected_words

    @corrected_words.setter
    def corrected_words(self, value):
        self._corrected_words = value

    def timing(method):
        """
        Decorator that allows to time the execution of a function
        """
        def timed(self, *args, **kwargs):
            if self._timing:
                t_start = time.time()
                result = method(self, *args, **kwargs)
                t_end = time.time()
                print('{0} --- {1} sec'.format(method.__name__.ljust(25, str(' ')), t_end - t_start))
            else:
                result = method(self, *args, **kwargs)
            return result

        return timed

    @timing
    def tokenize(self):
        """
        Converts a text into a list of words
        :return: Tokens
        """
        self._tokens = word_tokenize(self._text)
        return self._tokens

    @timing
    def clean(self):
        """
        Minimises words and filters not completely alpha words of tokens
        :return: Tokens
        """
        if self._tokens is None:
            raise Exception('It\'s necessary execute first tokenize')
        self._tokens = [word.lower() for word in self._tokens if word.isalpha() and len(word) > 2]
        return self._tokens

    @timing
    def filter_stop_words(self):
        """
        Filters stopwords of tokens
        :return: Tokens
        """
        if self._tokens is None:
            raise Exception('It\'s necessary execute first tokenize')
        spanish_stopwords = stopwords.words('spanish')
        self._tokens = [word for word in self._tokens if word not in spanish_stopwords]
        return self._tokens

    @classmethod
    def levenshtein(cls, s1, s2):
        """
        Calculates the Levenshtein's distance between two words
        :param s1:
        :param s2: Words to compare
        :return: Number of differences
        """
        if len(s1) < len(s2):
            return SpanishCorpus.levenshtein(s2, s1)
        if len(s2) == 0:
            return len(s1)
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

    def correct_word(self, token):
        """
        Correct a word using enchant and the dictionary Nltk.cess_esp and the Levenshtein's distance
        :param token: Word to correct
        :return similar_word: Word closest
        """
        if token in self._corrected_words:
            return self._corrected_words[token]
        suggested = (enchant.Dict('es')).suggest(token)
        if len(suggested) > 0:
            for similar_word in suggested:
                if SpanishCorpus.levenshtein(token, similar_word) <= SpanishCorpus.levenshtein_distance:
                    self._corrected_words[token] = similar_word
                    print u'--> Palabra corregida: {} --> {}'.format(token, similar_word)
                    return similar_word
        minimum = sys.maxint
        similar_word = ''
        for word in cess_esp.words():
            lev_dist = SpanishCorpus.levenshtein(token, word)
            if (lev_dist < minimum) or (lev_dist == minimum and
                                                len(token) == len(word) and len(similar_word) != len(token)):
                minimum = lev_dist
                similar_word = word
                if lev_dist == 0:
                    break
        if minimum <= SpanishCorpus.levenshtein_distance:
            self._corrected_words[token] = similar_word
            print u'--> Palabra corregida: {} --> {}'.format(token, similar_word)
            return similar_word
        else:
            return None

    def check_category_nltk(self, token, index):
        """
        Detects the word's category using Nltk library.
        :param token: Word to check category
        :param index: Word's index in tokens
        :return category: Word's grammar category
        """
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

    def check_category_pattern(self, token, index):
        """
        Detects the word's category using Pattern library (when pattern
        library does't know the word it says that the word is a noun).
        :param token: Word to check category
        :param index: Word's index in tokens
        :return category: Word's grammar category
        """
        category = parse(token)
        if '/NN' in category:
            category = 'n'
        elif '/VB' in category:
            category = 'v'
        elif '/JJ' in category:
            category = 'a'
        elif '/CC' or '/CS' in category:
            category = 'c'
        elif '/P' in category:
            category = 'p'
        else:
            category = '-'
        if index >= len(self._analysis):
            self._analysis.append([token, category.ljust(7, '0')])
        else:
            self._tokens[index] = token
            self._analysis[index] = [token, category.ljust(7, '0')]
        return category

    def analize_word(self, token, index, to_correct):
        """
        Categorizes lexically a word. Initially it uses Nltk,
        if it doesn't find the word's category it tries with Pattern library.
        If doesn't work and the word not is a foreign word
        it tries to correct the word with enchant and cess_esp
        :param token: Word to analize
        :param index: Word's index in tokens
        :param to_correct: Indicates if it will try to correct word
        """
        category = self.check_category_nltk(token, index)
        if not category:
            category = self.check_category_pattern(token, index)
            if to_correct and category == 'n' and any(c in ['a', 'e', 'i', 'o', 'u'] for c in token) \
                    and not enchant.Dict('en').check(token) and not enchant.Dict('fr').check(token) \
                    and not enchant.Dict('de_DE').check(token):
                new_token = self.correct_word(token)
                if new_token and new_token != token:
                    self.analize_word(new_token, index=index, to_correct=False)

    @timing
    def analize(self, to_correct):
        """
        Returns a list of tuples of lexical analysis of tokens
        :param to_correct: Indicates if it will try to correct twords
        :return: Result of analysis
        """
        if self._tokens is None:
            raise Exception('It\'s necessary execute first tokenize')
        self._analysis = []
        for i in range(len(self._tokens)):
            token = self._tokens[i]
            self.analize_word(token, index=i, to_correct=to_correct)
        return self._analysis

    @timing
    def clean_post_analysis(self):
        """
        Filters determinants, pronouns and conjunctions of tokens
        :return tokens
        """
        if self._analysis is None:
            raise Exception('It\'s necessary execute first analize')
        new_tokens = []
        new_analysis = []
        new_synonyms = []
        for i in range(len(self._tokens)):
            if self._analysis[i][1][0] != 'd' \
                    and self._analysis[i][1][0] != 'p' \
                    and self._analysis[i][1][0] != 'c':
                new_tokens.append(self._tokens[i])
                new_analysis.append(self._analysis[i])
                if self._synonyms:
                    new_synonyms.append(self.synonyms[i])
        self._tokens = new_tokens
        self._analysis = new_analysis
        self._synonyms = new_synonyms
        if self._fdist:
            self.calculate_frequencies()
        return self._tokens

    @timing
    def unify_tokens(self):
        """
        Singuralizes nouns, conjugates verbs to infinitive and passes adjectives to
        predicative form in tokens
        :return: Tokens
        """
        if self._analysis is None:
            raise Exception('It\'s necessary execute first analize')
        for i in range(len(self._tokens)):
            if self._analysis[i][1][0] == 'n':
                self._tokens[i] = singularize(self._tokens[i])
            elif self._analysis[i][1][0] == 'v':
                self._tokens[i] = conjugate(self._tokens[i], INFINITIVE)
            elif self._analysis[i][1][0] == 'a':
                self._tokens[i] = predicative(self._tokens[i])
        return self._tokens

    @timing
    def synonymize(self):
        """
        Returns a list of sets of synonyms of every word in tokens. Only searchs
        synonyms of nouns and verbs
        :return: Synonyms
        """
        if self._analysis is None:
            raise Exception('It\'s necessary execute first analize')
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

    @timing
    def calculate_frequencies(self):
        """
        Returns a list of tuples where every word in tokens has its frequency
        of occurence
        :return: Frequencies
        """
        if self._tokens is None:
            raise Exception('It\'s necessary execute first tokenize')
        self._fdist = FreqDist(self._tokens)
        return self._fdist.items()

    def return_to_text(self):
        """
        Returns a string with the concatenation of tokens with spaces
        :return: Text
        """
        text = ''
        for token in self._tokens:
            text = '{} {}'.format(text, token)
        return text

    def show_results(self):
        """
        Shows the results of the study of corpus
        """
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

