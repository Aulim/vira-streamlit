import streamlit as st
import pandas as pd
import math

st.markdown("<a name='top'></a>", unsafe_allow_html=True)

st.title("Viraindo Laptop Price Explorer")
st.markdown('''
Data didapatkan dari [laman harga notebook Viraindo](http://viraindo.com/notebook.html).
Data diupdate harian.
''')

def show_dataframe_paginated(df, page: int, show_row: int):
    start_idx = (page - 1) * show_row
    end_idx = (page * show_row)
    # 
    # st.session_state.prev_disabled = True if page == 1 else False
    # st.session_state.next_disabled = False if page < page_limit else True
    return df.iloc[start_idx:end_idx]

def filter_name(df, filters):
    filtered_df = df.copy()
    for filter in filters:
        filtered_df = filtered_df[filtered_df['Name'].str.contains(filter) == True]
    return filtered_df.reset_index(drop=True)

def filter_price(df, min, max):
    filtered_df = df.copy()
    filtered_df = filtered_df[filtered_df['Price'] >= min]
    filtered_df = filtered_df[filtered_df['Price'] <= max]
    return filtered_df.reset_index(drop=True)

@st.experimental_memo
def get_data():
    return pd.read_json("./vira_data_20220603.json").drop(columns=['Id'])

df = get_data()
#TODO: Set max price by session state

if 'page_current' not in st.session_state:
    st.session_state.page_current = 1

if 'filter_params' in st.session_state and len(st.session_state.filter_params) > 0:
    df = filter_name(df, st.session_state.filter_params)
    filter_txts, pop_filter, clear_filter = st.columns([18,3,3])
    filter_txts.write(f"Anda mencari {', '.join(st.session_state.filter_params)}")
    pop_filter_button = pop_filter.button(
        "Hapus terbaru", 
        disabled=len(st.session_state.filter_params) < 1)
    clear_filter_button = clear_filter.button(
        "Hapus semua"
    )

    if pop_filter_button:
        st.session_state.filter_params.pop()
        st.experimental_rerun()

    if clear_filter_button:
        st.session_state.filter_params.clear()
        st.experimental_rerun()
else:
    st.session_state.filter_params = []

if 'min_price' in st.session_state and 'max_price' in st.session_state:
    df = filter_price(df, st.session_state.min_price, st.session_state.max_price)
    st.write(f'Mencari produk dengan harga antara {st.session_state.min_price} sampai {st.session_state.max_price}')

with st.form("Filter form", True):
    filter = st.text_input("Cari produk yang mengandung kata:")
    min, max = st.columns([1,1])
    #TODO: Fix the max price
    min_price = min.number_input("Harga minimum", 0.0, 9999999999.0, 0.0)
    max_price = max.number_input("Harga maksimum", 0.0, 9999999999.0, df['Price'].max())
    filtered = st.form_submit_button("Cari")

    if filtered:
        if filter:
            st.session_state.filter_params.append(filter)
        st.session_state.min_price = min_price
        st.session_state.max_price = max_price
        st.session_state.page_current = 1
        st.experimental_rerun()

show_rows = 20
page_limit = math.ceil(len(df) / show_rows)

if len(df) > 0:
    st.write(f"Tampilkan halaman {st.session_state.page_current} dari total {len(df)} produk")

    prev, _, next = st.columns([1,20,1])

    prev_button = prev.button("<", disabled=st.session_state.page_current <= 1)
    next_button = next.button("\\>", disabled=st.session_state.page_current >= page_limit)

    if prev_button:
        st.session_state.page_current-=1
        st.experimental_rerun()
        
    if next_button:
        st.session_state.page_current+=1
        st.experimental_rerun()

    st.table(show_dataframe_paginated(df, st.session_state.page_current, show_rows))

    st.markdown("[Back to top](#top)")
else:
    st.write("Tidak ditemukan produk yang mengandung kata: ", ', '.join(st.session_state.filter_params))

