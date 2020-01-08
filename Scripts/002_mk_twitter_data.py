# -*- coding: utf-8 -*-
"""
Created on Mon Dec 16 14:51:58 2019

@author: jwilson2
"""

import tweepy
import pandas as pd
from pandas import DataFrame

jeopardy_funfact_twitter_link = 'https://twitter.com/cooljepstories?lang=en'

# load Twitter API credentials
consumer_key= 'arBjlD4kgWVTuqk4pIXw0JWPH'
consumer_secret= 'gH16KBtOAjrEZ5Mn0TzfvLaODG1yMkDOXGlwlGOl2ptrLX43kN'
access_key = '1119604302-tnGJbpmtWLbVZ6WltX6WBlnK7rC7kBTWD7NiM7g'
access_secret= 'XMwoahiPfA0bGnX9xitN5AJzn9UzLiq8hZCoCtx7TaI5K'

#User ID
userID = "@CoolJepStories"

# Authorization to consumer key and consumer secret 
auth = tweepy.OAuthHandler(consumer_key, consumer_secret) 
# Access to user's access key and access secret 
auth.set_access_token(access_key, access_secret) 
# Calling api 
api = tweepy.API(auth) 

# 1750 tweets to be extracted 
number_of_tweets=1750
tweets = api.user_timeline(screen_name=userID, count = number_of_tweets, 
                           include_rts = False, tweet_mode="extended") 

all_tweets = []
all_tweets.extend(tweets)
oldest_id = tweets[-1].id
while True:
    tweets = api.user_timeline(screen_name=userID, 
                           count=200, # max allowed count
                           include_rts = False,
                           max_id = oldest_id - 1,
                           # Necessary to keep full_text 
                           # otherwise only the first 140 words are extracted
                           tweet_mode = 'extended'
                           )
    if len(tweets) == 0:
        break
    oldest_id = tweets[-1].id
    all_tweets.extend(tweets)
    print('N of tweets downloaded till now {}'.format(len(all_tweets)))

#transform the tweepy tweets into a 2D array that will populate the csv	
outtweets = [[tweet.id_str, 
              tweet.created_at, 
              tweet.favorite_count, 
              tweet.retweet_count, 
              tweet.full_text.encode("utf-8").decode("utf-8")] 
             for idx,tweet in enumerate(all_tweets)]
df = DataFrame(outtweets,columns=["id","created_at","favorite_count","retweet_count", "text"])
df.to_csv('%s_tweets.csv' % userID,index=False)
df.head(10)

# Flag just relevant tweets 
df["game_info_flg"] = ""

#subset to just game events
for i in range(0,len(df)):
    #print(((df['text'][i][0]).isnumeric()))
    df.at[i,'game_info_flg'] = df['text'][i][0].isnumeric()
df_games = df[df["game_info_flg"] == True]
df_games.reset_index(drop=True, inplace=True)

# SPlIT TWT TEXT INTO SEPERATE COLUMNS 
df_games["Date"] = ""
df_games["Answer1"] = ""
df_games["Answer2"] = ""
df_games["Answer3"] = ""
for i in range(0,len(df_games)):
    twt_txt = df_games["text"].iloc[i].split("\n")
    # split and save as a new row 
    df_games.at[i,"Date"] = twt_txt[0]
    df_games.at[i,"Answer1"] = twt_txt[1]
    df_games.at[i,"Answer2"] = twt_txt[2]
    if(len(twt_txt) > 3):
        df_games.at[i,"Answer3"] = twt_txt[3]

# CLEAN COLUMNS 
# - Clean date
df_games['Date'].replace(regex=True,inplace=True,to_replace=r':',value=r'')
df_games['Date'] = pd.to_datetime(df_games['Date'], errors='coerce')

# Output Data
df_games.to_csv('jeopardy_twitter_data.csv', index = None, header=True) #Don't forget to add '.csv' at the end of the path



