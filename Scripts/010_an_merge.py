# -*- coding: utf-8 -*-
"""
Created on Mon Dec 16 15:11:30 2019

@author: jwilson2
"""
import pandas as pd

# Load Data
archive_df = pd.read_csv("jeopardy_archive_data.csv")
twitter_df = pd.read_csv("jeopardy_twitter_data.csv")

# Reformat Data
# Melt twitter data 
twitter_df = pd.melt(twitter_df, id_vars =['id', 'created_at', 'favorite_count', 'retweet_count', 'text',
       'game_info_flg', 'Date'], var_name="answer_number")

# Add "Answer" variable to twitter 
    #IMPORTANT - reverse order of answers for archive data to match how twitter account was organized
archive_df["answer_number"] = ""
archive_df['dt_indx'] = archive_df.groupby(['Date']).cumcount()+1
archive_df.loc[archive_df["dt_indx"]==1,"answer_number"] = "Answer3"
archive_df.loc[archive_df["dt_indx"]==2,"answer_number"] = "Answer2"
archive_df.loc[archive_df["dt_indx"]==3,"answer_number"] = "Answer1"

# Merge Data Files
jeopardy = pd.merge(archive_df,twitter_df, on=['Date','answer_number'])
jeopardy.head(10)

# Clean Data 
# clean money column
jeopardy['Final Score'] = jeopardy['Final Score'].str.replace(',', '')
jeopardy['Final Score'] = jeopardy['Final Score'].str.replace('$', '')
jeopardy['Final Score'] = jeopardy['Final Score'].astype(int)
        
# rename value column
jeopardy.rename(columns = {'value':'anecdote'}, inplace = True) 
jeopardy['anecdote'] = jeopardy['anecdote'].str.replace('"', '')

jeopardy_sub = jeopardy.iloc[:,[4,2,5,6,10,11,12,15,16,19]]

jeopardy_sub.to_csv('clean_jeopardy_data.csv', index = None, header=True) #Don't forget to add '.csv' at the end of the path


