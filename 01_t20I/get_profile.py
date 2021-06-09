#!/usr/bin/env python3

import numpy as np
import pandas as pd
import datetime, pickle

data_dir = "./database/"

def add_overs(overs):
    # given a list of overs returns total over
    # example: [1.2, ]
    ov_int = 0
    ov_frac = 0

    dtype = str(type(overs[0]))
    for ov in overs:
        ov = str(ov)
        ov_split = ov.split('.')
        ov_int  += int(ov_split[0])

        if len(ov_split)>1:
            ov_frac += int(ov_split[1])

        if ov_frac >= 6:
            ov_int += ov_frac//6
            ov_frac = ov_frac %6

    if ov_frac==0:
        if 'str' not in dtype:
            return ov_int
        else:
            return str(ov_int)
    else:
        if 'str' not in dtype:
            return ov_int+ov_frac*0.1
        else:
            return str(ov_int)+'.'+str(ov_frac)

def Over2Balls(Over):
    ov_split = Over.split('.')
    all_balls = int(ov_split[0])*6

    if len(ov_split) > 1:
        all_balls += int( ov_split[1] )
    return all_balls

def get_player_profile(player, batsman=True, year_from=2008, year_to=2021, ipl=False, t20=False):
    
    if batsman:
        if ipl:
            df=pickle.load(open(data_dir+'03_ipl/batting.df', 'rb'))
        elif t20:
            df=pickle.load(open(data_dir+'01_t20s/batting.df', 'rb'))

        data_player=[]
        for season in range(year_from, year_to, 1): 
            dfp   = df[ (df['season']==str(season)) & (df['batsman']==player) ]
            Inns_ = dfp.shape[0]

            if Inns_ != 0:
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

    else:
        if ipl:
            df=pickle.load(open(data_dir+'03_ipl/bowling.df', 'rb'))
        elif t20:
            df=pickle.load(open(data_dir+'01_t20s/bowling.df', 'rb'))

        data_player=[]
        for season in range(year_from, year_to, 1):
            dfp   = df[ (df['season']==str(season)) & (df['bowler']==player) ]
            Inns_ = dfp.shape[0]

            if Inns_ != 0:
                Team_ = dfp.Team.values[0]
                Ovs_  = add_overs(dfp['O'].values)
                Wkts_ = dfp['W'].sum()
                Runs_ = dfp['Runs'].sum()

                #HS_   = max(dfp.Runs) to be calculated for best bowling figures
                
                Balls_ = Over2Balls(Ovs_)
                
                SR_   = 0.
                Ave_  = 0.
                if Wkts_ > 0:
                    SR_   = round( Balls_ / Wkts_ , 2 )
                    Ave_  = round( Runs_ / Wkts_  , 2 )

                Fours_= dfp['4s'].sum()
                Sixes_= dfp['6s'].sum()
                WDs_  = dfp['WD'].sum()
                NBs_  = dfp['NB'].sum()

                NoWs_= ((dfp['W']==0)).sum()
                ThreeWs_= ((dfp['W']>=3)).sum()
                FourWs_ = ((dfp['W']>=4)).sum()
                FiveWs_ = ((dfp['W']>=5)).sum()
                
                data_player.append([season, Team_, Inns_, Ovs_, Wkts_, SR_, Ave_, Fours_, Sixes_,
                                    WDs_, NBs_, NoWs_, ThreeWs_, FourWs_, FiveWs_])

        df_p = pd.DataFrame(data_player, columns=['season', 'Team', 'Innings', 'Overs', 'Wickets', 
                                                  'SR', 'Ave', 'Fours', 'Sixes', 'WDs', 'NBs',
                                                  '0-Fers', '3-Fers', '4-Fers', '5-Fers'])                       
        return df_p

if __name__=="__main__":
    player='NA Saini'
    #player='SK Raina'
    player='MS Dhoni'
    dfp=get_player_profile(player, batsman=True)
    #print (dfp)
    print (dfp)
    #df=get_match_list()
    #print ( df.head() )
