import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import matplotlib.pyplot as plt
import japanize_matplotlib
from PIL import Image



st.set_page_config(page_title="相関分析", layout="wide")

st.title("相関分析")
st.caption("Created by Dit-Lab.(Daiki Ito)")
st.write("２つの変数から相関係数を表やヒートマップで出力し、相関関係の解釈の補助を行います。")
st.write("")

# 分析のイメージ
image = Image.open('correlation.png')
st.image(image)

# ファイルアップローダー
uploaded_file = st.file_uploader('ファイルをアップロードしてください (Excel or CSV)', type=['xlsx', 'csv'])

# デモデータを使うかどうかのチェックボックス
use_demo_data = st.checkbox('デモデータを使用')

# データフレームの作成
df = None
if use_demo_data:
    df = pd.read_excel('correlation_demo.xlsx', sheet_name=0)
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
    # 数値変数の抽出
    numerical_cols = df.select_dtypes(exclude=['object', 'category']).columns.tolist()

    # 数値変数の選択
    st.subheader("数値変数の選択")
    selected_cols = st.multiselect('数値変数を選択してください', numerical_cols)
    
    if len(selected_cols) < 2:
        st.write('少なくとも2つの変数を選択してください。')
    else:
        # 相関マトリックスの計算
        corr_matrix = df[selected_cols].corr()
        
        # 相関マトリックスの表示
        st.subheader('相関マトリックス')
        st.dataframe(corr_matrix)
        
        # ヒートマップの表示 (plotly.expressを使用)
        fig = px.imshow(corr_matrix, color_continuous_scale='rdbu', labels=dict(color="相関係数"))

        # アノテーションの追加 (相関係数の数値をセルに表示)
        annotations = []
        for i, row in enumerate(corr_matrix.values):
            for j, value in enumerate(row):
                annotations.append({
                    'x': j,
                    'y': i,
                    'xref': 'x',
                    'yref': 'y',
                    'text': f"{value:.2f}",
                    'showarrow': False,
                    'font': {
                        'color': 'black' if -0.5 < value < 0.5 else 'white'
                    }
                })

        fig.update_layout(title="相関係数のヒートマップ", annotations=annotations)
        st.plotly_chart(fig)
        
        # 相関の解釈
        st.subheader('解釈の補助')
        for i, col1 in enumerate(selected_cols):
            for j, col2 in enumerate(selected_cols):
                if i < j:
                    correlation = corr_matrix.loc[col1, col2]
                    description = f'【{col1}】と【{col2}】には'
                    if correlation > 0.7:
                        description += f'強い正の相関がある (r={correlation:.2f})'
                    elif correlation > 0.3:
                        description += f'中程度の正の相関がある (r={correlation:.2f})'
                    elif correlation > -0.3:
                        description += f'ほとんど相関がない (r={correlation:.2f})'
                    elif correlation > -0.7:
                        description += f'中程度の負の相関がある (r={correlation:.2f})'
                    else:
                        description += f'強い負の相関がある (r={correlation:.2f})'
                    st.write(description)



st.write('ご意見・ご要望は→', 'https://forms.gle/G5sMYm7dNpz2FQtU9', 'まで')
# Copyright
st.subheader('© 2022-2024 Dit-Lab.(Daiki Ito). All Rights Reserved.')
st.write("easyStat: Open Source for Ubiquitous Statistics")
st.write("Democratizing data, everywhere.")
st.write("")
st.subheader("In collaboration with our esteemed contributors:")
st.write("・Toshiyuki")
st.write("With heartfelt appreciation for their dedication and support.")
