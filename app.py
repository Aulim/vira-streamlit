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

#region Functions
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
    return filtered_df.reset_index(drop=True)

def on_search_product():
    if len(filter) > 0:
        _filters = filter.split(",")
        st.session_state.filter_params = _filters
    st.session_state.page_current = 1
    st.session_state.product_filter = ""
    # st.experimental_rerun()

def on_add_search_product():
    if len(filter) > 0:
        _filters = filter.split(",")
        st.session_state.filter_params = st.session_state.filter_params + _filters
    st.session_state.page_current = 1
    st.session_state.product_filter = ""
    # st.experimental_rerun()

def on_reset_product():
    st.session_state.filter_params = []
    st.session_state.page_current = 1
    st.session_state.product_filter = ""
    # st.experimental_rerun()

def on_page_select_changed():
    st.session_state.page_current = st.session_state.page_selected

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
    df = df.reset_index(drop=True)
    df.drop(columns=['date'], inplace=True)
    df['price'] = pd.to_numeric(df['price'], downcast='float')
    return df
#endregion

#region Init Session State Variables
if 'page_current' not in st.session_state:
    st.session_state.page_current = 1

if 'filter_params' not in st.session_state:
    st.session_state.filter_params = []

if 'min_price' not in st.session_state:
    st.session_state.min_price = 0.0

if 'max_price' not in st.session_state:
    st.session_state.max_price = 9999999999.0

if 'sorting' not in st.session_state:
    st.session_state.sorting = False

if 'sort_by' not in st.session_state:
    st.session_state.sort_by = 'price'

if 'sort_asc' not in st.session_state:
    st.session_state.sort_asc = True

if 'page_selected' not in st.session_state:
    st.session_state.page_selected = 1
#endregion

current_date = get_today_date()
df = get_data(current_date)

with st.expander("Lakukan pencarian", expanded=True):
    # filter = stt.st_tags(label="Cari produk dengan kata kunci:", text="Tekan enter untuk menambah kata kunci", key="search_query", value=st.session_state.filter_params)
    filter = st.text_input(label="Cari produk (pisahkan dengan tanda koma ','):", key="product_filter")
    search, add, reset = st.columns([1,1,1])
    search_filter_button = search.button("Cari produk", on_click=on_search_product)
    add_filter_button = add.button("Persempit produk", on_click=on_add_search_product)
    reset_filter_button = reset.button("Reset pencarian", on_click=on_reset_product)
    min, max = st.columns([1,1])
    min_val = st.session_state.min_price
    max_val = st.session_state.max_price
    min_price = min.number_input("Harga minimum", min_value=0.0, max_value=9999999999.0, value=float(min_val))
    max_price = max.number_input("Harga maksimum", min_value=0.0, max_value=9999999999.0, value=float(max_val))
    price_filter, price_reset = st.columns([1,1])
    reset_price_button = price_reset.button("Reset rentang harga")
    price_filter_button = price_filter.button("Cari dengan rentang harga")
    # if search_filter_button:
    #     if len(filter) > 0:
    #         _filters = filter.split(",")
    #         st.session_state.filter_params = _filters
    #     st.session_state.page_current = 1
    #     st.experimental_rerun()
    # if add_filter_button:
    #     if len(filter) > 0:
    #         _filters = filter.split(",")
    #         st.session_state.filter_params = st.session_state.filter_params + _filters
    #     st.session_state.page_current = 1
    #     st.experimental_rerun()
    if price_filter_button:
        st.session_state.min_price = min_price
        st.session_state.max_price = max_price
        st.session_state.page_current = 1
        st.experimental_rerun()
    # if reset_filter_button:
    #     st.session_state.filter_params = []
    #     st.session_state.page_current = 1
    #     st.experimental_rerun()
    if reset_price_button:
        st.session_state.min_price = 0.0
        st.session_state.max_price = 9999999999.0
        st.session_state.page_current = 1
        st.experimental_rerun()

