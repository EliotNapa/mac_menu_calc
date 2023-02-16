import pulp
import sys
"""
#urbanhacksの次の問題を得プログラム。

限られた試験時間90分の中で、どの問題に取り組めば効率的よく最も高い点を取れるか。
問題を解くのには、必ず所要時間がかかって部分点は存在しない。
また、取り組んだ問題は必ず解けるものとする。
問題1  6点 所要時間12分
問題2 11点 所要時間26分
問題3 20点 所要時間48分
問題4 12点 所要時間28分
問題5 10点 所要時間25分
問題6 19点 所要時間45分
問題7 14点 所要時間31分
問題7  8点 所要時間15分

結果は次の通り

Result - Optimal solution found

Objective value:                40.00000000
Enumerated nodes:               0
Total iterations:               0
Time (CPU seconds):             0.15
Time (Wallclock seconds):       0.15

Option for printingOptions changed from normal to all
Total time (CPU seconds):       0.16   (Wallclock seconds):       0.16

[1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0]
min = 40.0, pts = 86.0

"""

limit_time = 90  # 問題の制限時間
points  = [ 6, 11, 20, 12, 10, 19, 14, 8]  # 問題の点数
minutes = [12, 26, 48, 28, 25, 45, 31, 15]  # 問題の所要時間

if len(points) != len(minutes):
    print("問題設定ミスってまっせ！")
    sys.exit(1)

# 問題を定義。pulp.LpMaximizeで最大化を指定
prob = pulp.LpProblem('examination', sense=pulp.LpMaximize)
# 変数の定義。問題を得かどうかを0,1のbinaryで表現
vars = [pulp.LpVariable('{}'.format(x), cat='Binary', lowBound=0, upBound=1) for x in range(len(points))]
prob += pulp.lpDot(points, vars)  # values(係数),vars(変数)の内積を目的関数として登録
prob += pulp.lpDot(minutes, vars) <= limit_time  # 試験の制限時間を制約条件として追加

# 実行
status = prob.solve()

print([x.value() for x in vars])


sum_pts = 0
sum_min = 0
for i in range(len(vars)):
    sum_pts += vars[i].value() * points[i]
    sum_min += vars[i].value() * minutes[i]

print("min = {0}, pts = {1}".format(sum_min, sum_pts))