#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 26 20:04:29 2021

@author: Reaz
""" 

import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import numpy as np 

############## GET THE DF FOR BOWLING AND BATTING SCORE CARD ##################
class ScoreCardDf(object): 
    def __init__(self,URL): 
        self.URL=URL 
    
    @staticmethod 
    def ValidateLink(URL): 
        try: 
            page = requests.get(URL)
            bs = BeautifulSoup(page.content, 'lxml')  
            
            table_body=None
            table_body=bs.find_all('tbody') 
            
            if table_body == None: 
                return False 
            else: 
                return True
            
        except: 
            raise Exception('ScoreCardDf::ValidateLink(), Invalid Link was provided, Scraping Can not be completed' ) 
            
            
            
    def __GenerateBattingDf__(self): 
        
        if (ScoreCardDf.ValidateLink(self.URL)):
            page = requests.get(self.URL)
            bs = BeautifulSoup(page.content, 'lxml')
        
            table_body=bs.find_all('tbody')
            batsmen_df = pd.DataFrame(columns=["Name","Desc","Runs", "Balls", "4s", "6s", "SR", "Team"])
            for i, table in enumerate(table_body[0:4:2]):
                rows = table.find_all('tr')
                for row in rows[::2]:
                    cols=row.find_all('td')
                    cols=[x.text.strip() for x in cols]
                    if cols[0] == 'Extras':
                        continue
                    if len(cols) > 7:
                        batsmen_df = batsmen_df.append(pd.Series(
                        [re.sub(r"\W+", ' ', cols[0].split("(c)")[0]).strip(), cols[1], 
                        cols[2], cols[3], cols[5], cols[6], cols[7], i+1], 
                        index=batsmen_df.columns ), ignore_index=True)
                    else:
                        batsmen_df = batsmen_df.append(pd.Series(
                        [re.sub(r"\W+", ' ', cols[0].split("(c)")[0]).strip(), cols[1], 
                        0, 0, 0, 0, 0, i+1], index = batsmen_df.columns), ignore_index=True)
            

#### IGNORE DNB RECORDS, BUGGY CODE ####
# =============================================================================
#             # for i in range(2):
#             #     dnb_row = bs.find_all("tfoot")[i].find_all("div")
#             #     for c in dnb_row:
#             #         dnb_cols = c.find_all('span')
#             #         dnb = [x.text.strip().split("(c)")[0] for x in dnb_cols]
#             #         dnb = filter(lambda item: item, [re.sub(r"\W+", ' ', x).strip() for x in dnb])
#             #         for dnb_batsman in dnb:
#             #             batsmen_df = batsmen_df.append(pd.Series([dnb_batsman, "DNB", 0, 0, 0, 0, 0, i+1], index = batsmen_df.columns), ignore_index =True)
# =============================================================================
        
            return batsmen_df  
        
        else: 
            raise Exception('ScoreCardDf::ValidateLink(), Invalid Link was provided, Scraping Can not be completed' ) 
            
    
    def __GenerateBowlingDf__(self): 
        
        if (ScoreCardDf.ValidateLink(self.URL)):  
            page = requests.get(self.URL)
            bs = BeautifulSoup(page.content, 'lxml')       
            table_body=bs.find_all('tbody')
            bowler_df = pd.DataFrame(columns=['Name', 'Overs', 'Maidens', 'Runs', 'Wickets',
                                      'Econ', 'Dots', '4s', '6s', 'Wd', 'Nb','Team'])
            for i, table in enumerate(table_body[1:4:2]):
                rows = table.find_all('tr')
                for row in rows:
                    cols=row.find_all('td')
                    cols=[x.text.strip() for x in cols] 
                    #print (cols) # for debugging
                    
                    ## hard coded to rules avoid empty rows 
                    if len(cols)>=len(bowler_df.columns)-1 and len(cols)<=len(bowler_df.columns):
                        bowler_df = bowler_df.append(pd.Series([cols[0], cols[1], cols[2], cols[3], cols[4], cols[5], 
                                                    cols[6], cols[7], cols[8], cols[9], cols[10], (i==0)+1], 
                                                    index=bowler_df.columns ), ignore_index=True)
            return bowler_df
        
        else: 
            raise Exception('ScoreCardDf::ValidateLink(), Invalid Link was provided, Scraping Can not be completed' ) 
        
    
    def GetBattingDf(self): 
        df=self.__GenerateBattingDf__() 
        return df
    
    def GetBowlingDf(self): 
        df=self.__GenerateBowlingDf__()
        return df 
 
    
#################### ---------------------------------##########################


############## Calculate Fantasy Points for Bowling ##################
class FantasyBowlingPoints(object) :
    def __init__(self,score_card,squad,points_per_wicket=20): 
        self.df=score_card 
        self.squad=squad   
        self.points_per_wicket=points_per_wicket
        
    def __GenerateRawDf__(self):  
        bowler_df=self.df
        int_cols = ["Wickets","Runs", "Dots", "Maidens", "Team"]
        for col in int_cols:
            bowler_df[col] = bowler_df[col].astype(int) 
        bowler_df["Balls"] = bowler_df["Overs"].apply(lambda x: x.split(".")).\
                            apply(lambda x: int(x[0])*6 + int(x[1]) if len(x)>1 else int(x[0])*6)
    
        bowler_df["base_points"] = self.points_per_wicket*bowler_df["Wickets"]
        bowler_df["pace_points"] = 1.5*bowler_df["Balls"] - bowler_df["Runs"]
        bowler_df["pace_points"] = bowler_df["pace_points"] + (bowler_df.loc[:,"pace_points"]>0) * bowler_df["pace_points"]
        bowler_df["milestone_points"] = bowler_df["Wickets"].replace({1:0, 2:5, 3:15, 4:30, 5:50, 6:50, 7:50, 8:50})
        bowler_df["impact_points"] = bowler_df["Dots"] + bowler_df["Maidens"]*25
        bowler_df["bowling_points"] = bowler_df["base_points"] + bowler_df["pace_points"] + \
                                        bowler_df["milestone_points"] + bowler_df["impact_points"]
                                        
        return bowler_df 
    
    
    def __GenerateFantasyPointsDf__(self): 
        bowler_df=self.__GenerateRawDf__() 
        #print (bowler_df)
        fantasy_df=pd.DataFrame(columns=['Name','base_points','milestone_points','total_points'])
        for i in range (len(bowler_df)):  
            for each_player in self.squad:
                if bowler_df.Name[i] in each_player:  
                    #print (bowler_df.Name[i]) 
                    total_points=bowler_df.base_points[i]+bowler_df.milestone_points[i]
                    fantasy_df=fantasy_df.append(pd.Series([each_player,  
                                                            bowler_df.base_points[i], bowler_df.milestone_points[i], 
                                                            total_points],index=fantasy_df.columns),ignore_index=True) 
        #print (fantasy_df) 
        return fantasy_df 
    
    
    def GetFantasyPointsDf(self): 
        return self.__GenerateFantasyPointsDf__() 
    
    def GetFinalFantasyPoints(self): 
        fantasy_df=self.__GenerateFantasyPointsDf__() 
        return sum(fantasy_df['total_points'])
                

#################### ---------------------------------##########################
    
############## Calculate Fantasy Points for Batting ##################
class FantasyBattingPoints(object) :
    def __init__(self,score_card,squad,points_per_run=1): 
        self.df=score_card 
        self.squad=squad  
        self.points_per_run=points_per_run
        
    def __GenerateRawDf__(self): 
        batsmen_df=self.df
        int_cols = ["Runs", "Balls", "4s", "6s", "Team"]
        for col in int_cols:
            batsmen_df[col] = batsmen_df[col].astype(int)
            
        batsmen_df["base_points"] = batsmen_df["Runs"]*self.points_per_run
        batsmen_df["pace_points"] = batsmen_df["Runs"] - batsmen_df["Balls"]
        batsmen_df["milestone_points"] = (np.floor(batsmen_df["Runs"]/25)).replace(
                                          {1.0:5, 2.0:15, 3.0:30, 4.0:50, 5.0:50, 6.0:50, 7.0:50, 8.0:50})
        batsmen_df["impact_points"] = batsmen_df["4s"] + 2 * batsmen_df["6s"] + \
                                      (batsmen_df["Runs"] == 0) * (batsmen_df["Desc"] != "not out") * \
                                      (batsmen_df["Desc"] != "DNB") * (batsmen_df["Desc"] != "absent hurt") * (-5) 
        batsmen_df["batting_points"] = batsmen_df["base_points"] + batsmen_df["pace_points"] + \
                                        batsmen_df["milestone_points"] + batsmen_df["impact_points"]    
        
        return batsmen_df 
    
    def __GenerateFantasyPointsDf__(self): 
        batter_df=self.__GenerateRawDf__()
        fantasy_df=pd.DataFrame(columns=['Name','base_points','milestone_points','total_points'])
        for i in range (len(batter_df)):  
            for each_player in self.squad:
                if batter_df.Name[i] in each_player:  
                    #print (batter_df.Name[i]) 
                    total_points=batter_df.base_points[i]+batter_df.milestone_points[i]
                    fantasy_df=fantasy_df.append(pd.Series([each_player,  
                                                            batter_df.base_points[i], batter_df.milestone_points[i], 
                                                            total_points],index=fantasy_df.columns),ignore_index=True) 
        #print (fantasy_df) 
        return (fantasy_df) 
    
    
    def GetFantasyPointsDf(self): 
        return self.__GenerateFantasyPointsDf__() 
    
    def GetFinalFantasyPoints(self): 
        fantasy_df=self.__GenerateFantasyPointsDf__() 
        return sum(fantasy_df['total_points'])
    
        
#################### ---------------------------------##########################


############## Calculate Fantasy Points for Fielding ##################
class FantasyFieldingPoints(object) :
    def __init__(self,batting_score_card,squad,points_per_catch=10): 
        self.batsmen_df=batting_score_card 
        self.squad=squad  
        self.points_per_catch=points_per_catch
        
    def __GenerateRawDf__(self): 
        fielders = []
        for team in [1,2]:          
            for wicket in self.batsmen_df[self.batsmen_df["Team"] == team]["Desc"]:
                if wicket.find("c & b") == 0:
                    fielders.append(wicket.split("c & b")[1].strip())
                elif wicket.find("c") == 0:
                    fielders.append(wicket.split("c ")[1].split("b ")[0].strip())
                if wicket.find("st") == 0:
                    fielders.append(wicket.split("st ")[1].split("b ")[0].strip())
                if wicket.find("run out") == 0:
                    fielders.extend([x.strip() for x in wicket.split("run out")[1].replace('(', '').replace(')', '').split("/")])
                if wicket.find("sub (") != -1:
                    del fielders[-1]
        #print (f' fielders= {fielders}') # for debugging
        fielders = [re.sub(r"\W+", ' ', fielder).strip() for fielder in fielders]          
        #print (f' fielders2 = {fielders}') # for debugging
        
        ## store the fielders dismissals result into a dictionary
        point_dict={} 
        for each in fielders: 
            if each not in point_dict: 
                point_dict[each]=1 
            else: 
                point_dict[each]+=1 
        
        ## convert the points dict dictionary into a df
        fielder_df = pd.DataFrame(columns=['Name','Dismissals','total_points'])  
        for each in point_dict: 
            fielder_df=fielder_df.append(pd.Series([each,point_dict[each],point_dict[each]*10],index=fielder_df.columns),ignore_index=True) 
        
        return fielder_df
    
    def __GenerateFantasyPointsDf__(self): 
        fielder_df=self.__GenerateRawDf__()
        fantasy_df=pd.DataFrame(columns=['Name','base_points','milestone_points','total_points'])
        for i in range (len(fielder_df)):  
            for each_player in self.squad:
                if fielder_df.Name[i] in each_player:  
                    #print (bowler_df.Name[i]) 
                    total_points=fielder_df.total_points[i]
                    fantasy_df=fantasy_df.append(pd.Series([each_player,  
                                                            fielder_df.total_points[i], 0.0, 
                                                            total_points],index=fantasy_df.columns),ignore_index=True) 
        #print (fantasy_df) 
        return (fantasy_df) 
    
    
    def GetFantasyPointsDf(self): 
        return self.__GenerateFantasyPointsDf__() 
    
    def GetFinalFantasyPoints(self): 
        fantasy_df=self.__GenerateFantasyPointsDf__() 
        return sum(fantasy_df['total_points'])
    
        
#################### ---------------------------------##########################



def test():

    #score_url='https://www.espncricinfo.com/series/india-in-south-africa-2021-22-1277060/south-africa-vs-india-1st-test-1277079/full-scorecard'
    score_url='https://www.espncricinfo.com/series/bangladesh-in-new-zealand-2021-22-1288977/new-zealand-vs-bangladesh-1st-test-1288979/full-scorecard'
    #score_url='https://www.espncricinfo.com/series/india-in-south-africa-2021-22-1277060/south-africa-vs-india-1st-test-1277079/full-scorecard'
    #url='https://www.espncricinfo.com/series/super-smash-2021-22-1289602/central-districts-vs-auckland-14th-match-1289618/full-scorecard'
    a=ScoreCardDf(score_url) 
                 
    
    
    ### make me a random squad so i can test ###  
    from ListOfAllPlayers import AllPlayers 
    import random
    squad_url='https://www.espncricinfo.com/series/bangladesh-in-new-zealand-2021-22-1288977/new-zealand-vs-bangladesh-1st-test-1288979/match-playing-xi' 
    squads=AllPlayers(squad_url) 
    full_squad=squads.GetFullSquad() 
    random_squad=[]  
    while len(random_squad)!=11:  
        random_index=random.randrange(len(full_squad)) 
        if full_squad[random_index] not in random_squad:
            random_squad.append(full_squad[random_index])
    
    
    print ('---------------------')
    bowling_score_card=a.GetBowlingDf() 
    b=FantasyBowlingPoints(bowling_score_card, random_squad,30)
    bdf= b.__GenerateRawDf__()
    #print (bdf)
    
    fantasy_df_bowling=b.__GenerateFantasyPointsDf__() 
    print (fantasy_df_bowling) 
    
    
    
    print ('---------------------')
    batting_score_card=a.GetBattingDf() 
    c=FantasyBattingPoints(batting_score_card, random_squad,2)
    cdf= c.__GenerateRawDf__()
    #print (cdf)
    
    fantasy_df_batting=c.__GenerateFantasyPointsDf__() 
    print (fantasy_df_batting)
    
    
    print ('---------------------')
    d=FantasyFieldingPoints(batting_score_card,random_squad)
    ddf= d.__GenerateRawDf__()
    #print (ddf)
    fantasy_df_fielding=d.__GenerateFantasyPointsDf__() 
    print (fantasy_df_fielding) 
    
    print ('---------------------')
    print (f' batting total {c.GetFinalFantasyPoints()}')  
    print (f' bowling total {b.GetFinalFantasyPoints()}')  
    print (f' fielding total {d.GetFinalFantasyPoints()}')  
    
    total=c.GetFinalFantasyPoints()+b.GetFinalFantasyPoints()+d.GetFinalFantasyPoints()
    print (total)


if __name__=="__main__": 
    test()
