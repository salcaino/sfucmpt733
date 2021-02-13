import nltk
import os
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import twitter_samples, stopwords
from nltk.tag import pos_tag
from nltk.tokenize import word_tokenize
from nltk import FreqDist, classify, NaiveBayesClassifier
from sklearn.model_selection import train_test_split
import pickle
from sklearn.preprocessing import FunctionTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.ensemble import RandomForestClassifier
import numpy as np
import re, string, random, sys

def tokenmerger(tokens):
    return " ".join(tokens)

def tokenizeIt(data):
    res = [word_tokenize(text) for text in data]
    return res

def removeIt(data):
    res = [tokenmerger(remove_noise(tokens)) for tokens in data]
    return res

def remove_noise(tweet_tokens):

    cleaned_tokens = []
    lemmatizer = WordNetLemmatizer()
    stop_words = stopwords.words('english')
    for token, tag in pos_tag(tweet_tokens):
        token = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+#]|[!*\(\),]|'\
                       '(?:%[0-9a-fA-F][0-9a-fA-F]))+','', token)
        token = re.sub("(@[A-Za-z0-9_]+)","", token)

        if tag.startswith("NN"):
            pos = 'n'
        elif tag.startswith('VB'):
            pos = 'v'
        else:
            pos = 'a'

        
        token = lemmatizer.lemmatize(token, pos)

        if len(token) > 0 and token not in string.punctuation and token.lower() not in stop_words:
            cleaned_tokens.append(token.lower())
    return cleaned_tokens

def get_all_words(cleaned_tokens_list):
    for tokens in cleaned_tokens_list:
        for token in tokens:
            yield token

def get_tweets_for_model(cleaned_tokens_list):
    for tweet_tokens in cleaned_tokens_list:
        yield dict([token, True] for token in tweet_tokens)


def trainModel():    
    positive_tweets = twitter_samples.strings('positive_tweets.json')
    negative_tweets = twitter_samples.strings('negative_tweets.json')
    text = twitter_samples.strings('tweets.20150430-223406.json')
    # tweet_tokens = twitter_samples.tokenized('positive_tweets.json')[0]

    stop_words = stopwords.words('english')

    positive_tweet_tokens = twitter_samples.tokenized('positive_tweets.json')
    negative_tweet_tokens = twitter_samples.tokenized('negative_tweets.json')

    positive_cleaned_tokens_list = []
    negative_cleaned_tokens_list = []

    for tokens in positive_tweet_tokens:
        positive_cleaned_tokens_list.append(remove_noise(tokens))

    for tokens in negative_tweet_tokens:
        negative_cleaned_tokens_list.append(remove_noise(tokens))

    # all_pos_words = get_all_words(positive_cleaned_tokens_list)

    # freq_dist_pos = FreqDist(all_pos_words)
    # print(freq_dist_pos.most_common(10))

    positive_tokens_for_model = get_tweets_for_model(positive_cleaned_tokens_list)
    negative_tokens_for_model = get_tweets_for_model(negative_cleaned_tokens_list)

    positive_dataset = [(tweet_dict, "Positive")
                         for tweet_dict in positive_tokens_for_model]

    negative_dataset = [(tweet_dict, "Negative")
                         for tweet_dict in negative_tokens_for_model]

    dataset = positive_dataset + negative_dataset

    random.shuffle(dataset)

    train_data = dataset[:7000]
    test_data = dataset[7000:]

    classifier = NaiveBayesClassifier.train(train_data)
    print("Accuracy is:", classify.accuracy(classifier, test_data))
    with open('trainedmodel.pkl', 'wb') as f:
        pickle.dump(classifier, f)
        
    # print(classifier.show_most_informative_features(10))

def trainRandomForest():    
    
    stop_words = stopwords.words('english')
    positive_tweets = twitter_samples.strings('positive_tweets.json')
    negative_tweets = twitter_samples.strings('negative_tweets.json')

    X = positive_tweets + negative_tweets
    positives = np.ones([len(positive_tweets),1])
    negatives = np.zeros([len(negative_tweets),1])
    y = np.concatenate([positives, negatives])

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1, shuffle=True)
    
    pipe = Pipeline([
        ('tokenize', FunctionTransformer(tokenizeIt)),
        ('noise', FunctionTransformer(removeIt)), 
        ('tfidf', TfidfVectorizer(max_features=1500, min_df=5, max_df=0.7)),
        ('classifier', RandomForestClassifier(n_estimators=100, random_state=1))
        ])
    
    pipe.fit(X_train, y_train)
    y_pred = pipe.predict(X_test)
    print(confusion_matrix(y_test,y_pred))
    print(classification_report(y_test,y_pred))
    print(accuracy_score(y_test, y_pred))

    with open('trainedpipe.pkl', 'wb') as f:
        pickle.dump(pipe, f)

if __name__ == "__main__":
    path = os.path.dirname(os.path.realpath(__file__))
    parent = os.path.dirname(path)
    cwd = parent + "/nltk_data"
    print("Set NLTK path to {}".format(cwd))
    nltk.data.path = [cwd]

    if len(sys.argv) > 1 and sys.argv[1] == "train" :
        trainRandomForest()

    # trainRandomForest()
    # trainModel()
    
    custom_tweet = "I ordered just once from TerribleCo, they screwed up, never used the app again."
    # custom_tokens = remove_noise(word_tokenize(custom_tweet))
    # doc = ' '.join(custom_tokens)
    with open('trainedpipe.pkl', 'rb') as f:
        classifier = pickle.load(f)
    
    res = classifier.predict([custom_tweet])
    print(custom_tweet, "Positive" if res == 1 else "Negative")

