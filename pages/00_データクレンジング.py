import streamlit as st
import numpy as np
import pandas as pd
import io






st.set_page_config(page_title="データクレンジング", layout="wide")

st.title("データクレンジング")
st.caption("Created by Dit-Lab.(Daiki Ito)")
st.write("データセットに対して、欠損値処理や外れ値の処理などができます")
st.write("")

uploaded_file = st.file_uploader("CSVまたはExcelファイルを選択してください", type=["csv", "xlsx"])

if uploaded_file is not None:
    if uploaded_file.type == 'text/csv':
        data = pd.read_csv(uploaded_file)
    else:
        data = pd.read_excel(uploaded_file)
    
    st.subheader('元のデータ')
    st.write(data)

    processed_data = data

    remove_outliers_option = st.checkbox('外れ値の削除')
    data_cleansing_option = st.checkbox('欠損値の削除')
    remove_empty_columns_option = st.checkbox('値が入っていないカラム（列）の削除')

    if st.button('データ処理'):

        if remove_outliers_option:
            num_cols = processed_data.select_dtypes(include=np.number).columns
            if not num_cols.empty:
                Q1 = processed_data[num_cols].quantile(0.25)
                Q3 = processed_data[num_cols].quantile(0.75)
                IQR = Q3 - Q1
                outlier_condition = ((processed_data[num_cols] < (Q1 - 1.5 * IQR)) | (processed_data[num_cols] > (Q3 + 1.5 * IQR)))
                processed_data = processed_data[~outlier_condition.any(axis=1)]
            else:
                st.warning('外れ値を削除する数値列がありません')

        if data_cleansing_option:
            processed_data = processed_data.dropna()
            processed_data = processed_data.applymap(lambda x: x.strip() if isinstance(x, str) else x)

        if remove_empty_columns_option:
            empty_columns = processed_data.columns[data.isna().all()].tolist()
            processed_data = processed_data.dropna(axis=1, how='all')

        st.subheader('処理済みのデータ')
        st.write(processed_data)

        file_format = st.selectbox('ダウンロードするファイル形式を選択', ['Excel', 'CSV'])

        # アップロードされたファイル名から拡張子を削除し、'_processed'を追加して新しいファイル名を作成
        download_file_name = f"{uploaded_file.name.rsplit('.', 1)[0]}_processed"
        
        if file_format == 'CSV':
            csv_data = processed_data.to_csv(index=False)
            st.download_button(
                label="処理済みデータをダウンロード",
                data=csv_data,
                file_name=f'{download_file_name}.csv',  # 更新されたファイル名
                mime='text/csv'
            )
        else:
            excel_io = io.BytesIO()  # BytesIOオブジェクトを作成
            processed_data.to_excel(excel_io, index=False)  # ExcelデータをBytesIOオブジェクトに書き込む
            excel_data = excel_io.getvalue()  # BytesIOオブジェクトからバイトデータを取得
            st.download_button(
                label="処理済みデータをダウンロード",
                data=excel_data,
                file_name=f'{download_file_name}.xlsx',  # 更新されたファイル名
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
    
st.write('ご意見・ご要望は→', 'https://forms.gle/G5sMYm7dNpz2FQtU9', 'まで')
# Copyright
st.subheader('© 2022-2024 Dit-Lab.(Daiki Ito). All Rights Reserved.')
st.write("easyStat: Open Source for Ubiquitous Statistics")
st.write("Democratizing data, everywhere.")
st.write("")
st.subheader("In collaboration with our esteemed contributors:")
st.write("・Toshiyuki")
st.write("With heartfelt appreciation for their dedication and support.")

