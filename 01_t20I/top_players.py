#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import pickle

data_dir= '../database/01_t20s/'

def batting_summary_():
    df = pickle.load(open(data_dir+'batting.df', 'rb'))
    all_players = df['batsman'].unique()
    
    data=[]
    for player in all_players:
        dfp = df[ df['batsman']==player ]
        
        Inns_ = dfp.shape[0]
        Runs_ = dfp.Runs.sum()
        BF_   = dfp.BF.sum()
        NOs_  = dfp.NO.sum()
        
        HS    = max(dfp.Runs)
        Fifty = ((dfp.Runs>=50) & (dfp.Runs<100) ).sum()
        Hundred = (dfp.Runs>=100).sum()
        
        Wins  = sum(dfp.Win)
        Toss_wins = sum(dfp.Toss)
        
        SR    = np.round(100*Runs_/(BF_+0.1), 2) # add 0.1 to avoide deviding by 0
        
        if Inns_== NOs_:
            Ave=dfp.Runs.sum() 
        else:
            Ave   = np.round(Runs_/(Inns_-NOs_), 2)
        Fours = dfp['4s'].sum()
        Sixes = dfp['6s'].sum()

        data.append([player, Inns_, NOs_, Runs_, BF_, HS, Ave, SR, Fifty, Hundred, Fours, Sixes] )
    df_p = pd.DataFrame(data, columns=['player', 'Innings', 'NO', 'Runs', 'BF', 'HS',
                                       'Ave','SR', '50s', '100s', '4s', '6s'])
    return df_p

def sorted_table(sort_by='Runs'):
    df_summary = batting_summary_()
    return df_summary.sort_values(by=[sort_by], ascending=False)

if __name__=="__main__":

    #df_summary= batting_summary_()
    df_summary= sorted_table(sort_by='Runs')
    print ( df_summary.head(2) )
