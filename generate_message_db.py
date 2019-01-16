import pandas as pd
import sqlite3
import sys

HANDLE_IDS = sys.argv[1:]

PATH_TO_DB = "" # add your own PATH

conn = sqlite3.connect(PATH_TO_DB)
c = conn.cursor()

# get message df with the handles
command = f"""
          SELECT text, 
              is_from_me, 
              datetime(date/1000000000 + strftime('%s', '2001-01-01 00:00:00'), 'unixepoch') as date
          FROM message WHERE handle_id={HANDLE_IDS[0]} 
              OR handle_id={HANDLE_IDS[1]}
          ORDER BY date ASC;
          """
c.execute(command)

messages = pd.DataFrame(c.fetchall(), columns=['text', 'is_from_me', 'date'])

messages['date'] = pd.to_datetime(messages['date'])

# remove just attachments
errors = [i for i, text in enumerate(messages.text) if not isinstance(text,str)]
messages.drop(errors, axis=0, inplace=True)

# reindex 
messages.index = pd.RangeIndex(len(messages.index))

# -- SYNTHETIC COLUMNS ---
NUM_PERIODS = (max(messages.date) - min(messages.date)).days // 7 + 2
# the week it was sent
messages['week'] = pd.cut(
    messages.date, 
    bins=pd.date_range(
        pd.to_datetime(min(messages.date)).strftime("%Y-%m-%d"),
        periods=NUM_PERIODS,
        freq='W-TUE'),
    labels=range(NUM_PERIODS - 1))

# day it was sent. 0 == Monday, etc..
messages['day'] = messages['date'].apply(lambda x: x.weekday())

# the hour in which it was sent in 24h format
messages['hourly_bin'] = messages['date'].apply(lambda x: x.hour)

# holds the text_length
messages['text_length'] = [len(text) for text in messages.text]

# holds the word length of the text
messages['num_words'] = [len(text.split(" ")) for text in messages.text]


# export as csv file
messages.to_csv("messages.csv", sep=',', encoding='utf-8')
