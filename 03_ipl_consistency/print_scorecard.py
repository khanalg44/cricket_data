#!/usr/bin/env python3

import numpy as np
import pandas as pd
import os, sys, yaml

data_dir='../datasets/ipl/yaml/'

def print_scorecard(f, data_dir='./'):
    
    fil=os.path.join(data_dir,  f )
    #data=yaml.load(open(fil))

    with open(fil, 'r') as stream:
        try:
            data = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)


    batting_card = {}    
    for inn in range(2):
        inn_name = list(data['innings'][inn].keys())[0]

        batting_card_inn={}
        batting_card_inn[inn_name] = {'0':' ', '1':' ', '2':' ', '3':' ', '4':' ', '5':' ', '6':' ', 'R':' ', 'B':' '}
        
        runs_bowler={}
        runs_extra = 0
        runs_total = 0
        wkts       = 0

        for delivery in list(data['innings'][inn].values())[0]['deliveries']:
            deliv = list(delivery.items())[0]
            
            ball     = deliv[0]
            batsman  = deliv[1]['batsman'].strip()
            bowler   = deliv[1]['bowler'].strip()
            runs_bat = deliv[1]['runs'].get('batsman', 0)
            runs_ext = deliv[1]['runs'].get('extras',  0)
            runs_tot = deliv[1]['runs'].get('total',   0)
            
            if batsman not in batting_card_inn:
                batting_card_inn[batsman] = {'0':0, '1':0, '2':0, '3':0, '4':0,  '5':0, '6':0, 'R':0, 'B':0}

            batting_card_inn[batsman][str(runs_bat)] = batting_card_inn[batsman][str(runs_bat)]+1
            batting_card_inn[batsman]['R'] += runs_bat
            batting_card_inn[batsman]['B'] += 1 # remove the ball later if it's a wide
            
            if 'extras' in deliv[1]:
                if 'wides' in deliv[1]['extras']:
                    batting_card_inn[batsman]['B'] -= 1 # remove the ball from batsman's account

            runs_extra += runs_ext
            runs_total += runs_tot
            
            if deliv[1].get('wicket', None):
                wkts += 1

        batting_card_inn['Total_inn'+str(inn+1)] = {'0':' ', '1':' ', '2':' ', '3':' ', '4':' ', '5':' ', '6':' ',
                                                    'R':str(runs_total)+'-'+str(wkts), 'B':' '}
        # empty row
        batting_card_inn['  '] = {'0':' ', '1':' ', '2':' ', '3':' ', '4':' ', '5':' ', '6':' ', 'R':' ', 'B':' '}        
        batting_card.update(batting_card_inn)        

    
    df = pd.DataFrame(batting_card).transpose()
    df.style.set_caption("Title")
    
    
    print ()
    print ("------------------------------- Match Info-------------------------------")
    print (data['info']['teams'][0] ,' vs ', data['info']['teams'][1], ', ', data['info']['dates'][0].strftime('%Y-%m-%d'))
    print ( 'Toss \t\t\t', data['info']['toss']['winner'], 'Decided to', data['info']['toss']['decision'])
    print ('Result \t\t\t', data['info']['outcome']['winner'], 'won by ', 
           list(data['info']['outcome']['by'].values())[0], list(data['info']['outcome']['by'].keys())[0])
    print ('Player of the Match\t', data['info']['player_of_match'][0])
    print ()
    print ("------------------------------- BATTING SCORECARD -------------------------------")
    print ()
    print ()
    print (df)

    return df
    

if __name__=='__main__':

    f = '335982.yaml'
    f = '335989.yaml'
    if len(sys.argv)>1:
        f=sys.argv[1]

    print_scorecard(f, data_dir=data_dir)
