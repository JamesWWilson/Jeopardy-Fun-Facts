---
title: "Jeopardy Player Statistics & Fun Fact Text Bot"
date: '2020-02-12'
layout: post
summary: Who makes it onto Jeopardy, and just how interesting are they?
categories: null
---

{:refdef: style=“text-align: center;”}
![title](/assets/jeopardy_images/jeopardy_pic.jpg){: .center-image ; height="550px" width="550px"}
{: refdef}


Who makes it onto Jeopardy? And are they more interesting than a robot?
---------------------------------------------------------------

    #“I walked 10 2nd graders on my grandma.”

7 PM PST on a weeknight means Jeopardy. I’ll watch the show with anyone
that’s willing to listen as I mutter answers at a television screen
while Alex Trebek asks challenging trivia questions. Jeopardy has been a
central feature of my life, bonding with my Dad over dinner or competing
with college roommates to see who is the “smartest”.

The show is known for its structured and professional manner, where
contestants are cordial with one another, and everyone demonstrates a sort of
deference to the show and its now legendary host. After the first
commercial break, however, all contestants are given a chance to discuss
something interesting about themselves. This is where, in my opinion,
anyone who is a fan of the Bachelor gets a taste of their favorite
snack: human judgement. It’s fun watching contestants talk about being
mistaken for Nicolas Cage in Mexico, or tell embarassing stories about
coaching Quidditch teams (these are real examples!)

In celebration of the Ultimate Champions tournament that took place this past
month, I thought it would be fun to look at anyone but the Champions.
More specifically, I want to take a deep dive into the types of people
that make it onto the show, and what aspect of their lives they think is
worth discussing in front of a live audience. From a data perspective, can we
simulate the contestant's fun facts and create a Jeopardy *Watson* with its
own personality?

Part 1: The Data
----------------

{:refdef: style=“text-align: center;”}
![archive](/assets/jeopardy_images/jeopardy-archive.jpeg){:height="550px" width="750px"}
{: refdef}

We can collect information on Jeopardy contestants from two sources: the
Offical Jeopardy Archive & the Twitter account *@CoolJeopardyStories*.
The Jeopardy Archive collects and maintains all details related to the
show, including each contestant’s name, occupation, hometown, number of
games won, cash winnings, and more. Using the BeautifulSoup library in
Python 3.7, we can scrape the website for these variables and build a
data set of details for each contestant on each show.

### Archive Scraper Function

```Python
# Load packages
from bs4 import BeautifulSoup
import requests

# Prep Variables
index = 0
output = []
archive_link = "http://www.j-archive.com/showgame.php?game_id="
game_id = 6389
new_game_id = 0
jeopardy_archive_link = archive_link + str(game_id)

#Start Extraction -
while index < 2000:
  # pull page
  page_response = requests.get(jeopardy_archive_link, timeout=5)
  page_content = BeautifulSoup(page_response.content, "html.parser")

  # empty variables
  anecdotes = []
  final_scores = []
  names = []
  show_info1 = []
  show_info2 = []
  show_info3 = []

  #title date
  title_date = page_content.find_all('title')[0].text # clean to just date

  for j in range(0, 3):
    #Find all anecdotes for contestants
    paragraphs = page_content.find_all("p")[j].text

    # Final all final scores for contestants
    try:
    table1 = page_content.find_all(lambda tag: tag.name == 'td' and
    tag.get('class') == ['score_positive'])[9:12][j].text
    pass
    except IndexError:
    print("error" + str(new_game_id))
    # ignore error output -
      # used to locate mismatched fields from archive (special events)

    #find all names
    table2 = page_content.find_all(lambda tag: tag.name == 'td' and
    tag.get('class') == ['score_player_nickname'])[j].text
    # append those players together
    anecdotes.append(paragraphs)
    final_scores.append(table1)
    names.append(table2)

  # reorder and correct data
  show_info1.extend([names[0],anecdotes[2],final_scores[0],title_date])
  show_info2.extend([names[1],anecdotes[1],final_scores[1],title_date])
  show_info3.extend([names[2],anecdotes[0],final_scores[2],title_date])
  #create output file
  output.append(show_info1)
  output.append(show_info2)
  output.append(show_info3)
  #create link to next page
  #create previous page number
  new_game_id = page_content.find_all(lambda tag: tag.name == 'a' and
  tag.get('href') and
  tag.text == "[<< previous game]")
  new_game_id = re.findall(r'\d+', str(new_game_id[0]))[0]
  # create link
  jeopardy_archive_link = archive_link + new_game_id
  jeopardy_archive_link
  #update iterator
  index = index + 1

```

{:refdef: style=“text-align: center;”}
![CoolJeopardyStores](/assets/jeopardy_images/cooljepstories.jpeg){:height="550px" width="750px"}
{: refdef}

For the “fun fact” part of the analysis, we rely on the work of Chad
Mosher, as there are no episode transcripts easily available
online<sup>1</sup>. Chad ran the @CoolJeopardyStories account from February
11th, 2014 to July 26th, 2019, where he created tweet length version’s
of each show contestant’s story. While these transcription aren’t
perfect representations, they get to the meat of the stories and should
work for our purposes.

