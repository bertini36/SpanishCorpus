#! /usr/bin/python
# coding=utf-8

__author__ = "Alberto Pou Quirós"

from SpanishCorpus import SpanishCorpus

def main():
    text = u'Azkaban ha existido desde el siglo XV, pero en sus origenes no era una prisión.\
             La isla en el mar del Norte en la que se construyó la primera fortaléza no se documenta\
             en ningun mapa, muggle o mágico, y se cree que fue creada, o agrandada, por medios\
             mágicos.'
    corpus = SpanishCorpus(text, timing=True)
    corpus.tokenize()
    corpus.clean()
    corpus.filterStopwords()
    corpus.analize(to_correct=True)
    corpus.cleanPostAnalysis()
    corpus.unifyTokens()
    corpus.synonymize()
    corpus.calculateFrequencies()
    corpus.showResults()

if __name__ == "__main__": main()