#!/bin/bash

USER_MODE="--user"
if [ $# -eq 1 ] && [ $1 == "--nouser" ]
then
    echo "No user mode."
    USER_MODE=""
fi

if [ ! -d CoreNLP ]
then
    echo "Cloning and installing CoreNLP…"
    git clone https://github.com/stanfordnlp/CoreNLP.git
    cd CoreNLP
    ant compile
    ant jar
    cd ..
fi
if ! ls stanford-english-corenlp-*models.jar 1> /dev/null 2>&1
then
    echo "Downloading English model for CoreNLP…"
    wget http://nlp.stanford.edu/software/stanford-english-corenlp-2016-01-10-models.jar
fi
yes | cp -l stanford-english-corenlp-*models.jar CoreNLP
echo "All seemed to work. Hold tight while we test it on a simple example (might take some time)."
cd CoreNLP
export CLASSPATH="`find . -name '*.jar'`"
java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer &
SERVER_PID=$!
sleep 1 # Let the server some time to start...
wget --post-data 'the quick brown fox jumped over the lazy dog' 'localhost:9000/?properties={"annotators": "tokenize,ssplit,pos", "outputFormat": "json"}' -O -
if [ $? -ne 0 ]
then
    echo "Something does not work…"
else
    echo "All seemed to work!"
fi
kill $SERVER_PID
