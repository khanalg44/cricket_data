#!/usr/bin/env python3

import numpy as np
import yaml, os, sys
import pandas as pd

def read_match_info(fil):
    with open(fil, 'r') as stream:
        try:
            data = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    try:
        match_date=data['info']['dates'][0].strftime('%Y-%m-%d')
    except:
        match_date=data['info']['dates'][0]

    season = match_date.split('-')[0]
    teams  = data['info']['teams']
    winner = data['info']['outcome'].get('winner', None)
    win_margin    = list(data['info']['outcome']['by'].values())[0]
    win_type      = list(data['info']['outcome']['by'].keys())[0]
    toss_winner   = data['info']['toss'].get('winner', None)
    toss_decision = data['info']['toss'].get('decision', None)

    batting_1st_team = list(data['innings'][0].items())[0][1]['team']

    print (teams[0] ,' vs ', teams[1], ', On ', match_date)
    print ('---------------------------------------------------------------')
    print ( 'Toss \t\t\t', toss_winner, 'Decided to', toss_decision)
    print ('Team Batting First\t', batting_1st_team)
    print ('Result \t\t\t', winner, 'won by ', win_margin, win_type )
    print ('Player of the Match\t', data['info']['player_of_match'][0])
    print ('---------------------------------------------------------------')


def print_scorecard(f, data_dir='./'):
    fil=os.path.join(data_dir, f )
    
    with open(fil, 'r') as stream:
        try:
            data = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    
    try:
        match_date=data['info']['dates'][0].strftime('%Y-%m-%d')
    except:
        match_date=data['info']['dates'][0]
    
    season = match_date.split('-')[0]
    teams  = data['info']['teams']
    winner = data['info']['outcome'].get('winner', None)
    toss_winner = data['info']['toss'].get('winner', None)
    
    
    def add_player(player, scorecard, season=season, Team=' ', Against=' '):
        if player not in scorecard:
            scorecard[player] = {'0':0, '1':0, '2':0, '3':0, '4':0, '5':0, '6':0,
                                 'Runs':0, 'BF':0, 'NO':True, 'Team':Team, 'Against':Against,
                                 'Win':False, 'Toss':False, 'team-total':0, 'season':season}
    batting_card = {}
    
    for i, inn in enumerate(data['innings']):
        inn_name     = list(inn.keys())[0]

        batting_team = data['innings'][i][inn_name]['team']
        bowling_team = [team for team in  teams if team!=batting_team][0]

        batting_card_inn={}
        runs_bowler={}
        runs_extra = 0
        runs_total = 0
        wkts       = 0
        
        for delivery in data['innings'][i][inn_name]['deliveries']:
            deliv    = list(delivery.items())[0]

            ball     = deliv[0]
            batsman  = deliv[1]['batsman'].strip()
            bowler   = deliv[1]['bowler'].strip()
            runs_bat = deliv[1]['runs'].get('batsman', 0)
            runs_ext = deliv[1]['runs'].get('extras',  0)
            runs_tot = deliv[1]['runs'].get('total',   0)
            
            add_player(batsman, batting_card_inn)

            # counter for each runs (1, 2, 3, 4, 5, 6)
            batting_card_inn[batsman][str(runs_bat)] += 1
            
            # counter for total batsman run
            batting_card_inn[batsman]['Runs']        += runs_bat
            
            # counter for toal balls faced [ball will be removed later if it's a wide]
            batting_card_inn[batsman]['BF']          += 1
            
            if 'extras' in deliv[1]:
                if 'wides' in deliv[1]['extras']:
                    batting_card_inn[batsman]['BF']  -= 1 # remove the ball from batsman's account

            runs_extra += runs_ext
            runs_total += runs_tot
            
            if deliv[1].get('wicket', None):
                wkts += 1
                player_out = deliv[1]['wicket']['player_out']
                
                # for case when player is runout without facing a ball
                add_player(player_out, batting_card_inn, Team=batting_team, Against=bowling_team)
                batting_card_inn[player_out]['NO']=False
                
            batting_card_inn[batsman]['Team']     = batting_team
            batting_card_inn[batsman]['Against']  = bowling_team
            
            if batting_team == winner:
                batting_card_inn[batsman]['Win']  = True
                
            if batting_team == toss_winner:
                batting_card_inn[batsman]['Toss'] = True
            
        for b in batting_card_inn.keys():
            batting_card_inn[b]['team-total']     = runs_total

            
        #batting_card_inn['Total_inn'+str(i+1)]= {'0':' ', '1':' ', '2':' ', '3':' ', '4':' ', '5':' ', '6':' ',
        #                         'Runs':' ', 'BF':' ', 'NO':' ', 'Team':' ', 'Against':' ',
        #                         'Win':' ', 'Toss':' ', 'team-total':str(runs_total)+'-'+str(wkts), 'season':' '}
            
        batting_card.update(batting_card_inn)
    
    df = pd.DataFrame(batting_card).transpose()
    
    df.reset_index(inplace=True)
    df.rename(columns={"index": "batsman"}, inplace=True)
    df['date']=match_date
    df['match-id']=f.split('/')[-1].split('.')[0]
    
    read_match_info(fil)

    return df

def nice_scorecard(f, data_dir='./'):
    df_ = print_scorecard(f, data_dir=data_dir)
    df_nice = df_[['batsman', 'Runs', 'BF', '4', '6', 'team-total']]
    return df_nice


if __name__=="__main__":
    f='../datasets/ipl/yaml/336002.yaml'
    df=nice_scorecard(f)
    if 'full' in sys.argv:
        df=print_scorecard(f)
    print (df)

