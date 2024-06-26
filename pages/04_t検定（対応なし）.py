import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
import math
from statistics import median, variance
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import japanize_matplotlib
from PIL import Image

st.set_page_config(page_title="t検定(対応なし)", layout="wide")

st.title("t検定(対応なし)")
st.caption("Created by Dit-Lab.(Daiki Ito)")
st.write("変数の選択　→　t検定　→　表作成　→　解釈の補助を行います")
st.write("")

# 分析のイメージ
image = Image.open('ttest.png')
st.image(image)

# ファイルアップローダー
uploaded_file = st.file_uploader('ファイルをアップロードしてください (Excel or CSV)', type=['xlsx', 'csv'])

# デモデータを使うかどうかのチェックボックス
use_demo_data = st.checkbox('デモデータを使用')

# データフレームの作成
df = None
if use_demo_data:
    df = pd.read_excel('ttest_demo.xlsx', sheet_name=0)
    st.write(df.head())
else:
    if uploaded_file is not None:
        if uploaded_file.type == 'text/csv':
            df = pd.read_csv(uploaded_file)
            st.write(df.head())
        else:
            df = pd.read_excel(uploaded_file)
            st.write(df.head())

if df is not None:
    # カテゴリ変数の抽出
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    # 数値変数の抽出
    numerical_cols = df.select_dtypes(exclude=['object', 'category']).columns.tolist()

    # カテゴリ変数の選択
    st.subheader("カテゴリ変数の選択")
    cat_var = st.multiselect('カテゴリ変数（独立変数）を選択してください', categorical_cols,max_selections=1)

    # 数値変数の選択
    st.subheader("数値変数の選択")
    num_vars = st.multiselect('数値変数（従属変数）を選択してください', numerical_cols)

    # エラー処理
    if not cat_var:
        st.error("カテゴリ変数を選択してください。")
    elif not num_vars:
        st.error("数値変数を選択してください。")
    elif len(df[cat_var].iloc[:, 0].unique()) != 2:
        st.error("独立変数が2群になっていないため、分析を実行できません")
    else:
        st.success("分析可能な変数を選択しました。分析を実行します。")

        # 独立変数から重複のないデータを抽出し、リストに変換
        xcat_var_d = df[cat_var].iloc[:, 0].unique().tolist()
        st.subheader('【分析前の確認】')
        cat_var_str = str(cat_var)
        st.write(f'{(cat_var_str)}（{xcat_var_d[0]}・{xcat_var_d[1]}）によって、')

        for num_var in num_vars:
            st.write(f'● {num_var}')

        st.write("これらの数値変数に有意な差が生まれるか検定します。")

        # グラフタイトルを表示するチェックボックス
        show_graph_title = st.checkbox('グラフタイトルを表示する', value=True)  # デフォルトでチェックされている

        # t検定の実行
        if st.button('t検定の実行'):
            st.subheader('【分析結果】')
            st.write('【要約統計量】')

            # 数値変数の要素の数を取得
            num_range = len(num_vars)

            # 各値の初期化
            n = 1
            summaryList = [num_vars]
            summaryColumns = ["有効N", "平均値", "中央値", "標準偏差", "分散",
                            "最小値", "最大値"]

            # 目的変数、従属変数から作業用データフレームのセット
            df00_list = cat_var + num_vars
            df00 = df[df00_list]

            # サマリ(df0)用のデータフレームのセット
            df0 = pd.DataFrame(index=summaryList, columns=summaryColumns)

            # サマリ(df0)用のデータフレームに平均値と標準偏差を追加
            for summary in range(num_range):
                # 列データの取得（nは従属変数の配列番号）
                y = df00.iloc[:, n]

                # 従属変数の列データの計算処理
                df0.at[df00.columns[n], '有効N'] = len(y)
                df0.at[df00.columns[n], '平均値'] = y.mean()
                df0.at[df00.columns[n], '中央値'] = median(y)
                df0.at[df00.columns[n], '標準偏差'] = y.std()
                df0.at[df00.columns[n], '分散'] = variance(y)
                df0.at[df00.columns[n], '最小値'] = y.min()
                df0.at[df00.columns[n], '最大値'] = y.max()
                n += 1

            # 要約統計量（サマリ）のデータフレームを表示
            st.write(df0.style.format("{:.2f}"))

            st.write('【平均値の差の検定（対応なし）】')
            groups = df[cat_var].iloc[:, 0].unique().tolist()

            # 結果を保存するデータフレームの初期化
            columns = ['全体M', '全体S.D', f'{groups[0]}M', f'{groups[0]}S.D',
                    f'{groups[1]}M', f'{groups[1]}S.D', 'df', 't', 'p', 'sign', 'd']
            df_results = pd.DataFrame(columns=columns)

            for var in num_vars:
                series = df[var]
                group0_data = df[df[cat_var[0]] == groups[0]][var]
                group1_data = df[df[cat_var[0]] == groups[1]][var]

                ttest_result = stats.ttest_ind(group0_data, group1_data, equal_var=False)
                overall_mean = series.mean()
                overall_std = series.std()
                g0_mean = group0_data.mean()
                g0_std = group0_data.std()
                g1_mean = group1_data.mean()
                g1_std = group1_data.std()
                effect_size = abs(g0_mean - g1_mean) / overall_std

                if ttest_result.pvalue < 0.01:
                    significance = '**'
                elif ttest_result.pvalue < 0.05:
                    significance = '*'
                elif ttest_result.pvalue < 0.1:
                    significance = '†'
                else:
                    significance = 'n.s.'

                results_row = {
                    '全体M': overall_mean,
                    '全体S.D': overall_std,
                    f'{groups[0]}M': g0_mean,
                    f'{groups[0]}S.D': g0_std,
                    f'{groups[1]}M': g1_mean,
                    f'{groups[1]}S.D': g1_std,
                    'df': len(series) - 1,
                    't': abs(ttest_result.statistic),
                    'p': ttest_result.pvalue,
                    'sign': significance,
                    'd': effect_size
                }

                df_results.loc[var] = results_row

            # 結果の表示
            # 数値型の列だけを選択
            numeric_columns = df_results.select_dtypes(include=['float64', 'int64']).columns
            # 選択した列にのみ、スタイルを適用
            styled_df = df_results.style.format({col: "{:.2f}" for col in numeric_columns})
            st.write(styled_df)

            # sign_captionを初期化
            sign_caption = ''

            # 各記号に対するチェックを実行
            if df_results['sign'].str.contains('\*\*').any():
                sign_caption += 'p<0.01** '
            if df_results['sign'].str.contains('\*').any():
                sign_caption += 'p<0.05* '
            if df_results['sign'].str.contains('†').any():
                sign_caption += 'p<0.1† '
            
            st.caption(sign_caption)


            # サンプルサイズの表示
            st.write('【サンプルサイズ】')
            st.write(f'全体N ＝ {len(df)}')
            st.write(f'● {groups[0]}： {len(group0_data)}')
            st.write(f'● {groups[1]}： {len(group1_data)}')

            st.subheader('【解釈の補助】')

            for index, row in df_results.iterrows():
                comparison = " < " if row[f'{groups[0]}M'] < row[f'{groups[1]}M'] else " > "
                sign = row['sign']
                if sign in ['**', '*']:
                    significance = "有意な差が生まれる"
                elif sign == '†':
                    significance = "有意な差が生まれる傾向にある"
                else:
                    significance = "有意な差が生まれない"
                p_value = row['p']
                st.write(f'{cat_var_str}によって、{index}には{significance}（{xcat_var_d[0]}{comparison}{xcat_var_d[1]}）（p= {p_value:.2f}）')


            st.subheader('【可視化】')
            # グラフの描画
            font_path = 'ipaexg.ttf'
            plt.rcParams['font.family'] = 'IPAexGothic'

            # ブラケット付きの棒グラフを出力する機能の更新
            def add_bracket(ax, x1, x2, y, text):
                bracket_length = 4  # ブラケットの両端の縦棒の長さを固定
                ax.add_line(Line2D([x1, x1], [y, y + bracket_length], color='black', lw=1))
                ax.add_line(Line2D([x2, x2], [y, y + bracket_length], color='black', lw=1))
                ax.add_line(Line2D([x1, x2], [y + bracket_length, y + bracket_length], color='black', lw=1))
                ax.text((x1 + x2) / 2, y + bracket_length + 2, text, ha='center', va='bottom')

            # グラフ描画部分の更新
            for var in num_vars:
                data = pd.DataFrame({
                    '群': groups,
                    '平均値': [df_results.at[var, f'{groups[0]}M'], df_results.at[var, f'{groups[1]}M']],
                    '誤差': [df_results.at[var, f'{groups[0]}S.D'], df_results.at[var, f'{groups[1]}S.D']]
                })

                fig, ax = plt.subplots(figsize=(8, 6))
                bars = ax.bar(x=data['群'], height=data['平均値'], yerr=data['誤差'], capsize=5)
                if show_graph_title:
                    ax.set_title(f'平均値の比較： {var}')
                p_value = df_results.at[var, 'p']
                significance_text = "p < 0.01 **" if p_value < 0.01 else "p < 0.05 *" if p_value < 0.05 else "p < 0.1 †" if p_value < 0.1 else "n.s."
                bracket_length = 4
                bracket_height = max(data['平均値']) + max(data['誤差']) * 1.1 + bracket_length
                ax.set_ylim([0, bracket_height * 1.4])
                add_bracket(ax, 0, 1, bracket_height, significance_text)
                st.pyplot(fig)
                
                

st.write('ご意見・ご要望は→', 'https://forms.gle/G5sMYm7dNpz2FQtU9', 'まで')
# Copyright
st.subheader('© 2022-2024 Dit-Lab.(Daiki Ito). All Rights Reserved.')
st.write("easyStat: Open Source for Ubiquitous Statistics")
st.write("Democratizing data, everywhere.")
st.write("")
st.subheader("In collaboration with our esteemed contributors:")
st.write("・Toshiyuki")
st.write("With heartfelt appreciation for their dedication and support.")