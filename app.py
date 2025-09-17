import streamlit as st
import pandas as pd
import datetime
from streamlit_autorefresh import st_autorefresh
# import pytz

# Run the autorefresh every 2000 milliseconds (2 seconds)
st_autorefresh(interval=3000, key="data_refresher")

def get_current_time():
    current_time = datetime.datetime.utcnow() - datetime.timedelta(hours=5)
    return current_time

def get_theaters(dt_ts):
    theaters = df[df['start_ts'] >= now]['theater_number'].unique()
    return theaters

def get_current_block(dt_ts, theater_id):
    blocks = df[(df['theater_number'] == theater_id) & (df['start_ts'] <= dt_ts) & (df['end_ts'] >= dt_ts)].copy().reset_index()
    if len(blocks) > 0:
        curr_block_id = blocks.loc[0, 'block_id']
    else:
        curr_block_id = 0
    return curr_block_id

def get_next_block(dt_ts, theater_id):
    blocks = df[(df['theater_number'] == theater_id) & (df['end_ts'] >= dt_ts) & (df['start_ts'] >= dt_ts)].copy().reset_index()
    if len(blocks) > 1:
        curr_block_id = blocks['block_id'].unique()[0]
    # elif len(blocks) == 1:
    #     curr_block_id = blocks['block_id'].unique()[0]
    else:
        curr_block_id = 0
    return curr_block_id

def get_block_start(block_id):
    if block_id == 0:
        return ['N/A']
    start_ts = df[df['block_id'] == block_id]['start_ts'].unique()[0]
    return start_ts

def get_films(block_id):
    if block_id == 0:
        return ['N/A']
    film_list = df[df['block_id'] == block_id]['film_name'].to_list()
    return film_list

def check_qa_status(block_id):
    if block_id == 0:
        return False
    status = any(df[df['block_id'] == block_id]['has_qa'])
    return status

def check_qa_time(block_id):
    if block_id == 0:
        return 0
    qa_time = df[df['block_id'] == block_id]['qa_time_available'].iloc[0]
    return qa_time

df = pd.read_csv('data/csaff25_operations_20250917.csv')

current_cols = ['Film Name',
                'Film Name to Match',
                'Venue',
                'Theater Number',
                'Film Screen Date',
                'Film Run Time (minutes)',
                'Film Block Id',
                'Film Sequence in Block',
                'Film Block Start Time',
                'Film Block End Time',
                'Approx Sequence Start Time',
                'Film Block has Q&A',
                'Approximate Time for Q&A Per Block',
                'Category']
df.rename(columns={
    ' Film Name':'film_name',
    'Film Name to Match':'match_name',
    'Venue':'venue',
    'Theater Number':'theater_number',
    'Film Screen Date':'screen_date',
    'Film Run Time (minutes)':'run_time',
    'Film Block Id':'block_id',
    'Film Sequence in Block':'sequence_id',
    'Film Block Start Time':'start_time',
    'Film Block End Time':'end_time',
    'Approx Sequence Start Time':'seq_start',
    'Film Block has Q&A':'has_qa',
    'Approximate Time for Q&A Per Block':'qa_time_available',
    'Category':'category'
}, inplace=True)
# df['start_time']
df['start_ts'] = df['screen_date'] + ' ' + df['start_time']
df['start_ts'] = df['start_ts'].apply(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d %I:%M %p'))
df['end_ts'] = df['screen_date'] + ' ' + df['end_time']
df['end_ts'] = df['end_ts'].apply(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d %I:%M %p'))
# now = get_current_time()
# now = datetime.datetime.fromisoformat('2025-09-18 13:05:00')
if st.checkbox('Use current time'):
    time_default = get_current_time()
else:
    time_default = datetime.datetime(2025, 9, 19, 13, 30)
now = st.slider(
    "Set start time",
    # value=datetime.datetime(2025, 9, 19, 13, 30),
    value=time_default,
    min_value=datetime.datetime(2025, 9, 18, 8, 30),
    max_value=datetime.datetime(2025, 9, 21, 23, 45),
    format="MM/DD/YY - HH:mm",
    step=datetime.timedelta(minutes=15)
)

current_theater = st.selectbox('Choose a theater', get_theaters(now))


st.header('CSAFF 2025 AMC')
st.subheader('Now Playing')
current_block = get_current_block(now, current_theater)
block_start = get_block_start(current_block)
st.write(f"Block: {current_block} starting at: {block_start}")
current_films = get_films(current_block)
for film in current_films:
    st.markdown("- " + film)
has_qa = check_qa_status(current_block)
if has_qa:
    st.write('This block has a confirmed Q&A')
qa_time_available = check_qa_time(current_block)
if qa_time_available > 0:
    st.write(f"approximate time available for Q&A: {qa_time_available} minutes")

st.subheader('Up Next')
next_block = get_next_block(now, current_theater)
block_start = get_block_start(next_block)
st.write(f"Block: {next_block} starting at: {block_start}")
next_films = get_films(next_block)
for film in next_films:
    st.markdown("- " + film)
has_qa = check_qa_status(next_block)
if has_qa:
    st.write('This block has a confirmed Q&A')
qa_time_available = check_qa_time(next_block)
if qa_time_available > 0:
    st.write(f"approximate time available for Q&A: {qa_time_available} minutes")

st.subheader('All remaining films')
remaining_films = df[(df['start_ts'] >= now)] 
                    #  & (df['start_time'] >= now.hour)]
st.dataframe(remaining_films)

# if st.button('refresh current time'):
#     now = get_current_time()
st.write(now)