### Twitter API Pull

```Python

# -*- coding: utf-8 -*-
import tweepy
import pandas as pd
from pandas import DataFrame

consumer_key= '###############################'
consumer_secret= '###############################'
access_key = '###############################'
access_secret= '###############################'

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

```

We can merge these datasets together on their respective player id and
show date fields to create a full data set of contestant details.

```Python
    #jeopardy_df.head()
```

The final dataset for our analysis contains *1,971* contestants playing
in games ranging from October 24th, 2010 to July 26th, 2019.

Part 2: Player Statistics
-------------------------

So who are these contestants? First, lets look at where they list their
Hometowns across the United States<sup>2</sup>.

<table>
<thead>
<tr class="header">
<th style="text-align: center;">Hometown</th>
<th style="text-align: center;">Contestant Count</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td style="text-align: center;">New York, New York</td>
<td style="text-align: center;">133</td>
</tr>
<tr class="even">
<td style="text-align: center;">Chicago, Illinois</td>
<td style="text-align: center;">104</td>
</tr>
<tr class="odd">
<td style="text-align: center;">Los Angeles, California</td>
<td style="text-align: center;">99</td>
</tr>
<tr class="even">
<td style="text-align: center;">Brooklyn, New York</td>
<td style="text-align: center;">70</td>
</tr>
<tr class="odd">
<td style="text-align: center;">Seattle, Washington</td>
<td style="text-align: center;">45</td>
</tr>
<tr class="even">
<td style="text-align: center;">Atlanta, Georgia</td>
<td style="text-align: center;">44</td>
</tr>
<tr class="odd">
<td style="text-align: center;">Austin, Texas</td>
<td style="text-align: center;">39</td>
</tr>
<tr class="even">
<td style="text-align: center;">Las Vegas, Nevada</td>
<td style="text-align: center;">37</td>
</tr>
<tr class="odd">
<td style="text-align: center;">Arlington, Virginia</td>
<td style="text-align: center;">31</td>
</tr>
<tr class="even">
<td style="text-align: center;">San Diego, California</td>
<td style="text-align: center;">30</td>
</tr>
<tr class="odd">
<td style="text-align: center;">Portland, Oregon</td>
<td style="text-align: center;">29</td>
</tr>
<tr class="even">
<td style="text-align: center;">…</td>
<td style="text-align: center;">…</td>
</tr>
</tbody>
</table>

We can take these hometowns and plot them to their respective FIP codes
(using data from the U.S. Census Bureau) across the United States\[3\].

{:refdef: style=“text-align: center;”}
![Map](/assets/jeopardy_images/uscountymap.png)
{: refdef}

Contestants appear to make it onto Jeopardy in proportion with
population centers across the country. Put more aptly, while higher
numbers of contestants come from dense coastal cities, we also see
individuals popping up from small towns across the US. In reality, 51%
of contestants come from their own unique hometown!

We can also take a glimpse at which states have the highest winnings overall!






# Occupation Types & Winnings






Part 3: Sentiment Analysis
--------------------------








Part 4: Fun Fact Text-Bot Using TextGenRNN
------------------------------------------

{:refdef: style=“text-align: center;”}
![watson](/assets/jeopardy_images/ibm_watson_logo.jpg){: .center-image ; height="550px" width="750px"}
{: refdef}

Each contestant's fun fact about themselves makes for perfect text bot fuel. I cleaned
each tweet for punctuation and correct name formatting, as well as stringing them
together ...

Once done, we can now








```Python
## four lines of code for TextGenRNN


```


### The LSTM Model










<table>
<thead>
<tr class="header">
<th style="text-align: center;">Generated Fun Facts</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td style="text-align: center;">I have a chicken contest in the Marching Sandois.</td>
</tr>
<tr class="even">
<td style="text-align: center;">My dad wrote me a bug geography</td>
</tr>
<tr class="odd">
<td style="text-align: center;">I proposed in a theatre in a trivia contest.</td>
</tr>
<tr class="even">
<td style="text-align: center;">I met my husband at social food climbing.</td>
</tr>
<tr class="odd">
<td style="text-align: center;">I met my wife when I was pregnant with London.</td>
</tr>
</tbody>
</table>

Part 5: Conclusion
------------------




Data
====

[Jeopardy Archive](https://data.lacity.org/A-Well-Run-City/Parking-Citations/wjz9-h9np)

[@CoolJeopardyStores](https://github.com/JamesWWilson/UCLA-Parking-Tickets-Analysis)

Code
====

[Github](https://github.com/JamesWWilson/Jeopardy-Fun-Facts)

Citations
=========

1 If you work for Jeopardy or NBC, I would love access to transcripts from the show to analyze!

2 Excluding contestants from Canada, Alaska, and Hawaii.

3 [Simple Maps Data](https://simplemaps.com/data/us-cities)
