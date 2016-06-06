## Spanish Corpus

The Python dependencies are described in **requirements.txt**. To install
I recommend install _virtualenv_ and _virtualenvwrapper_ (http://rukbottoland.com/blog/tutorial-de-python-virtualenvwrapper/). 
Then you can install the spanishCorpus requirements with the command:
_pip install -r requirements.txt_

This little library needs some packages of _NLTK (Natural Language Toolkit)_.
To install these packages is required init a _Python_ console in the _virtualenv_ 
in which the requirements are installed. 

Now enter the command: _nltk.download()_

In the _nltk_ manager you have to ensure that Corpora has installed:
* cess_esp
* omw
* stopwords
* wordnet
* words

And in Models you have to ensure that _Snowball_data_ is installed.

Install German and French dictionaries to more accurately:
* _sudo apt-get install myspell-de-de_
* _sudo apt-get install myspell-fr-fr_

In **main.py** you have an example of the library's use.
