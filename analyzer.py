import itertools
from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
from collections import Counter
import emoji

extract = URLExtract()

def remove_unwanted_data(selected_user, df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    df = df[df['user'] != 'group_notification']
    df = df[df['message'] != '<Media omitted>\n']
    df = df[df['message'] != 'This message was deleted\n']

    links = []
    for message in df['message']:
        links.extend(extract.find_urls(message))

    for i in range(len(links)):
        df = df[df['message'] != str(links[i]+'\n')]

    return df

def fetch_stats(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # fetch the number of messages
    num_messages = df.shape[0]

    # fetch number of media messages
    num_media_messages = df[df['message'] == '<Media omitted>\n'].shape[0]

    # fetch number of deleted messages
    num_del_mes = df[df['message'] == 'This message was deleted\n'].shape[0]

    # fetch the total number of words
    df = remove_unwanted_data(selected_user, df)
    words = []
    for message in df['message']:
        words.extend(message.split())

    # fetch number of links shared
    links = []
    for message in df['message']:
        links.extend(extract.find_urls(message))

    return num_messages,len(words),num_media_messages,len(links),num_del_mes

def most_busy_users(df):
    x = df['user'].value_counts().head()
    df = round((df['user'].value_counts() / df.shape[0]) * 100, 2).reset_index().rename(columns={'index': 'name', 'user': 'name'})
    return x,df

def most_messages_deleted(df):

    dic = {}
    msg = df['message'].tolist()
    user = df['user'].tolist()
    for i in range(df.shape[0]):
        if msg[i] == 'This message was deleted\n':
            if user[i] not in dic.keys():
                dic[user[i]] = 1
            else:
                dic[user[i]] = dic[user[i]] + 1

    dic = dict(sorted(dic.items(), key=lambda x: x[1], reverse=True))
    dic = dict(itertools.islice(dic.items(), 5))
    return dic

def most_negative_messages(df):

    f = open('negative_words.txt', 'r')
    neg_words = f.read()
    nl = []
    for word in neg_words.lower().split():
        nl.append(word)
    dic = {}
    msg = df['message'].tolist()
    user = df['user'].tolist()
    for i in range(df.shape[0]):
        message=msg[i].lower().split()
        for j in range(len(message)):
            if message[j] in nl:
                if user[i] not in dic.keys():
                    dic[user[i]] = 1
                else:
                    dic[user[i]] = dic[user[i]] + 1

    dic = dict(sorted(dic.items(), key=lambda x: x[1], reverse=True))
    dic = dict(itertools.islice(dic.items(), 5))
    return dic

def create_wordcloud(df):

    def wordlist(message):
        y = []
        for word in message.lower().split():
            y.append(word)
        return " ".join(y)

    wc = WordCloud(width=500,height=500,min_font_size=10,background_color='white')
    df['message'] = df['message'].apply(wordlist)
    if df.shape[0]!=0:
        df_wc = wc.generate(df['message'].str.cat(sep=" "))
        return df_wc

def remove_hinglish(df):

    f = open('stop_hinglish.txt', 'r')
    stop_words = f.read()
    sw = []
    for word in stop_words.lower().split():
        sw.append(word)

    words = []
    for message in df['message']:
        for word in message.lower().split():
            if word not in sw:
                words.append(word)

    return words

def most_common_words(df):

    words = remove_hinglish(df)
    most_common_df = pd.DataFrame(Counter(words).most_common(20))
    return most_common_df

def most_neg_words(df):

    words = remove_hinglish(df)
    f = open('negative_words.txt', 'r')
    neg_words = f.read()
    nl = []
    for word in neg_words.lower().split():
        nl.append(word)
    nw = []
    for i in range(len(words)):
        if words[i] in nl:
            nw.append(words[i])
    most_common_df = pd.DataFrame(Counter(nw).most_common(20))
    return most_common_df

def count_negative_words(df):

    words = []
    for message in df['message']:
        for word in message.lower().split():
            words.append(word)

    f = open('negative_words.txt', 'r')
    neg_words = f.read()
    nl = []
    for word in neg_words.lower().split():
        nl.append(word)
    nw=[]
    for i in range(len(words)):
        if words[i] in nl:
            nw.append(words[i])
    if(len(words)!=0):
        return round((len(nw)/len(words)*100),1)
    else:
        return 0

def emoji_helper(df):

    emojis = []
    for message in df['message']:
        emojis.extend([c for c in message if c in emoji.UNICODE_EMOJI['en']])

    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))

    return emoji_df

def monthly_timeline(df):

    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()

    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))

    timeline['time'] = time

    return timeline
