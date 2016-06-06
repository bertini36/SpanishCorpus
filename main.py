# -*- coding: UTF-8 -*-

from __future__ import unicode_literals

from SpanishCorpus import SpanishCorpus


def main():
    text = 'Azkaban ha existido desde el siglo XV, pero en sus origenes no era una prisión.\
            La isla en el mar del Norte en la que se construyó la primera fortaléza no se documenta\
            en ningun mapa, muggle o mágico, y se cree que fue creada, o agrandada, por medios\
            mágicos.'
    corpus = SpanishCorpus(text, timing=True)
    corpus.tokenize()
    corpus.clean()
    corpus.filter_stop_words()
    corpus.analize(to_correct=True)
    corpus.clean_post_analysis()
    corpus.unify_tokens()
    corpus.synonymize()
    corpus.calculate_frequencies()
    corpus.show_results()


if __name__ == '__main__': main()