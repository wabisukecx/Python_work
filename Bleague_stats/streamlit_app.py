import streamlit as st
import sqlite3
import pandas as pd
import math

def calculate_ppp(PTS, FGA, FTA, TO):
    possessions = FGA + 0.44 * FTA + TO
    ppp = PTS / possessions
    return ppp

def calculate_poss(FGA, FTA, TOV):
    poss = FGA + 0.44 * FTA + TOV
    return poss

def calculate_efg_percent(FGM, TFGM, FGA):
    efg_percent = (FGM + 0.5 * TFGM) / FGA * 100
    return efg_percent

def calculate_or_percent(OR, OpponentDR):
    or_percent = (OR / (OR + OpponentDR)) * 100
    return or_percent

def calculate_to_percent(TO, FGA, FTA):
    to_percent = (TO / (FGA + 0.44 * FTA + TO)) * 100
    return to_percent

def calculate_pace(Tm_Poss, Op_Poss, Tm_MP):
    pace = 40 * (Tm_Poss + Op_Poss) / (2 * Tm_MP / 5)
    return pace

def calculate_per(MP, threeP, AST, team_AST, team_FG, FG, FT, TOV, FGA, FTA,
                DRB, ORB, STL, BLK, PF, lg_FT, lg_PF, lg_FTA, lg_PTS,
                lg_FGA, lg_ORB, lg_TOV, lg_TRB, lg_AST, lg_FG):
    if MP == 0:
        return 0

    # Calculate factors used in the formula
    factor = (2 / 3) - (0.5 * (lg_AST / lg_FG)) / (2 * (lg_FG / lg_FT))
    VOP = lg_PTS / (lg_FGA - lg_ORB + lg_TOV + 0.44 * lg_FTA)
    DRB_perc = (lg_TRB - lg_ORB) / lg_TRB
    ApFGM = team_AST / team_FG

    # Calculate parts of the PER formula
    t_fgm = (2 - factor * ApFGM) * FG
    t_ftm = (FT * 0.5 * (1 + (1 - ApFGM) + (2/3) * ApFGM))
    t_ast = (2/3) * AST
    t_orb = VOP * DRB_perc * ORB
    t_drb = VOP * (1 - DRB_perc) * DRB
    t_stl = VOP * STL
    t_blk = VOP * DRB_perc * BLK
    t_fgmiss = VOP * DRB_perc * (FGA - FG)
    t_ftmiss = VOP * 0.44 * (0.44 + (0.56 * DRB_perc)) * (FTA - FT)
    t_tov = VOP * TOV
    t_foul = ((lg_FT / lg_PF) - 0.44 * (lg_FTA / lg_PF) * VOP) * PF

    # Final PER calculation
    uper = (threeP + t_fgm + t_ftm + t_ast + t_orb + t_drb + t_stl + t_blk -
            t_fgmiss - t_ftmiss - t_tov - t_foul) / MP

    return uper

def get_per(tgt_team, conn):

    aper_list = []
    per_list = []
    per_name_list = []

    # Fetch league and team statistics in fewer queries
    league_stats_query = "SELECT * FROM player_stats"
    league_stats_df = pd.read_sql(league_stats_query, conn)

    team_stats_df = league_stats_df[league_stats_df['team'] == tgt_team]

    # Aggregate league and team statistics
    league = league_stats_df.agg('sum').to_dict()
    team = team_stats_df.agg('sum').to_dict()

    team_poss = calculate_poss(team['fga'], team['fta'], team['tov'])
    team_pace = calculate_pace(team_poss, team_poss, team['minute'])
    league_poss = calculate_poss(league['fga'], league['fta'], league['tov'])
    league_pace = calculate_pace(league_poss, league_poss, league['minute'])

    # Fetch player stats for all players in one query
    player_stats_query = "SELECT * FROM player_stats"
    all_player_stats_df = pd.read_sql(player_stats_query, conn)

    # Initialize variables for league average PER calculation
    league_aper = 0
    num_players = len(all_player_stats_df)

    # Iterate over all players
    for _, player in all_player_stats_df.iterrows():
        player_name = player['name']

        # Calculate uPER for the player
        uper = calculate_per(
            player['minute'], player['tfgm'], player['asst'], team['asst'],
            team['fgm'], player['fgm'], player['ftm'], player['tov'],
            player['fga'], player['fta'], player['drb'],
            player['orb'], player['st'], player['bs'], player['f'],
            league['ftm'], league['f'], league['fta'], league['pts'],
            league['fga'], league['orb'], league['tov'],
            league['orb'] + league['drb'], league['asst'], league['fgm']
        )

        # Culculate aper and league_aper  
        aper = (league_pace / team_pace) * uper
        league_aper += aper

        if player['team'] == tgt_team:
            aper_list.append(aper)
            per_name_list.append(player_name)

    # Adjust PER to a league scale of 15
    avr_league_aper = league_aper / num_players
    for aepr in aper_list:
        per = aepr * (15 / avr_league_aper)
        per_list.append(per)

    return per_list, per_name_list

