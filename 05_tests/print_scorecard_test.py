#!/usr/bin/env python3

import pandas as pd
import os, yaml

data_dir='../datasets/test_matches/tests_male/'

def read_ball_by_ball(f, data_dir='./'):
    fil=os.path.join(data_dir, f )
    match_id = f.split('/')[-1].split('.')[0]

    with open(fil, 'r') as stream:
        try:
            data = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    try:
        match_date=data['info']['dates'][0].strftime('%Y-%m-%d')
    except:
        match_date=data['info']['dates'][0]

    num_inns = len(data['innings'])
    inns  = {list(data['innings'][i].keys())[0]: list(data['innings'][i].values())[0]['team']
             for i in range(num_inns) }

    teams  = data['info']['teams']
    winner = data['info']['outcome'].get('winner', None)
    draw   = False
    if winner is None:
        draw = True

    toss_winner = data['info']['toss'].get('winner', None)

    score_card = []

    for i, inn in enumerate(inns):
        batting_team = inns[inn]
        bowling_team = [team for team in  teams if team != batting_team][0]

        for delivery in data['innings'][i][inn]['deliveries']:
            deliv    = list(delivery.items())[0]
            ball     = deliv[0]
            ov_num   = int(str(ball+1).split('.')[0])

            batsman  = deliv[1]['batsman'].strip()
            bowler   = deliv[1]['bowler'].strip()
            non_striker = deliv[1]['non_striker']

            runs_bat = deliv[1]['runs'].get('batsman', 0)
            runs_ext = deliv[1]['runs'].get('extras',  0)
            runs_tot = deliv[1]['runs'].get('total',   0)

            runs_type={str(i)+'s':0 for i in range(8)}
            runs_type[str(runs_bat)+'s'] += 1

            wd = 0; nb = 0; lb = 0; byes = 0;
            if 'extras' in deliv[1]:
                wd = deliv[1]['extras'].get('wides', 0)
                nb = deliv[1]['extras'].get('noballs', 0)
                lb = deliv[1]['extras'].get('legbyes', 0)
                byes = deliv[1]['extras'].get('byes', 0)
            exts = {'wd':wd, 'nb':nb, 'lb':lb, 'byes':byes}

            wkt = False; player_out = ''; out_kind = ''; out_fielder = ''

            if 'wicket' in deliv[1]:
                wkt = True
                player_out = deliv[1]['wicket']['player_out']
                out_kind   = deliv[1]['wicket']['kind']
                if deliv[1]['wicket'].get('fielders', None):
                    out_fielder = deliv[1]['wicket']['fielders']

            info_deliv = [inn, ball, batsman, bowler, non_striker, runs_bat, runs_ext, runs_tot, runs_type,
                          exts, wkt, player_out, out_kind, out_fielder, batting_team, bowling_team,
                          winner, toss_winner, draw, match_date, match_id]
            score_card.append( info_deliv )

    columns = ["innings", "over", "batsman", "bowler", "non_striker", "runs_bat", "runs_ext", "runs_tot", "runs_type",
               "extra", "wicket", "player_out", "out_kind", "out_fielder", "batting_team", "bowling_team",
               "winner", "toss_winner", "draw", "match_date", "match_id"]
    df = pd.DataFrame(score_card, columns = columns)

    return df



