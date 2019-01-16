import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import sys
import nltk
from textblob import TextBlob
from wordcloud import WordCloud

if len(sys.argv) != 3:
    print("Error: Usage is 'py generate_graphs.py <filename> <context>'")
    
PATH_TO_CSV = sys.argv[1]
CONTEXT = sys.argv[2]

messages = pd.read_csv(PATH_TO_CSV, index_col=0, parse_dates=['date'])
receiver = messages[messages.is_from_me == 0]
sender = messages[messages.is_from_me == 1]

NUM_PERIODS = (max(messages.date) - min(messages.date)).days // 7 + 2

WEEKLY_DATE_RANGE = pd.date_range(
    start=pd.to_datetime(min(messages['date']).strftime("%Y-%m-%d")), 
    periods=NUM_PERIODS,
    freq='W-MON')

plt.style.use(CONTEXT)

def messages_pchart():
    num_messages = len(messages)
    num_receiver_messages = len(receiver)
    num_sender_messages = len(sender)
    
    def _format_pie_label(pct):
        total = int(pct/100 * num_messages)
        return f"{total} messages \n({pct:.2f}%)"
    
    fig, ax = plt.subplots(figsize=(10,10))
    ax.set_aspect('equal')
    
    ax.pie([num_receiver_messages, num_sender_messages],
           labels=['receiver', 'sender'],
           autopct=lambda num: _format_pie_label(num),
           startangle=90,
           shadow=True)
    ax.set_title("Who has sent more messages?")
    
    return fig

def weekly_texts():

    receiver_wtext = [receiver.week[receiver.week == i].count() for i in range(NUM_PERIODS)]
    sender_wtext = [sender.week[sender.week == i ].count() for i in range(NUM_PERIODS)]
    xlabels = [date.strftime("%b %d") for date in WEEKLY_DATE_RANGE]
    bar_width = 0.4

    fig, ax = plt.subplots(figsize=(12,10))
    ax.set_aspect('auto')
    
    rects1 = ax.bar(np.arange(NUM_PERIODS), receiver_wtext, bar_width, label="Receiver")
    rects2 = ax.bar(np.arange(NUM_PERIODS)+bar_width, sender_wtext, bar_width, label="Sender")
    
    ax.set_title("When did we text more often?")
    ax.set_xlabel("Week of")
    ax.set_ylabel("Texts sent")
    ax.set_xticks(np.arange(NUM_PERIODS) + bar_width / 2)
    ax.set_xticklabels(xlabels)
    ax.legend(loc=0)
    
    for rects in [rects1, rects2]:
        for rect in rects:
            height = rect.get_height()
            ax.text(rect.get_x() + rect.get_width()/2, height, 
                    '%d' % int(height), ha='center', va='bottom',
                    rotation=0,
                    fontsize='small')
        
    fig.tight_layout()
    fig.autofmt_xdate()
    
    return fig

def text_length_hist():
    fig, ax = plt.subplots(figsize=(10,8))
    ax.set_aspect('auto')
    ax.set_title("Who sends longer texts?\n(Dist. of text messages)")
    
    for i, db in enumerate([receiver, sender]): 
        db_name = 'Receiver' if i == 0 else 'Sender'
        ax.hist(db.text_length[db.text_length < 800], bins=50,alpha=0.7, label=db_name)
        
    ax.legend(loc=0)
    ax.set_xlabel("Text length")
    
    return fig

def num_words_hist():
    fig, ax = plt.subplots(1, 1, figsize=(10,8))
    ax.set_aspect('auto')
    ax.set_title("Who sends more words per text?\n(Dist. of number of words/text)")
    
    for i, db in enumerate([receiver, sender]): 
        db_name = 'Receiver' if i == 0 else 'Sender'
        ax.hist(db.num_words[db.num_words < 202], bins=50,alpha=0.7, label=db_name)
              
    ax.legend(loc=0)
    ax.set_xlabel("Number of words per text")
    
    return fig

