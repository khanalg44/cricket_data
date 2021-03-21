#!/usr/bin/env python3

import numpy as np
import yaml, os, sys
import pandas as pd

data_dir='../datasets/t20s_male/'

def print_scorecard(f, data_dir=data_dir):
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

    tied = False
    if data['info']['outcome'].get('result', None)== 'tie':
        winner = data['info']['outcome'].get('bowl_out', None)
        tied = True

    def convert_to_ov(balls):
        ov, balls_ = (balls//6, balls%6)
        if balls_==0:
            return str(ov)
        else:
            return str(ov)+'.'+str(balls_)


    def add_batsman(player, batting_scorecard, season=season, Team=' ', Against=' '):
        if player not in batting_scorecard:
            batting_scorecard[player] = {'0s':0, '1s':0, '2s':0, '3s':0, '4s':0, '5s':0, '6s':0, '7s':0,
                                         'R':0, 'BF':0, 'NO':True, 'Team':Team, 'Against':Against, 'Tied':tied,
                                         'Win':False, 'Toss':False, 'team-total':0, 'season':season}

    def add_bowler(player,   bowling_scorecard, season=season, Team=' ', Against=' '):
        if player not in bowling_scorecard:
            bowling_scorecard[player] = {'O':0, 'M':0, 'R':0, 'W':0, 'ovs':{},
                    '0s':0, '1s':0, '2s':0, '3s':0, '4s':0, '5s':0, '6s':0, '7s':0,
                                         'WD':0, 'NB':0, 'Team':Team, 'Against':Against, 'Win':False, 'Tied':tied,
                                         'Toss':False, 'team-total':0, 'season':season}

    batting_card = {}
    bowling_card = {}

    innings = [list(d.keys())[0] for d in data['innings'] if 'Super' not in list(d.keys())[0] ]

    for i, inn_name in enumerate(innings):
        batting_team = data['innings'][i][inn_name]['team']
        bowling_team = [team for team in  teams if team!=batting_team][0]

        batting_card_inn={}
        bowling_card_inn={}

        runs_extra = 0
        runs_total = 0
        wkts       = 0

        for delivery in data['innings'][i][inn_name]['deliveries']:
            deliv    = list(delivery.items())[0]
            ball     = deliv[0]
            ov_num   = int(str(ball+1).split('.')[0])

            batsman  = deliv[1]['batsman'].strip()
            bowler   = deliv[1]['bowler'].strip()
            runs_bat = deliv[1]['runs'].get('batsman', 0)
            runs_ext = deliv[1]['runs'].get('extras',  0)
            runs_tot = deliv[1]['runs'].get('total',   0)

            add_batsman(batsman, batting_card_inn)
            add_bowler(bowler , bowling_card_inn)

            # counter for each runs (1, 2, 3, 4, 5, 6)
            batting_card_inn[batsman][str(runs_bat)+'s'] += 1
            bowling_card_inn[bowler ][str(runs_bat)+'s'] += 1

            # first check if the over exists on the dictionary
            if not bowling_card_inn[bowler ]['ovs'].get(ov_num, False):
                bowling_card_inn[bowler ]['ovs'][ov_num] = {'R':0, 'W':0}
            bowling_card_inn[bowler ]['ovs'][ov_num]['R'] += runs_tot

            # counter for total batsman run
            batting_card_inn[batsman]['R']           += runs_bat
            batting_card_inn[batsman]['BF']          += 1

            bowling_card_inn[bowler ]['R']           += runs_tot
            bowling_card_inn[bowler ]['O']           += 1

            if 'extras' in deliv[1]:
                if 'wides' in deliv[1]['extras']:
                    batting_card_inn[batsman]['BF'] -= 1 # remove the ball from batsman's account
                    bowling_card_inn[bowler]['O']   -= 1 # to count the extra ball
                    bowling_card_inn[bowler]['WD']  += 1 #

                elif 'noballs' in deliv[1]['extras']:
                    bowling_card_inn[bowler]['O']   -= 1 # to count the extra ball
                    bowling_card_inn[bowler]['NB']  += 1 #

                elif 'legbyes' in deliv[1]['extras']:
                    #bowling_card_inn[bowler]['R']   -= 1 #
                    bowling_card_inn[bowler]['R']   -= deliv[1]['extras']['legbyes']
                    bowling_card_inn[bowler ]['ovs'][ov_num]['R'] -= deliv[1]['extras']['legbyes']

                elif 'byes' in deliv[1]['extras']:
                    bowling_card_inn[bowler]['R']   -= deliv[1]['extras']['byes']

            runs_extra += runs_ext
            runs_total += runs_tot

            if deliv[1].get('wicket', None):
                wkts += 1
                player_out = deliv[1]['wicket']['player_out']

                # for case when player is runout without facing a ball
                add_batsman(player_out, batting_card_inn, Team=batting_team, Against=bowling_team)
                batting_card_inn[player_out]['NO'] = False

                # add wicket to bowler only if it's not RUN OUT
                if deliv[1]['wicket']['kind'] != 'run out':
                    bowling_card_inn[bowler ]['W']                += 1
                    bowling_card_inn[bowler ]['ovs'][ov_num]['W'] += 1

            batting_card_inn[batsman]['Team']    = batting_team
            batting_card_inn[batsman]['Against'] = bowling_team

            bowling_card_inn[bowler ]['Team']    = bowling_team
            bowling_card_inn[bowler ]['Against'] = batting_team

            if batting_team == winner:
                batting_card_inn[batsman]['Win'] = True
            else:
                bowling_card_inn[bowler ]['Win'] = True

            if batting_team == toss_winner:
                batting_card_inn[batsman]['Toss'] = True
            else:
                bowling_card_inn[bowler]['Toss'] = True

        for b in batting_card_inn.keys():
            batting_card_inn[b]['team-total'] = runs_total

        for b in bowling_card_inn.keys():
            bowling_card_inn[b]['team-total'] = runs_total
            bowling_card_inn[b]['O'] = convert_to_ov(bowling_card_inn[b]['O'])

        batting_card.update(batting_card_inn)
        bowling_card.update(bowling_card_inn)

    df_bat = pd.DataFrame(batting_card).transpose()

    df_bat.reset_index(inplace=True)
    df_bat.rename(columns={"index": "batsman"}, inplace=True)
    df_bat['date']=match_date
    df_bat['match-id']=f.split('/')[-1].split('.')[0]

    df_bowl = pd.DataFrame(bowling_card).transpose()

    df_bowl.reset_index(inplace=True)
    df_bowl.rename(columns={"index": "bowler"}, inplace=True)
    df_bowl['date']=match_date
    df_bowl['match-id']=f.split('/')[-1].split('.')[0]

    return (df_bat, df_bowl)
