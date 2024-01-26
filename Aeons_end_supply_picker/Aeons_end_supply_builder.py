import sqlite3
import pandas as pd
import streamlit as st
import random

def check_condition(pattern, applyset, mode, i):
    cmd = ''
    select_type = False

    cmd = 'SELECT name, card_set FROM cardlist WHERE type = ? AND cost '

    if pd.notna(pattern.cost_2[i]):
        select_type = True
        cmd += 'BETWEEN ? AND ? '
    elif pattern.condition[i] == '以下':
        cmd += '<= ? '
    elif pattern.condition[i] == '以上':
        cmd += '>= ? '
    elif pattern.condition[i] == '等しい':
        cmd += '= ? '

    if applyset != 'all':
        cmd += 'AND wave = ? '

    if mode == 1:
        cmd += 'AND destroy_card = ?'
    elif mode == 2:
        cmd += 'AND focus_breach = ?'
    elif mode == 3:
        cmd += 'AND gain_charge = ?'
    elif mode == 4:
        cmd += 'AND gain_gravehold_life = ?'
    elif mode == 5:
        cmd += 'AND gain_life = ?'

    cmd += 'ORDER BY RANDOM() LIMIT 1'
    return select_type, cmd

def main():
    st.title('イーオンズ・エンド - サプライ自動生成')

    conn = sqlite3.connect('Aeons_end.db')
    cur = conn.cursor()

    # サプライ検索条件の選択
    applyset = st.selectbox('検索するカードセット：', ('all', '1st wave', '2nd wave'))

    # チェックボックス
    destroy_card = st.checkbox('カード破棄')
    focus_breach = st.checkbox('破孔強化')
    gain_charge = st.checkbox('チャージを得る')
    gain_gravehold_life = st.checkbox('グレイヴホールド回復')
    gain_life = st.checkbox('体力回復')

    if st.button('サプライ選択'):
        supply_card, pattern_number = generate_supply_card(conn, applyset, destroy_card, focus_breach, gain_charge, gain_gravehold_life, gain_life)
        display_supply_card(supply_card, pattern_number)

    conn.close()

def generate_supply_card(conn, applyset, destroy_card, focus_breach, gain_charge, gain_gravehold_life, gain_life):
    supply_card = []
    option_index = []
    option_list = []
    keys = []
    option = []

    keys.append(random.randint(1, 6))
    pattern = pd.read_sql_query('SELECT * FROM supply WHERE pattern == ?', conn, params=keys)
    
    pattern_number = keys[0]  # パターン番号を取得

    option.append(destroy_card)
    option.append(focus_breach)
    option.append(gain_charge)
    option.append(gain_gravehold_life)
    option.append(gain_life)

    for i in range(len(pattern)):
        mode = 0
        result = check_condition(pattern, applyset, mode, i)
        keys = [pattern.type[i], int(pattern.cost_1[i])]
        if result[0] == True:
            keys.append(int(pattern.cost_2[i]))

        if applyset != 'all':
            keys.append(applyset)

        cardselect = pd.read_sql_query(result[1], conn, params=keys)

        if len(cardselect) != 0:
            while (cardselect.name[0] + '： ' + cardselect.card_set[0]) in supply_card:
                cardselect = pd.read_sql_query(result[1], conn, params=keys)
            supply_card.append(cardselect.name[0] + '： ' + cardselect.card_set[0])
        else:
            st.error('該当するカードが存在しません。\nサプライ選択ボタンを押してください。')
            break

    for i in range(len(option)):
        if option[i] == True:
            option_index = []
            option_list = []
            mode = i + 1
            for j in range(len(pattern)):
                result = check_condition(pattern, applyset, mode, j)
                keys = [pattern.type[j], int(pattern.cost_1[j])]
                if result[0] == True:
                    keys.append(int(pattern.cost_2[j]))
                if applyset != 'all':
                    keys.append(applyset)
                keys.append('applicable')
                cardselect = pd.read_sql_query(result[1], conn, params=keys)
                if len(cardselect) != 0:
                    option_index.append(j)
                    option_list.append(cardselect.name[0] + '： ' + cardselect.card_set[0])
                else:
                    option_list.append('None')
            if len(option_index) != 0:
                update_card = random.choice(option_index)
                if option_list[update_card] not in supply_card:
                    supply_card[update_card] = option_list[update_card]

    return supply_card, pattern_number

def display_supply_card(supply_card, pattern_number):
    if supply_card:
        st.header('サプライ構成チャート：' + str(pattern_number))
        for i, card in enumerate(supply_card):
            st.write(f'{i + 1}. {card}')
    else:
        st.warning('選択されたサプライカードはありません。')

if __name__ == '__main__':
    main()
