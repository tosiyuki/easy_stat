import streamlit as st
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import japanize_matplotlib
import seaborn as sns
from PIL import Image

# フォントのプロパティを設定
font_prop = mpl.font_manager.FontProperties(fname="ipaexg.ttf")
    
# Matplotlibのデフォルトのフォントを変更
mpl.rcParams['font.family'] = font_prop.get_name()

st.set_page_config(page_title="相関分析", layout="wide")

st.title("相関分析")
st.caption("Created by Daiki Ito")
st.write("")
st.subheader("ブラウザで相関分析　→　表　→　解釈まで出力できるウェブアプリです。")
st.write("iPad等でも分析を行うことができます")

st.write("")

st.write("また、Excelファイルに不備があるとエラーが出ます")
st.write('<span style="color:blue">デフォルトでデモ用データの分析ができます。</span>',
         unsafe_allow_html=True)
st.write(
    '<span style="color:blue">ファイルをアップせずに「データフレームの表示」ボタンを押すと　'
    'デモ用のデータを確認できます。</span>',
    unsafe_allow_html=True)
st.write('<span style="color:red">欠損値を含むレコード（行）は自動で削除されます。</span>',
         unsafe_allow_html=True)

# Excelデータの例
image = Image.open('correlation.png')
st.image(image)

# デモ用ファイル
df = pd.read_excel('correlation_demo.xlsx', sheet_name=0)

# xlsxまたはcsvファイルのアップロード
upload_files = st.file_uploader("ファイルアップロード", type=['xlsx', 'csv'])

# xlsxまたはcsvファイルの読み込み → データフレームにセット
if upload_files:
    # dfを初期化
    df.drop(range(len(df)))
    # xlsxまたはcsvファイルの読み込み → データフレームにセット
    if upload_files.type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
        df = pd.read_excel(upload_files, sheet_name=0)
    elif upload_files.type == 'text/csv':
        df = pd.read_csv(upload_files)
    # 欠損値を含むレコードを削除
    df.dropna(how='any', inplace=True)

# データフレーム表示ボタン
if st.checkbox('データフレームの表示（クリックで開きます）'):
    st.dataframe(df, width=0)

# 変数選択フォーム
with st.form(key='variable_form'):
    st.subheader("分析に使用する変数の選択")

    # 変数のセット
    a = df.columns.tolist()

    # 複数選択
    Variable = st.multiselect('変数を選択（複数選択可）', a)

    st.write(
        '<span style="color:blue">【注意】変数に数値以外のものがある場合、分析できません</span>',
        unsafe_allow_html=True)

    aRange = len(Variable)

    # 確認ボタンの表示
    CHECK_btn = st.form_submit_button('確認')

# 分析前の確認フォーム
with st.form(key='check_form'):
    if CHECK_btn:
        st.subheader('【分析前の確認】')

        n = 0
        for ViewCheck in range(aRange):
            st.write(
                f'● 【'f'{(Variable[n])}'f'】')
            n += 1
        st.write('    ' + 'これらの変数間に相関関係があるか分析します。')

    # 分析実行ボタンの表示
    ANALYZE_btn = st.form_submit_button('分析実行')

# 分析結果表示フォーム
with st.form(key='analyze_form'):
    if ANALYZE_btn:
        st.subheader('【分析結果】')

        # 各値の初期化
        n = 1
        m = 0
        # リストの名前を取得
        VariableList = []
        for ListAppend in range(aRange):
            VariableList.append(
                f'【'f'{(Variable[m])}'f'】')
            m += 1

        # 選択した変数から作業用データフレームのセット
        dfAv = df[Variable]

        st.write('【相関分析】')
        st.dataframe(dfAv.corr(), width=0)

        # Adding a heatmap of correlation
        st.write('【相関行列のヒートマップ】')
        fig, ax = plt.subplots()
        sns.heatmap(dfAv.corr(), annot=True, cmap='coolwarm', ax=ax)
        st.pyplot(fig)

        if st.checkbox('【相関係数( r )の判定】'):
            st.write('0.7 ≦ r ≦ 1.0 ・・・強い正の相関')
            st.write('0.4 ≦ r ≦ 0.7 ・・・正の相関')
            st.write('0.2 ≦ r ≦ 0.4 ・・・弱い正の相関')
            st.write('-0.2 ≦ r ≦ 0.2 ・・・相関なし')
            st.write('-0.4 ≦ r ≦ -0.2 ・・・弱い負の相関')
            st.write('-0.7 ≦ r ≦ -0.4 ・・・負の相関')
            st.write('-1.0 ≦ r ≦ -0.7 ・・・強い負の相関')

        st.write('')
        st.write('【分析結果の解釈】')
        for v1 in range(aRange):
            for v2 in range(aRange):
                if v1 != v2:
                    dn = Variable[v2]
                    r = round(dfAv.corr().iat[v1, v2], 2)  # rを小数点第2位まで表示
                    if dfAv.corr().iat[v1, v2] >= 0.7:
                        st.markdown(
                            f'<p style="color:red;">'
                            f'【{Variable[v1]}】と【{dn}】の間には「強い正の相関」がある（ r = {r} )'
                            f'</p>',
                            unsafe_allow_html=True)
                    elif dfAv.corr().iat[v1, v2] >= 0.4:
                        st.markdown(
                            f'<p style="color:orange;">'
                            f'【{Variable[v1]}】と【{dn}】の間には「正の相関」がある（ r = {r} )'
                            f'</p>',
                            unsafe_allow_html=True)
                    elif dfAv.corr().iat[v1, v2] >= 0.2:
                        st.markdown(
                            f'<p style="color:yellow;">'
                            f'【{Variable[v1]}】と【{dn}】の間には「弱い正の相関」がある（ r = {r} )'
                            f'</p>',
                            unsafe_allow_html=True)
                    elif dfAv.corr().iat[v1, v2] >= -0.2:
                        st.write(
                            f'【{Variable[v1]}】と【{dn}】の間には「相関がない」（ r = {r} )')
                    elif dfAv.corr().iat[v1, v2] >= -0.4:
                        st.markdown(
                            f'<p style="color:yellow;">'
                            f'【{Variable[v1]}】と【{dn}】の間には「弱い負の相関」がある（ r = {r} )'
                            f'</p>',
                            unsafe_allow_html=True)
                    elif dfAv.corr().iat[v1, v2] >= -0.7:
                        st.markdown(
                            f'<p style="color:orange;">'
                            f'【{Variable[v1]}】と【{dn}】の間には「負の相関」がある（ r = {r} )'
                            f'</p>',
                            unsafe_allow_html=True)
                    elif dfAv.corr().iat[v1, v2] >= -1.0:
                        st.markdown(
                            f'<p style="color:red;">'
                            f'【{Variable[v1]}】と【{dn}】の間には「強い負の相関」がある（ r = {r} )'
                            f'</p>',
                            unsafe_allow_html=True)

    ANALYZE_btn = st.form_submit_button('OK')

st.write('ご意見・ご要望は→', 'https://forms.gle/G5sMYm7dNpz2FQtU9',
             'まで')
st.write('© 2022-2023 Daiki Ito. All Rights Reserved.')
