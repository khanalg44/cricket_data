#!/usr/bin/env python3

import numpy as np
import pandas as pd
import datetime, pickle

def get_player_profile(player, batsman=True):
    
    if batsman:
        df=pickle.load(open('./database/batting_record_all_years.df', 'rb'))

        data_player=[]
        for season in range(2008, 2021, 1): 
            dfp   = df[ (df['season']==str(season)) & (df['batsman']==player) ]
            Inns_ = dfp.shape[0]

            if Inns_ == 0:
                data_player.append([season,' ', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] )
            else:
                Team_ = dfp.Team.values[0]
                Runs_ = dfp.Runs.sum()
                BF_   = dfp.BF.sum()
                NOs_  = int(dfp.NO.sum())
                HS_   = max(dfp.Runs)
                SR_   = np.round(100*Runs_/BF_, 2)
                if Inns_ == NOs_:
                    Ave_  = Runs_
                else:
                    Ave_  = np.round(Runs_/(Inns_-NOs_), 2)
                Fours_= dfp['4s'].sum()
                Sixes_= dfp['6s'].sum()
                Fifty_= ((dfp.Runs>=50) & (dfp.Runs<100) ).sum()
                Hundred_= (dfp.Runs>=100).sum()
    
                data_player.append([season, Team_, Inns_, NOs_, Runs_, BF_, HS_, Ave_, SR_, Fifty_, Hundred_, Fours_, Sixes_] )
        df_p = pd.DataFrame(data_player, columns=['season', 'Team', 'Innings', 'NO', 'Runs', 'BF', 'HS', 'Ave','SR', '50s', '100s', '4s', '6s'])
        return df_p

if __name__=="__main__":
    #player='NA Saini'
    #dfp=get_player_profile(player, batsman=False)
    player='SK Raina'
    #player='MS Dhoni'
    dfp=get_player_profile(player, batsman=True)
    #print (dfp)
    print (dfp)
    #df=get_match_list()
    #print ( df.head() )
