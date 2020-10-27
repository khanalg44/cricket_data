#!/usr/bin/env python3

import numpy as np
import pandas as pd
import datetime, pickle

def get_match_list(year=None, fil='../datasets/ipl/README.txt'):
    f_in = open(fil, 'r')
    lines= f_in.readlines()
    matches = []
    for line in lines[::-1]:  # reversed to get the games sorted with date
        if (len(line)>2 and line[:2]=='20'):
            line_  = line.strip('\n').split(' - ')
            
            date = line_[0]
            match_id = line_[4]
            match_teams = line_[5].strip().split('vs')
            matches.append([date, match_id, match_teams[0].strip(), match_teams[1].strip()])
            
    df_matches = pd.DataFrame(matches, columns=['date', 'match_id', 'team1', 'team2'])
    df_matches['date'] = pd.to_datetime(df_matches['date'])

    if year:
        df_year = df_matches[(df_matches['date']>=datetime.datetime(year, 1,   1)) & 
                         (df_matches['date']<=datetime.datetime(year, 12, 31))]
        return df_year

    return df_matches

def get_player_profile(player):
    df=pickle.load(open('./database/scorecard_all.df', 'rb'))

    data=[]
    for season in range(2008, 2020, 1):
        dfp   = df[ (df['season']==str(season)) & (df['batsman']==player) ]
        Inns_ = dfp.shape[0]
        Runs_ = dfp.Runs.sum()
        BF_   = dfp.BF.sum()
        NOs_  = dfp.NO.sum()
        HS_   = max(dfp.Runs)
        SR_   = np.round(100*Runs_/BF_, 2)
        Ave_  = np.round(Runs_/(Inns_-NOs_), 2)
        Fours_= dfp['4'].sum()
        Sixes_= dfp['6'].sum()
        Fifty_= ((dfp.Runs>=50) & (dfp.Runs<100) ).sum()
        Hundred_= (dfp.Runs>=100).sum()

        data.append([season, Inns_, NOs_, Runs_, BF_, HS_, Ave_, SR_, Fifty_, Hundred_, Fours_, Sixes_] )
    df_p = pd.DataFrame(data, columns=['season', 'Innings', 'NO', 'Runs', 'BF', 'HS', 'Ave','SR', '50s', '100s', '4s', '6s'])
    return df_p


if __name__=="__main__":
    df=get_match_list()
    print ( df.head() )
