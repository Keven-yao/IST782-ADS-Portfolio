'''
  This program shell reads phrase data for the kaggle phrase sentiment classification problem.
  The input to the program is the path to the kaggle directory "corpus" and a limit number.
  The program reads all of the kaggle phrases, and then picks a random selection of the limit number.
  It creates a "phrasedocs" variable with a list of phrases consisting of a pair
    with the list of tokenized words from the phrase and the label number from 1 to 4
  It prints a few example phrases.
  In comments, it is shown how to get word lists from the two sentiment lexicons:
      subjectivity and LIWC, if you want to use them in your features
  Your task is to generate features sets and train and test a classifier.

  Usage:  python classifyKaggle.py  <corpus directory path> <limit number>

  This version uses cross-validation with the Naive Bayes classifier in NLTK.
  It computes the evaluation measures of precision, recall and F1 measure for each fold.
  It also averages across folds and across labels.
'''

# open python and nltk packages needed for processing
import re
import os
import sys
import random
import nltk
from nltk.corpus import stopwords
from nltk.collocations import *
from nltk.metrics import ConfusionMatrix

# this code is commented off now, but can be used for sentiment lists
#import sentiment_read_subjectivity
# initialize the positive, neutral and negative word lists
#(positivelist, neutrallist, negativelist)
#    = sentiment_read_subjectivity.read_three_types('SentimentLexicons/subjclueslen1-HLTEMNLP05.tff')

#import sentiment_read_LIWC_pos_neg_words
# initialize positve and negative word prefix lists from LIWC
#   note there is another function isPresent to test if a word's prefix is in the list
#(poslist, neglist) = sentiment_read_LIWC_pos_neg_words.read_words()

## define a feature definition function here

# this function define features (keywords) of a document for a BOW/unigram baseline
# each feature is 'V_(keyword)' and is true or false depending
# on whether that keyword is in the document

def extractFeatureSet(phraseGiven,bagofwords):
    wordVec={}
    tokens=phraseGiven[0]
    for word in bagofwords:
        wordVec[word]=False
        if word in tokens:
            wordVec[word]=True
    return wordVec

def extract_not_features(phraseGiven, bagofwords):
    negationwords = ['n\'t','no', 'not', 'never', 'none', 'nowhere', 'nothing', 'noone', 'rather', 'hardly', 'scarcely', 'rarely', 'seldom', 'neither', 'nor']
    wordVec = {}
    for word in bagofwords:
        nword="Not "+word
        wordVec[word]=False
        wordVec[nword]=False

    tokens=phraseGiven[0]
    prev=""
    if word in tokens:
        nword="Not "+word
        wordVec[word]=True
        if prev in negationwords:
            wordVec[nword]=True
        prev=word
    return wordVec


def get_biagram_features(tokens):
    if not tokens:
        return {}
    bigram_measures = nltk.collocations.BigramAssocMeasures()
    finder = BigramCollocationFinder.from_words(tokens,window_size=3)
    bigram_features = finder.nbest(bigram_measures.chi_sq, 3000)
    return bigram_features[:500]

def extract_bigram_features(phraseGiven, bagofwords):
    features = {}
    bigram_features=get_biagram_features(bagofwords)
    tokens=phraseGiven[0]
    if not tokens:
        return features
    document_bigrams=[]
    for word in bagofwords :
        features['contains({})'.format(word)] = (word in tokens)
    document_bigrams=get_biagram_features(tokens)
    for bigram in bigram_features:
        features['bigram({} {})'.format(bigram[0], bigram[1])] = (bigram in document_bigrams)
    return features

def extract_POS_features(phraseGiven, bagofwords):
    tokens = phraseGiven[0]
    tagged_words = nltk.pos_tag(tokens)
    features = {}
    for word in bagofwords:
        features['contains({})'.format(word)] = (word in tokens)
    numNoun = 0
    numVerb = 0
    numAdj = 0
    numAdverb = 0
    for (word, tag) in tagged_words:
        if tag.startswith('N'): numNoun += 1
        if tag.startswith('V'): numVerb += 1
        if tag.startswith('J'): numAdj += 1
        if tag.startswith('R'): numAdverb += 1
    features['nouns'] = numNoun
    features['verbs'] = numVerb
    features['adjectives'] = numAdj
    features['adverbs'] = numAdverb
    return features