def print_scorecard(f, data_dir='./'):
    df = read_ball_by_ball(f, data_dir=data_dir)
    
    all_inns = df['innings'].unique()
    
    winner = df['winner'].unique()[0]
    draw   = df['draw'].values[0]
    toss_winner = df['toss_winner'].unique()[0]
    #print (winner, toss_winner, draw)
    
    batting_card = []
    bowling_card = []
    for inn in all_inns:
        #print (inn)
        dfi = df[df['innings']==inn]
        
        batting_team = dfi['batting_team'].unique()[0]
        bowling_team = dfi['bowling_team'].unique()[0]
        
        match_date   = dfi['match_date'].values[0]
        match_id     = dfi['match_id'].values[0] 
        

        all_batsman = dfi['batsman'].unique()
        all_bowler  = dfi['bowler'].unique()
        all_players = list(all_batsman) + list(all_bowler)
        #print (all_players)
        all_bat_out = [d for d in dfi['player_out'] if d]
        runs_tot = dfi['runs_tot'].sum()
        wkts_tot = dfi['wicket'].sum()
        #print (inn, runs_tot, wkts_tot)
        for player in all_players:
            
            dfbat = dfi[dfi['batsman']==player]
            if (dfbat.shape[0]>0) or (player in all_bat_out) :  # second condition if batsman runout for 0(0)
                runs = dfbat['runs_bat'].sum()
                balls = dfbat['over'].shape[0] - sum([d['wd'] for d in dfbat['extra']])
                not_out = [False if player in all_bat_out else True][0]

                runs_type = [sum([d[str(i)+'s'] for d in dfbat['runs_type']]) for i in range(8) ]
                zeros, ones, twos, threes, fours, fives, sixes, sevens = runs_type
                
                win  = (winner == batting_team)
                toss = (toss_winner == batting_team)

                info_bat = [player, runs, balls, not_out, zeros, ones, twos, threes, fours, fives, sixes, sevens,
                            inn, batting_team, bowling_team, match_date, match_id, win, draw, toss,
                            runs_tot, wkts_tot]
                
                batting_card.append( info_bat )
            
            dfbwl = dfi[dfi['bowler']==player]
            if dfbwl.shape[0]>0:
                overs = dfbwl['over'].values
                runs_bat = dfbwl['runs_bat'].values
                runs_ext = dfbwl['runs_ext'].values
                runs_tot = dfbwl['runs_tot'].values
                
                runs_type = [sum( [d[str(i)+'s'] for d in dfbwl['runs_type']] ) for i in range(8) ]
                zeros, ones, twos, threes, fours, fives, sixes, sevens = runs_type
                
                wide_balls = [d['wd'] for d in dfbwl['extra'] if d['wd'] !=0]
                no_balls   = [d['nb'] for d in dfbwl['extra'] if d['nb'] !=0]
                wide_runs  = sum(wide_balls)
                noball_runs = sum(no_balls)

                total_balls_bowled = dfbwl.over.count() - len(wide_balls) - len(no_balls)
                ov, balls_ = (total_balls_bowled//6, total_balls_bowled%6)
                total_runs_given   = dfbwl.runs_tot.sum() - sum([d['lb']+d['byes'] for d in dfbwl['extra']])
                
                ov, balls_ = (total_balls_bowled//6, total_balls_bowled%6)

                ov_dict = {(ov+1):{'R':0, 'W':0} for ov in dfbwl.over.astype(int).unique()}
                for i in range(len(overs)):
                    ov_int = int(dfbwl.over.iloc[i])+1
                    runs_  = dfbwl.runs_tot.iloc[i] # - dfbwl.extra.iloc[i]['lb'] - dfbwl.extra.iloc[i]['byes']
                    wkts_  = dfbwl.wicket.iloc[i].astype(int)
                    ov_dict[ov_int]['R'] += runs_
                    ov_dict[ov_int]['W'] += wkts_
                    
                maidens = sum([1 for i in ov_dict if ov_dict[i]['R']==0])
                wds = sum([ d['wd'] for d in dfbwl['extra'] ] )
                nbs = sum([ d['nb'] for d in dfbwl['extra'] ] )
                
                wkt_taken = dfbwl['wicket'].sum() -\
                        dfbwl[dfbwl['out_kind']=='run out'].shape[0] -\
                        dfbwl[dfbwl['out_kind']=='retired hurt'].shape[0]

                ov = str(ov)
                if balls_>0:
                    ov = str(ov)+'.'+str(balls_)
                    
                win  = (winner == bowling_team)
                toss = (toss_winner == bowling_team)
                    
                info_ball = [player, ov, maidens, total_runs_given, wkt_taken, inn, ov_dict,
                             zeros, ones, twos, threes, fours, fives, sixes, sevens, wds, nbs, 
                             match_date, match_id, win, draw, toss ]
                
                bowling_card.append( info_ball )

            #print (batsman, runs, balls, not_out, zeros, ones, twos, threes, fours, fives, sixes,
            #batting_team, bowling_team, match_date, match_id, win, draw, toss)


    col_bat = ['batsman', 'runs', 'BF', 'NO', '0s', '1s', '2s', '3s', '4s', '5s', '6s', '7s',
               'innings', 'Team', 'Against', 'date',  'match_id', 'Win', 'Draw', 'Toss',
               'runs_tot_inn', 'wkts_tot_inn']
    df_bat  = pd.DataFrame(batting_card, columns=col_bat)
    
    col_bowl = ['bowler', 'O', 'M', 'R', 'W', 'innings', 'all_overs',
               '0s', '1s', '2s', '3s', '4s', '5s', '6s', '7s', 'wds', 'nbs',
               'date', 'match_id', 'Win', 'draw', 'Toss']
    df_bowl = pd.DataFrame(bowling_card, columns=col_bowl)
    
    return df_bat, df_bowl

if __name__=="__main__":
    f = data_dir+'1223869.yaml'
    df = read_ball_by_ball(f)
    print (df.columns)
    df_bat, df_bowl = print_scorecard(f)#, data_dir=data_dir)
    print ( df_bowl.columns )
