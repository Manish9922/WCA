import re
import pandas as pd


def frame_data(data):

    pattern = r'(\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s?(?:am|pm|AM|PM)?\s-\s)'

    parts = re.split(pattern, data)

    messages = []
    dates = []

    for i in range(1, len(parts), 2):
        dates.append(parts[i].strip(" - "))
        messages.append(parts[i + 1])

    df = pd.DataFrame({
        'message_date': dates,
        'user_message': messages
    })

    df['message_date'] = pd.to_datetime(
        df['message_date'],
        dayfirst=True,
        errors='coerce'
    )

    df = df.dropna(subset=['message_date'])

    df.rename(columns={'message_date': 'date'}, inplace=True)

    users = []
    messages = []

    for message in df['user_message']:

        entry = re.split(r'([^:]+):\s', message, maxsplit=1)

        if len(entry) >= 3:
            users.append(entry[1])
            messages.append(entry[2])
        else:
            users.append('group_notification')
            messages.append(message)

    df['user'] = users
    df['message'] = messages

    df.drop(columns=['user_message'], inplace=True)

    df['only_date'] = df['date'].dt.date
    df['year'] = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month'] = df['date'].dt.month_name()
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    df = df[df["user"] != 'group_notification']

    period = []

    for hour in df['hour']:

        if hour == 23:
            period.append("23-00")

        elif hour == 0:
            period.append("00-01")

        else:
            period.append(f"{hour}-{hour+1}")

    df['period'] = period

    return df