def readSubjectivity(path):
  flexicon = open(path, 'r')
  sldict = { }
  for line in flexicon:
    fields = line.split()
    strength = fields[0].split("=")[1]
    word = fields[2].split("=")[1]
    posTag = fields[3].split("=")[1]
    stemmed = fields[4].split("=")[1]
    polarity = fields[5].split("=")[1]
    if (stemmed == 'y'):
      isStemmed = True
    else:
      isStemmed = False
    # put a dictionary entry with the word as the keyword
    #     and a list of the other values
    sldict[word] = [strength, posTag, isStemmed, polarity]
  return sldict

def extract_SL_features(phraseGiven, bagofwords,SL):
  tokens = phraseGiven[0]
  features = {}
  for word in bagofwords:
    features['contains({})'.format(word)] = (word in tokens)
  weakPos = 0
  strongPos = 0
  weakNeg = 0
  strongNeg = 0
  for word in tokens:
    if word in SL:
      strength, posTag, isStemmed, polarity = SL[word]
      if strength == 'weaksubj' and polarity == 'positive':
        weakPos += 1
      if strength == 'strongsubj' and polarity == 'positive':
        strongPos += 1
      if strength == 'weaksubj' and polarity == 'negative':
        weakNeg += 1
      if strength == 'strongsubj' and polarity == 'negative':
        strongNeg += 1
      features['positivecount'] = weakPos + (2 * strongPos)
      features['negativecount'] = weakNeg + (2 * strongNeg)

  if 'positivecount' not in features:
    features['positivecount']=0 #final positive counts
  if 'negativecount' not in features:
    features['negativecount']=0 #final negative counts
  return features


def alpha_filter(w):
  pattern = re.compile('^[^a-z]+$')
  if (pattern.match(w)):
    return True
  else:
    return False

def display_confusion_matrix(classifier_type, test_set):
  reflist = []
  testlist = []
  for (features, label) in test_set:
    reflist.append(label)
    testlist.append(classifier_type.classify(features))
  print("The confusion matrix")
  cm = ConfusionMatrix(reflist, testlist)
  print("cm")

def cross_validation_accuracy(num_folds, featuresets):
    subset_size = int(len(featuresets)/num_folds)
    accuracy_list = []
    for i in range(num_folds):
        test_this_round = featuresets[(i*subset_size):][:subset_size]
        train_this_round = featuresets[:(i*subset_size)] + featuresets[((i+1)*subset_size):]
        classifier = nltk.NaiveBayesClassifier.train(train_this_round)
        accuracy_this_round = nltk.classify.accuracy(classifier, test_this_round)
        print (i, accuracy_this_round)
        display_confusion_matrix(classifier,test_this_round)
        accuracy_list.append(accuracy_this_round)
    print ('mean accuracy', sum(accuracy_list) / num_folds)

def convertToCSV(data, bagofwords):
    f=open("/Users/yaoyunkai/Desktop/IST 664/Final Project/FinalProjectData/kagglemoviereviews/corpus/train.csv","w")
    f.write("ID,")
    for i in range(len(bagofwords)):
        f.write(bagofwords[i]+",")
    f.write("Sentiment Target\n")
    count=0
    for phrase in data:
        f.write(str(count)+",")
        count+=1
        dictFS=extractFeatureSet(phrase,bagofwords) #using word-vector feature set
        valuesl= dictFS.values()
        for i in valuesl:
            if(i==False):
                f.write("0,")
            else:
                f.write("1,")
        f.write(str(phrase[1])+"\n")
    f.close()