def messages_wordcloud(db, color):
    stopwords = set(nltk.corpus.stopwords.words("english")).union(set(['u','ull','youre','ure','i',"ill","im"]))
    def _get_texts(db):
        text = [word.lower() for message in db['text'] for word in message.split() if word.lower() not in stopwords]
        return " ".join(text)
    text = _get_texts(db)
    wc = WordCloud(
        normalize_plurals = True,
        stopwords=stopwords, 
        scale=5,  # higher the number, the more it renders with high definition
        background_color='white', 
        colormap=color).generate(text)
    
    fig, ax = plt.subplots(figsize=(12,12))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    ax.set_aspect('equal')

    return fig

def message_positivity_graph():
    
    def _get_message_polarity(db):
        polarities = [TextBlob(message).sentiment.polarity for message in db.text]
        polarities = list(filter(lambda polarity: polarity != 0, polarities))
        return polarities
    
    receiver_polarity = _get_message_polarity(receiver)
    sender_polarity = _get_message_polarity(sender)
    
    MIN = min([len(receiver_polarity), len(sender_polarity)])
    
    receiver_polarity = receiver_polarity[:MIN]
    sender_polarity = sender_polarity[:MIN]
    
    fig, ax = plt.subplots(figsize=(12,12))
    
    ax = sns.kdeplot(receiver_polarity, sender_polarity,
                    shade=True, cmap='Purples', ax=ax)
    ax.set_title("On a scale of [-1, 1], how positive is our conversation?\n(bivariate distribution of the polarity of the messages)")
    ax.set_aspect('equal')

    ax.set_xlabel("receiver")
    ax.set_ylabel("sender")
    
    return fig

def messages_by_day():
    days = ["",'Mon','Tues','Wed','Thu','Fri','Sat','Sun']
    
    fig, ax = plt.subplots(figsize=(12,10))
    
    ax.bar(days[1:], [messages[messages.day == d].hourly_bin.count() for d in range(7)])
    
    ax.set_title("What days did we send our texts?")
    ax.set_ylabel("Number of texts sent")
    ax.grid(axis='y')
    
    return fig

def messages_by_hour():
    days = ["",'Mon','Tues','Wed','Thu','Fri','Sat','Sun']
    
    fig, ax = plt.subplots(figsize=(12,10))
    
    ax = sns.violinplot(x='day', y='hourly_bin',
                       hue='is_from_me', split=True,
                       data=messages,cut=0,
                       orient='v', ax=ax)
    ax.get_xaxis().get_label().set_visible(False)
    ax.get_yaxis().get_label().set_visible(False)
    
    legend = ax.legend(bbox_to_anchor=(1.005, 1.005), loc=2)
    labels = ['Receiver', 'Sender']
    
    for text, label in zip(legend.texts, labels):
        text.set_text(label)
    
    ax.set_xticklabels(labels=days[1:])
    ax.yaxis.set_ticks(list(range(0, 24, 3)) + [23])
    ax.yaxis.set_major_formatter(matplotlib.ticker.StrMethodFormatter('{x:,.0f}:00H'))
    ax.grid(axis='y')
    
    ax.set_title("What hour did we send our texts?")
    
    return fig

# save figures
messages_by_hour().savefig('messages_by_hour.png', quality=95)
messages_by_day().savefig('messages_by_day.png', quality=95)
messages_pchart().savefig('pie_chart.png', quality=95)
weekly_texts().savefig('weekly_messages_sent.png', quality=95)
text_length_hist().savefig('text_length_hist.png', quality=95)
num_words_hist().savefig('num_words_hist.png', quality=95)
messages_wordcloud(receiver, 'Blues_r').savefig('receiver_wordcloud.png', quality=95)
messages_wordcloud(sender, 'Greens_r').savefig('sender_wordcloud.png', quality=95)
message_positivity_graph().savefig('positivity_graph.png', quality=95)