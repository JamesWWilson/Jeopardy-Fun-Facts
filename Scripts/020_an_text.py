# -*- coding: utf-8 -*-
"""
Created on Tue Dec 17 08:50:03 2019

@author: jwilson2
"""

#import nltk
import pandas as pd
import re
from nltk.corpus import stopwords
#nltk.download('stopwords')

# Read Data 
jeopardy_df = pd.read_csv("clean_jeopardy_data.csv")
# General Analysis
contestants = jeopardy_df.groupby('Full Name').agg(['count'])
jobs = jeopardy_df.groupby('Occupation')['Full Name'].nunique()
town = jeopardy_df.groupby('Hometown')['Full Name'].nunique()
# Investigate
jeopardy_df.groupby('Full Name')['Occupation'].nunique()

# Analyze Text 

# clean general text 
# replace "&amp;" with "and" 
jeopardy_df['text'] = jeopardy_df['anecdote'].str.replace('&amp;','and')
# remove " " 
jeopardy_df['text'] = jeopardy_df['text'].str.replace('"','')
jeopardy_df['text'] = jeopardy_df['text'].str.replace("'",'')
jeopardy_df['text'] = jeopardy_df['text'].str.lstrip('\"')



# fix jeopardy exclamation mark
jeopardy_df['text'] = jeopardy_df['text'].str.replace('Jeopardy!','Jeopardy')
# general misspelling
jeopardy_df['text'] = jeopardy_df['text'].str.replace('justl ike','just like')

# rename individuals with @ signs 
# Function to clean the names 
def Clean_names(jprdy): 
    if re.search('@', jprdy): 
        sentence = re.sub( r"([A-Z])", r" \1", jprdy).split()
        jprdy = ' '.join(sentence)
        return jprdy
    else:
        return jprdy

# Updated the clean text columns 
jeopardy_df['text1'] = jeopardy_df['text'].apply(Clean_names) 

# remove '@'
jeopardy_df['text'] = jeopardy_df['text'].str.replace('@ ','')




# lower and punctuation 
#jeopardy_df['text1'] = jeopardy_df['anecdote'].apply(lambda x: " ".join(x.lower() for x in x.split()))
#jeopardy_df['text1'].head()
#jeopardy_df['text1'] = jeopardy_df['text'].str.replace('[^\w\s]','')




# stop words
stop = stopwords.words('english')
jeopardy_df['text3'] = jeopardy_df['text2'].apply(lambda x: " ".join(x for x in x.split() if x not in stop))

# frequent words - maybe edit this manually
freq = pd.Series(' '.join(jeopardy_df['text3']).split()).value_counts()[:20]
freq = list(freq.index)
jeopardy_df['text4'] = jeopardy_df['text3'].apply(lambda x: " ".join(x for x in x.split() if x not in freq))

# non frequent
nonfreq = pd.Series(' '.join(jeopardy_df['text4']).split()).value_counts()[-10:]
nonfreq = list(nonfreq.index)
jeopardy_df['text5'] = jeopardy_df['text4'].apply(lambda x: " ".join(x for x in x.split() if x not in nonfreq))
jeopardy_df['text5'].head()


# check spelling - doesn't work well
from textblob import TextBlob
#jeopardy_df['text6'] = jeopardy_df['text5'].apply(lambda x: str(TextBlob(x).correct()))
# just create word vector
#jeopardy_df['text6'] = TextBlob(jeopardy_df['text5']).words

from nltk.stem import PorterStemmer
st = PorterStemmer()
jeopardy_df['text5'][:5].apply(lambda x: " ".join([st.stem(word) for word in x.split()]))

from textblob import Word
jeopardy_df['text6'] = jeopardy_df['text5'].apply(lambda x: " ".join([Word(word).lemmatize() for word in x.split()]))
jeopardy_df['text6'].head()


TextBlob(jeopardy_df['text6'][0]).ngrams(2)
# scikit-learn api

tweets = list(jeopardy_df['text1'])


## USING TEXTGENRNN
from textgenrnn import textgenrnn
textgen = textgenrnn()
textgen.train_on_texts(tweets, num_epochs = 10)
textgen.generate(10)


# Clean text - spelling / jeopardy handles / additional words / etc. 











