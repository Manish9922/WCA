import itertools
from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
from collections import Counter
import emoji

extract = URLExtract()

def fetch_stats(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # fetch the number of messages
    num_messages = df.shape[0]

    # fetch the total number of words
    words = []
    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']
    temp = temp[temp['message'] != 'This message was deleted\n']
    for message in temp['message']:
        words.extend(message.split())

    # fetch number of media messages
    num_media_messages = df[df['message'] == '<Media omitted>\n'].shape[0]

    # fetch number of deleted messages
    num_del_mes = df[df['message'] == 'This message was deleted\n'].shape[0]

    # fetch number of links shared
    links = []
    for message in df['message']:
        links.extend(extract.find_urls(message))

    return num_messages,len(words),num_media_messages,len(links),num_del_mes

def most_busy_users(df):
    x = df['user'].value_counts().head()
    df = round((df['user'].value_counts() / df.shape[0]) * 100, 2).reset_index().rename(
        columns={'index': 'name', 'user': 'percent'})
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
    temp = df[df['message'] != '<Media omitted>\n']
    temp = temp[temp['message'] != 'This message was deleted\n']
    msg = temp['message'].tolist()
    user = temp['user'].tolist()
    for i in range(temp.shape[0]):
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

def remove_unwanted_data(selected_user,df):
    f = open('stop_hinglish.txt', 'r')
    stop_words = f.read()
    sw = []
    for word in stop_words.lower().split():
        sw.append(word)

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']
    temp = temp[temp['message'] != 'This message was deleted\n']

    return sw,temp

def create_wordcloud(selected_user,df):
    stop_words, temp = remove_unwanted_data(selected_user, df)

    def remove_stop_words(message):
        y = []
        for word in message.lower().split():
            if word not in stop_words:
                y.append(word)
        return " ".join(y)

    wc = WordCloud(width=500,height=500,min_font_size=10,background_color='white')
    temp['message'] = temp['message'].apply(remove_stop_words)
    if temp.shape[0]!=0:
        df_wc = wc.generate(temp['message'].str.cat(sep=" "))
        return df_wc

def most_common_words(selected_user,df):

    stop_words,temp=remove_unwanted_data(selected_user,df)

    words = []

    for message in temp['message']:
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)

    most_common_df = pd.DataFrame(Counter(words).most_common(20))
    return most_common_df

def count_negative_words(selected_user,df):
    stop_words, temp = remove_unwanted_data(selected_user,df)

    words = []

    for message in temp['message']:
        for word in message.lower().split():
            if word not in stop_words:
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
        return int(len(nw)/len(words)*100)
    else:
        return 0

def emoji_helper(selected_user,df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    emojis = []
    for message in df['message']:
        emojis.extend([c for c in message if c in emoji.UNICODE_EMOJI['en']])

    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))

    return emoji_df

def monthly_timeline(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()

    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))

    timeline['time'] = time

    return timeline

def daily_timeline(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    dt = df.groupby('only_date').count()['message'].reset_index()

    return dt

def week_activity_map(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['day_name'].value_counts()

def month_activity_map(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    return df['month'].value_counts()

def activity_heatmap(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    user_heatmap = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)

    return user_heatmap
