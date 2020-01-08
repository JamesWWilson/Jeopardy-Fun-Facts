# -*- coding: utf-8 -*-
"""
Created on Mon Dec 16 14:51:58 2019

@author: jwilson2
"""
from bs4 import BeautifulSoup
import requests
import pandas as pd
import re


#http://www.j-archive.com/showgame.php?game_id=6388

## Scrape online archive data
#Prep variables 
index = 0
output = []
archive_link = "http://www.j-archive.com/showgame.php?game_id="
game_id = 6389
new_game_id = 0
jeopardy_archive_link = archive_link + str(game_id)

#start extraction 
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
    title_date = page_content.find_all('title')[0].text # clean to just date (?)
    
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

#output
arch = pd.DataFrame.from_records(output)
arch.columns = ["Nickname", "Player Details", "Final Score", "Show Info"]
arch
arch["Player Details"].iloc[0].split("from")[1].split("(")[1].strip()
    
# Create Name Field 

# SPlIT TWT TEXT INTO SEPERATE COLUMNS 
arch["Full Name"] = ""
arch["Occupation"] = ""
arch["Hometown"] = ""
arch["Streak"] = ""
arch["Cash Winnings"] = ""
arch["Archive Info"] = ""
arch["Date"] = ""

for i in range(0,len(arch)):
    
    # extract player details 
    arch.at[i,"Full Name"] = arch["Player Details"].iloc[i].split(",")[0]
    arch.at[i,"Occupation"] = arch["Player Details"].iloc[i].split(",")[1].split("from")[0].strip()
    arch.at[i,"Hometown"] = arch["Player Details"].iloc[i].split("from")[1].split("(")[0].strip()
    
    # To Add 
    #arch.at[i,"Streak"] = ""
    #arch.at[i,"Cash Winnings"] = ""
    
    # extra show info 
    arch.at[i,"Archive Info"] = arch["Show Info"].iloc[i].split(", aired")[0].strip()
    arch.at[i,"Date"] = arch["Show Info"].iloc[i].split(", aired")[1].strip()

arch.head(5)

# - Clean date
arch['Date'].replace(regex=True,inplace=True,to_replace=r':',value=r'')
arch['Date'] = pd.to_datetime(arch['Date'], errors='coerce')
arch.head(5)

arch.to_csv('jeopardy_archive_data.csv', index = None, header=True) #Don't forget to add '.csv' at the end of the path

    
    