def get_ffactor(tgt_team, conn):
    ffactor_list = []
    # 各チームの統計情報を格納するための辞書
    team_stats = {team: {} for team in tgt_team}

    # 両チームのデータを一度のクエリで取得
    query = f"""SELECT team, g, SUM(minute) as minute, SUM(pts) as pts,
            SUM(fgm) as fgm, SUM(fga) as fga, SUM(tfgm) as tfgm, SUM(ftm) as ftm,
            SUM(fta) as fta, SUM(orb) as orb, SUM(drb) as drb, SUM(asst) as asst,
            SUM(tov) as tov, SUM(st) as st, SUM(bs) as bs, SUM(f) as f
            FROM player_stats WHERE team IN (?, ?) GROUP BY team"""
    df = pd.read_sql(query, conn, params=tgt_team)

    # データフレームからチームごとの統計情報を抽出
    for index, row in df.iterrows():
        team_stats[row['team']] = row.to_dict()

    # 各種計算処理
    for team in tgt_team:
        stats = team_stats[team]
        opponent = tgt_team[0] if team != tgt_team[0] else tgt_team[1]
        opp_stats = team_stats[opponent]

        ppp = calculate_ppp(stats['pts'], stats['fga'], stats['fta'], stats['tov'])
        tposs = calculate_poss(stats['fga'], stats['fta'], stats['tov'])
        games = stats['minute'] / 5
        tposs_pg = tposs / stats['g']
        pts = ppp * tposs_pg
        efg_percent = calculate_efg_percent(stats['fgm'], stats['tfgm'], stats['fga'])
        orb_percent = calculate_or_percent(stats['orb'], opp_stats['drb'])
        tov_percent = calculate_to_percent(stats['tov'], stats['fga'], stats['fta'])
        ftr = stats['fta'] / stats['fga']
        ORtg = stats['pts'] / tposs * 100
        DRtg = opp_stats['pts'] / tposs * 100

        # 結果をsum_ffactorリストに追加
        ffactor_list += [team, str(round(pts,2)), str(round(ppp,2)), str(round(tposs_pg,2)), str(round(efg_percent,2)), str(round(orb_percent,2)), str(round(tov_percent,2)), str(round(ftr,2)), str(round(ORtg,2)), str(round(DRtg,2))]

    return ffactor_list

# Streamlitのセレクトボックスを使用してチームを選択
st.sidebar.title("B-League Stats")

team = ['北海道', '仙台', '秋田', '茨城', '宇都宮', '群馬', '千葉J', 'A東京',
        'SR渋谷', '川崎', '横浜BC', '富山', '信州', '三遠', '三河', 'FE名古屋',
        '名古屋D', '京都', '大阪', '島根', '広島', '佐賀', '長崎', '琉球']

selected_team = st.sidebar.selectbox('チームを選択', team)
selected_opponent_team = st.sidebar.selectbox('対戦チームを選択', team)

# ボタンが押されたら統計を計算
if st.sidebar.button('チームスタッツとPERを表示する'):
    if selected_team != selected_opponent_team:
        try:
            # データベース接続
            conn = sqlite3.connect("Bleague_stats/bleague_stat.db")
            per_list, per_name_list = get_per(selected_team, conn)
            match_up = [selected_team, selected_opponent_team]
            ffactor_list = get_ffactor(match_up, conn)
            index = ffactor_list.index(selected_opponent_team)
            ffactor_list_opp = ffactor_list[index:]
            ffactor_list = ffactor_list[:index]
            ffactor_name_list = ["Team", "PTS", "PPP", "POSS", "eFG%", "OR%", "TO%", "FTR", "ORtg", "DRtg"]
            
            # 選手の統計をデータフレームに整理
            ffactor_df = pd.DataFrame(
                {
                'Select Team': ffactor_list,
                'Stats': ffactor_name_list,
                'Opponent Team': ffactor_list_opp
                }    
            )
            per_df = pd.DataFrame(
                {
                'Player': per_name_list,
                'PER': per_list
                }
            )
            
            # Streamlitで表を表示
            st.table(ffactor_df)
            st.table(per_df)
        except sqlite3.Error as e:
            st.error(f"データベースエラー: {e}")
    else:
        st.write("同じチームを選択しています。別々のチームを指定してください。")
