# Spanish Corpus

This little library needs some packages of NLTK (Natural Language Toolkit).
To install these packages is required init a Python console in the virtualenv 
in which the requirements are installed. 
Now enter the command: nltk.download()

In the nltk manager you have to ensure that Corpora has installed:
	- cess_esp
	- omw
	- stopwords
	- wordnet
	- words
And in Models you have to ensure that Snowball_data is installed.

Install German and French dictionaries to more accurately:
	sudo apt-get install myspell-de-de
 	sudo apt-get install myspell-fr-fr

In 'main.py' you have an example of the library's use.
