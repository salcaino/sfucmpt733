import nltk, os, pickle
from sklearn.pipeline import Pipeline
from tweet_analytics import *

path = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(path)
cwd = parent + "/nltk_data"
nltk.data.path = [cwd]

custom_tweet = "I love it."
    # custom_tokens = remove_noise(word_tokenize(custom_tweet))
    # doc = ' '.join(custom_tokens)
with open(path + '/trainedpipe.pkl', 'rb') as f:
    classifier = pickle.load(f)

res = classifier.predict([custom_tweet])
print(custom_tweet, "Positive" if res == 1 else "Negative")