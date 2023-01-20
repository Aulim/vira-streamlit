import streamlit as st
import pandas as pd
import math
import datetime
# from pymongo import MongoClient

st.set_page_config(page_title="Viraindo Explorer", layout='wide')

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
        filtered_df = filtered_df[filtered_df['name'].str.lower().str.contains(filter.lower()) == True]
    return filtered_df.reset_index(drop=True)

def filter_price(df, min, max):
    filtered_df = df.copy()
    filtered_df = filtered_df[filtered_df['price'] >= min]
    filtered_df = filtered_df[filtered_df['price'] <= max]
    return filtered_df.sort_values(by=['name','price']).reset_index(drop=True)

@st.experimental_memo
def get_today_date():
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=+7))).strftime("%Y-%m-%d")

@st.experimental_memo
def get_data(date: str):
    # with MongoClient('mongodb://localhost:27017/') as client:
    #     coll = client['viraindo']['Notebook']
    #     df = pd.DataFrame(list(coll.find()))
    #     df.drop(columns=['_id','item_id','category'], inplace=True)
    df = pd.read_csv("https://raw.githubusercontent.com/Aulim/vira-db/main/data/viraindo_notebook.csv")
    df.drop(columns=['item_id','category'], inplace=True)
    df = df.loc[df['date'] == date]
    df.drop(columns=['date'], inplace=True)
    return df

current_date = get_today_date()
df = get_data(current_date)

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
        st.session_state.min_price = 0.0
        st.session_state.max_price = 9999999999.0
        st.experimental_rerun()
else:
    st.session_state.filter_params = []

if 'min_price' in st.session_state and 'max_price' in st.session_state:
    df = filter_price(df, st.session_state.min_price, st.session_state.max_price)
    st.write(f'Mencari produk dengan harga antara {st.session_state.min_price} sampai {st.session_state.max_price}')
else:
    st.session_state.min_price = 0.0
    st.session_state.max_price = 9999999999.0

with st.form("Filter form", True):
    filter = st.text_input("Cari produk yang mengandung kata:")
    min, max = st.columns([1,1])
    #TODO: Fix the max price
    min_val = st.session_state.min_price if st.session_state.min_price is not None else 0.0
    max_val = st.session_state.max_price if st.session_state.max_price is not None else 9999999999.0
    min_price = min.number_input("Harga minimum", min_value=0.0, max_value=9999999999.0, value=float(min_val))
    max_price = max.number_input("Harga maksimum", min_value=0.0, max_value=9999999999.0, value=float(max_val))
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
    curr_page_start_product = ((st.session_state.page_current - 1) * show_rows) + 1
    if st.session_state.page_current * show_rows < len(df):
        curr_page_end_product = st.session_state.page_current * show_rows
    else:
        curr_page_end_product = len(df)
    st.write(f"Ditemukan {len(df)} produk. Tampilkan produk ke-{curr_page_start_product} sampai {curr_page_end_product}")
    prev, _, next = st.columns([4,30,4])

    prev_button = prev.button("Prev", disabled=st.session_state.page_current <= 1, key='prev_top')
    next_button = next.button("Next", disabled=st.session_state.page_current >= page_limit, key='next_top')

    st.table(show_dataframe_paginated(df, st.session_state.page_current, show_rows))

    prev_bottom, _, next_bottom = st.columns([4,30,4])
    prev_button_bottom = prev_bottom.button("Prev", disabled=st.session_state.page_current <= 1, key='prev_bottom')
    next_button_bottom = next_bottom.button("Next", disabled=st.session_state.page_current >= page_limit, key='next_bottom')

    if prev_button or prev_button_bottom:
        st.session_state.page_current-=1
        st.experimental_rerun()
        
    if next_button or next_button_bottom:
        st.session_state.page_current+=1
        st.experimental_rerun()

    st.markdown("[Back to top](#top)")
else:
    st.write("Tidak ditemukan produk yang mengandung kata: ", ', '.join(st.session_state.filter_params))