#region Sort Data
reset_sort, sort_name_asc, sort_name_desc, sort_price_asc, sort_price_desc = st.columns([1,1,1,1,1])
if reset_sort.button('Hapus penyortiran'):
    st.session_state.sorting = False
    st.experimental_rerun()

if sort_name_asc.button('Urutkan berdasarkan nama A-Z'):
    st.session_state.sorting = True
    st.session_state.sort_by = 'name'
    st.session_state.sort_asc = True
    st.experimental_rerun()

if sort_name_desc.button('Urutkan berdasarkan nama Z-A'):
    st.session_state.sorting = True
    st.session_state.sort_by = 'name'
    st.session_state.sort_asc = False
    st.experimental_rerun()

if sort_price_asc.button('Urutkan berdasarkan harga rendah ke tinggi'):
    st.session_state.sorting = True
    st.session_state.sort_by = 'price'
    st.session_state.sort_asc = True
    st.experimental_rerun()

if sort_price_desc.button('Urutkan berdasarkan harga tinggi ke rendah'):
    st.session_state.sorting = True
    st.session_state.sort_by = 'price'
    st.session_state.sort_asc = False
    st.experimental_rerun()

if 'sorting' in st.session_state and 'sort_by' in st.session_state and 'sort_asc' in st.session_state:
    if st.session_state.sorting:
        df = df.sort_values(by=st.session_state.sort_by, ascending=st.session_state.sort_asc)
#endregion

#region Filter Data
if 'filter_params' in st.session_state and len(st.session_state.filter_params) > 0:
    df = filter_name(df, st.session_state.filter_params)
    st.write(f"Anda mencari {', '.join(st.session_state.filter_params)}")

if st.session_state.min_price > 0 or st.session_state.max_price < 9999999999.0:
    df = filter_price(df, st.session_state.min_price, st.session_state.max_price)
    st.write(f'Mencari produk dengan harga antara {st.session_state.min_price} sampai {st.session_state.max_price}')

show_rows = 20
page_limit = math.ceil(len(df) / show_rows)
#endregion

if len(df) > 0:
    curr_page_start_product = ((st.session_state.page_current - 1) * show_rows) + 1
    if st.session_state.page_current * show_rows < len(df):
        curr_page_end_product = st.session_state.page_current * show_rows
    else:
        curr_page_end_product = len(df)
    st.write(f"Ditemukan {len(df)} produk. Menampilkan produk ke-{curr_page_start_product} sampai {curr_page_end_product}")
    valid_pages = [i for i in range(1,page_limit+1)]
    page_select = st.selectbox('Tampilkan halaman: ', valid_pages, index=st.session_state.page_current-1 or 0, on_change=on_page_select_changed, key='page_selected')
    page_show_label = st.write(f'Menampilkan halaman {st.session_state.page_current} dari {page_limit}')
    prev_top, _, next_top = st.columns([4,30,4])

    prev_button_top = prev_top.button("Prev", disabled=st.session_state.page_current <= 1, key='prev_top')
    next_button_top = next_top.button("Next", disabled=st.session_state.page_current >= page_limit, key='next_top')

    st.table(show_dataframe_paginated(df, st.session_state.page_current, show_rows))

    prev_bottom, _, next_bottom = st.columns([4,30,4])
    prev_button_bottom = prev_bottom.button("Prev", disabled=st.session_state.page_current <= 1, key='prev_bottom')
    next_button_bottom = next_bottom.button("Next", disabled=st.session_state.page_current >= page_limit, key='next_bottom')

    if prev_button_top or prev_button_bottom:
        if st.session_state.page_current > 1:
            st.session_state.page_current-=1
        st.experimental_rerun()
        
    if next_button_top or next_button_bottom:
        if st.session_state.page_current < page_limit:
            st.session_state.page_current+=1
        st.experimental_rerun()

    st.markdown("[Back to top](#top)")
else:
    st.write("Tidak ditemukan produk yang mengandung kata: ", ', '.join(st.session_state.filter_params))

