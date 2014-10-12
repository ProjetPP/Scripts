#!/bin/bash

if [ ! -f corenlp-python ]
then
then
    echo "Cloning Valentin's modified corenlp-python library…"
    git clone https://bitbucket.org/ProgVal/corenlp-python.git
fi
echo "Installing it…"
cd corenlp-python
python3 setup.py install --user
cd ..
if [ ! -f stanford-corenlp-full-2014-08-27.zip ]
then
    echo "Downloading CoreNLP (long: 221MB)…"
    wget http://nlp.stanford.edu/software/stanford-corenlp-full-2014-08-27.zip
fi
echo "Extracting CoreNLP…"
rm -f stanford-corenlp-full-2014-08-27
unzip stanford-corenlp-full-2014-08-27.zip
echo "All seemed to work. Hold tight while we test it on a simple example (might take some time)."
CORENLP=stanford-corenlp-full-* python3 -c "print(repr(__import__('corenlp').StanfordCoreNLP().raw_parse('This is a sentence.')))"