def processkaggle(dirPath,limitStr):
  limit = int(limitStr)

  os.chdir(dirPath)

  f = open('./train.tsv', 'r')
  phrasedata = []
  for line in f:
    if (not line.startswith('Phrase')):
      line = line.strip()
      phrasedata.append(line.split('\t')[2:4])

  random.shuffle(phrasedata)
  phraselist = phrasedata[:limit]

  print('Read', len(phrasedata), 'phrases, using', len(phraselist), 'random phrases')

  for phrase in phraselist[:10]:
    print (phrase)

  phrasedocs = []
  for phrase in phraselist:
    tokens = nltk.word_tokenize(phrase[0])
    phrasedocs.append((tokens, int(phrase[1])))

  print("\n--------- Phrases from the documents: ")
  for phrase in phrasedocs[:10]:
      print (phrase)

  filteredPhrases=[]
  stopwords = nltk.corpus.stopwords.words('english')
  for phrase in phrasedocs:
      tokens=phrase[0]
      stopwordsTokens=[]
      lowercaseTokens = [w.lower() for w in tokens]
      alphaTokens = [w for w in lowercaseTokens if not alpha_filter(w)]
      count=0
      for word in alphaTokens:
          if word not in stopwords:
              stopwordsTokens.append(word)
              count+=1
          if count == 0:
              stopwords.append(word)
      filteredPhrases.append((stopwordsTokens,phrase[1]))

  # print a few
  print("\n--------- Filtered Phrases: ")
  for phrase in filteredPhrases[:10]:
      print (phrase)

  bagOfWords=[]
  for phrase in filteredPhrases:
      tokens=phrase[0]
      for word in tokens:
          if word not in bagOfWords:
              bagOfWords.append(word)

  bagOfWords500=[]
  wordlist = nltk.FreqDist(bagOfWords)
  bagOfWords500 = [w for (w, c) in wordlist.most_common(200)]

  # feature sets from a feature definition function
  # feature set with all the words in the phrase- words to vector
  featureSet= [(extractFeatureSet(phrase,bagOfWords),phrase[1]) for phrase in filteredPhrases]
  # feature set with 500 most frequently used words in the phrase- words to vector
  featureSet1= [(extractFeatureSet(phrase,bagOfWords500),phrase[1]) for phrase in filteredPhrases]


  #feature set where negatation words are also consider as a part of our featureSet
  featureSet2= [(extract_not_features(phrase,bagOfWords),phrase[1]) for phrase in filteredPhrases]
  # feature set with 500 most frequently used words in the phrase and using negation words in our feature set
  featureSet3= [(extractFeatureSet(phrase,bagOfWords500),phrase[1]) for phrase in filteredPhrases]


  #feature set where bigram words are also consider as a part of our featureSet
  featureSet4= [(extract_bigram_features(phrase,bagOfWords),phrase[1]) for phrase in filteredPhrases]
  #feature set where bigram words are also consider as a part of our featureSet with 500 most common word features
  featureSet5= [(extract_bigram_features(phrase,bagOfWords500),phrase[1]) for phrase in filteredPhrases]



  #pos tagged words feature set with all words
  featureSet6= [(extract_POS_features(phrase,bagOfWords),phrase[1]) for phrase in filteredPhrases]
  #pos tagged words feature set with all 500 most common words
  featureSet7= [(extract_POS_features(phrase,bagOfWords500),phrase[1]) for phrase in filteredPhrases]


  #feature set where SL are also consider as a part of our featureSet
  SLpath = "/Users/yaoyunkai/Desktop/IST 664/Final Project/FinalProjectData/kagglemoviereviews/SentimentLexicons/subjclueslen1-HLTEMNLP05.tff"
  SL = readSubjectivity(SLpath)
  # with all words
  featureSet8= [(extract_SL_features(phrase,bagOfWords,SL),phrase[1]) for phrase in filteredPhrases]
  # with the 500 most common words
  featureSet9= [(extract_SL_features(phrase,bagOfWords500,SL),phrase[1]) for phrase in filteredPhrases]


  # train classifier and show performance in cross-validation
  # SL Feature classifier
  cross_validation_accuracy(5,featureSet8)
  cross_validation_accuracy(5,featureSet9)

  # Word-Vector Classifier
  cross_validation_accuracy(5,featureSet)
  cross_validation_accuracy(5,featureSet1)

  # Not Features Classifier
  cross_validation_accuracy(5,featureSet2)
  cross_validation_accuracy(5,featureSet3)

  # POS tag features classifier
  cross_validation_accuracy(5,featureSet6)
  cross_validation_accuracy(5,featureSet7)

  # bigram features classifier
  cross_validation_accuracy(5,featureSet4)
  cross_validation_accuracy(5,featureSet5)


"""
commandline interface takes a directory name with kaggle subdirectory for train.tsv
   and a limit to the number of kaggle phrases to use
It then processes the files and trains a kaggle movie review sentiment classifier.

"""
if __name__ == '__main__':
    if (len(sys.argv) != 3):
        print('usage: classifyKaggle.py <corpus-dir> <limit>')
        sys.exit(0)
    processkaggle(sys.argv[1], sys.argv[2])
