# -*- coding: utf-8 -*-
"""
マクドナルドサイトより成分表を取得し
必要栄養を満たすメニューを計算
"""

import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
from pulp import *

def main():
	"""
		マクドナルドサイトの成分表の並び順に依存
		種類			  	kind
		0名称			    name
		1製品重量 g/個	    weight
		2エネルギー kcal    kcal
		3たんぱく質 g	    protein
		4脂質 g			    fat
		5炭水化物 g		    carb
		6ナトリウム mg	    natrium
		7カリウム mg	    kalium
		8カルシウム mg	    calicium
		9リン mg		    phos
		10鉄 mg			    iron		
		11ビタミンA μg	    vitamin_a
		12ビタミンB1 mg	    vitamin_b1
		13ビタミンB2 mg	    vitamin_b2
		14ナイアシン mg	    niacin
		15ビタミンC mg	    vitamin_c
		16コレステロール mg  chol
		17食物繊維 g		 fiber
		18食塩相当量 g		 solt
	"""

	#成分表のカラムを指定
	df = pd.DataFrame([], columns=[
			'kind',
			'name',
			'weight',
			'kcal',
			'protein',
			'fat',
			'carb',
			'natrium',
			'kalium',
			'calicium',
			'phos',
			'iron',
			'vitamin_a',
			'vitamin_b1',
			'vitamin_b2',
			'niacin',
			'vitamin_c',
			'chol',
			'fiber',
			'solt'
		])
	#マクドナルド公式サイトの成分表ページURL
	url = 'https://www.mcdonalds.co.jp/quality/allergy_Nutrition/nutrient/'
	res = requests.get(url)
	soup = BeautifulSoup(res.text, "html.parser")
	
	items = soup.find_all('tr')

	#DOMよりDataFrameを作成
	for item in items:
		if item.has_attr('data-kind'):
			tds = item.find_all('td')

			addRow = pd.Series([
				item.get('data-kind'),
				list(list(list(tds)[0].children)[1].contents)[0],
                *[list(list(tds)[x].contents)[0] for x in range(1,19)]
				], index=df.columns)

			df = df.append(addRow, ignore_index=True)


	# 表の-を0に置換
	df.replace('-','0',True)
	#変換後の表をCSV出力する場合
	#df.to_csv('mac2.csv')

	#条件は最小
	prob = pulp.LpProblem(name="mac", sense=LpMinimize)
	#DataFrameのインデックス番号よりLpVariableの辞書を作成
	#日本語名比較のコストを削減
	x = pulp.LpVariable.dicts('x', df.index.values.tolist(), lowBound = 0, upBound = 999, cat="Integer")


	#重量を最小にするほうが条件としては適正に思える
	prob += pulp.lpSum([x[i] * float(df[i:i+1]['weight'].values[0]) for i in range(len(df))])

	#各成分の必要最小値を設定
	prob += pulp.lpSum([x[i] * float(df[i:i+1]['protein'].values[0]) for i in range(len(df))]) >= 39
	prob += pulp.lpSum([x[i] * float(df[i:i+1]['fat'].values[0]) for i in range(len(df))]) >= 75
	prob += pulp.lpSum([x[i] * float(df[i:i+1]['carb'].values[0]) for i in range(len(df))]) >= 675
	prob += pulp.lpSum([x[i] * float(df[i:i+1]['natrium'].values[0]) for i in range(len(df))]) >= 5000
	prob += pulp.lpSum([x[i] * float(df[i:i+1]['kalium'].values[0]) for i in range(len(df))]) >= 3000
	prob += pulp.lpSum([x[i] * float(df[i:i+1]['calicium'].values[0]) for i in range(len(df))]) >= 738
	prob += pulp.lpSum([x[i] * float(df[i:i+1]['phos'].values[0]) for i in range(len(df))]) >= 600
	prob += pulp.lpSum([x[i] * float(df[i:i+1]['iron'].values[0]) for i in range(len(df))]) >= 6.3
	prob += pulp.lpSum([x[i] * float(df[i:i+1]['vitamin_a'].values[0]) for i in range(len(df))]) >= 625
	prob += pulp.lpSum([x[i] * float(df[i:i+1]['vitamin_b1'].values[0]) for i in range(len(df))]) >= 1.4
	prob += pulp.lpSum([x[i] * float(df[i:i+1]['vitamin_b2'].values[0]) for i in range(len(df))]) >= 1.6
	prob += pulp.lpSum([x[i] * float(df[i:i+1]['niacin'].values[0]) for i in range(len(df))]) >= 15
	prob += pulp.lpSum([x[i] * float(df[i:i+1]['vitamin_c'].values[0]) for i in range(len(df))]) >= 100
	prob += pulp.lpSum([x[i] * float(df[i:i+1]['chol'].values[0]) for i in range(len(df))]) >= 0
	prob += pulp.lpSum([x[i] * float(df[i:i+1]['fiber'].values[0]) for i in range(len(df))]) >= 21
	prob += pulp.lpSum([x[i] * float(df[i:i+1]['solt'].values[0]) for i in range(len(df))]) <= 5

	#実行
	prob.solve()

	#結果表示
	print(LpStatus[prob.status])

	print("Result")
	#商品と個数を表示
	for i in range(len(df)):
		if x[i].value() is not None:
			if x[i].value() > 0:
				print("{0}:{1}".format(df[i:i+1]['name'].values[0], int(x[i].value())))

	#成分ごとの量を表示
	for col_name in df.columns:
		try:
			float(df[0:1][col_name].values[0])
			print('{0} = {1}'.format(col_name,
			pulp.lpSum([x[i].value() * float(df[i:i+1][col_name].values[0]) for i in range(len(df))])))
		except:
			pass

if __name__ == '__main__':
	main()
