# -------------------------------------------------------------------------------
# Name:        Hit & Blow CUI
# Author:      Wabisuke
# Created:     24/08/2021
# Copyright:   (c) Wabisuke 2021
# -------------------------------------------------------------------------------
import random

duplicate = True  # ランダムで数字を取り出すとき数字重複とする場合はTrue
nbr_list = ['1', '2', '3', '4', '5', '6']  # ランダムで選出する数字の範囲
n = 4  # ランダムで選出する桁数
ans = []  # 答えを保持するリストの初期化
life = 8  # 何回解答できるか
total_value = 0  # 答えをリストから数値に変換する際の変数初期化

if duplicate:  # 数字重複の場合
    for i in range(n):
        ans.append(random.choice(nbr_list))  # ランダムに重複する可能性のある数字を選択
else:  # 数字重複しない場合
    ans = random.sample(nbr_list, n)  # ランダムに重複しない数字を選択

for i in range(life):  # 解答権回数
    hit = 0  # Hit数
    blow = 0  # Blow数
    ans_work = []
    remove_key = []

    i_print = i + 1  # 何度目の挑戦か表示
    print('------------------------------')
    print(str(i_print) + '/' + str(life) + '回目')
    if duplicate:
        inp = (input(nbr_list[0] + 'から' + nbr_list[-1] + 'までの数字で'
                     + str(n) + '桁入力してください(答えには同じ数字が2回以上使われる可能性があります)：'))
    else:
        inp = (input(nbr_list[0] + 'から' + nbr_list[-1] + 'までの数字で'
                     + str(n) + '桁入力してください(答えは必ず異なる数字で構成されます)：'))
    if not inp.isdecimal():
        print('入力した値の一部が数字でないため不正です')
        pass
    else:
        inp = list(inp)  # strのinpをリスト化する
        if len(inp) != n:  # 入力された値の桁数と答えの桁数の比較
            print('入力した値の桁数が異なるため不正です')
            pass
        else:
            ans_work = ans.copy()  # 答えを処理用変数にコピーする
            for j in range(len(inp)):  # Hit数を求める
                if inp[j] == ans_work[j]:
                    hit += 1
                    remove_key.append(j)
            remove_key = sorted(remove_key, reverse=True)  # Hitした値のList番号を昇順ソートする(Listの後ろから消したいため)
            for j in range(len(remove_key)):
                inp.pop(remove_key[j])  # 入力値からHitした数字を取り除く
                ans_work.pop(remove_key[j])  # 答えからHitした数字を取り除く
            remove_key = []
            for j in range(len(inp)):  # Blow数を求める
                for k in range(len(ans_work)):  # 入力を基準に答えと一桁ずつ比較
                    if inp[j] == ans_work[k]:  # 異なる桁に同じ値が存在する
                        if k not in remove_key:  # すでにBlowと判断した答えの桁は再度判定しない
                            blow += 1
                            remove_key.append(k)
                            break  # Blowが見つかったら、次の入力桁を見る(答えに同じ値が複数桁に存在するときの対応)
                        else:
                            pass
            remove_key = []
            print('Hit ：' + str(hit))
            print('Blow：' + str(blow))
            if hit == n:
                print('------------------------------')
                print(str(i_print) + '回で正解です！お見事です！')
                break
            elif i_print == life:
                print('------------------------------')
                print('残念でした。正解は' + ''.join(map(str, ans)) + 'でした')
