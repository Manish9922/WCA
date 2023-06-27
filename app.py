import streamlit as st
import data_framing,analyzer
import matplotlib.pyplot as plt
import seaborn as sns

st.sidebar.title("Whatsapp Chat Analyzer")

uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:

    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df = data_framing.frame_data(data)

    # fetch unique users
    user_list = df['user'].unique().tolist()
    user_list.sort()
    user_list.insert(0,"Overall")

    selected_user = st.sidebar.selectbox("Show Chat analysis wrt",user_list)

    if st.sidebar.button("Show Analysis"):

        num_messages, num_of_words, num_media_messages, num_links, num_del_mes = analyzer.fetch_stats(selected_user,df)
        if selected_user == 'Overall':
            md = analyzer.most_messages_deleted(df)

        df = analyzer.remove_unwanted_data(selected_user, df)

        nw = analyzer.count_negative_words(selected_user, df)

        # Stats Area
        st.title("Top Statistics")
        col1, col2, col3, col4, = st.columns(4)

        with col1:
            st.header("Total Messages")
            st.title(num_messages)
        with col2:
            st.header("Total Words")
            st.title(num_of_words)
        with col3:
            st.header("Media Shared")
            st.title(num_media_messages)
        with col4:
            st.header("Links Shared")
            st.title(num_links)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.header("Deleted Messages")
            st.title(num_del_mes)
        with col2:
            st.header("Positive Messages")
            st.title(str(100 - nw) + "%")
        with col3:
            st.header("Negative Messages")
            st.title(str(nw) + "%")
        with col4:
            st.header("Overall Sentiment")
            if nw > 50:
                st.title("Negative")
            elif nw > 25:
                st.title("Neutral")
            else:
                st.title("Positive")

        # finding the busiest users in the group(Group level)
        if selected_user == 'Overall':
            st.title('Most Busy Users')
            x,new_df = analyzer.most_busy_users(df)
            fig, ax = plt.subplots()

            col1, col2 = st.columns(2)

            with col1:
                ax.bar(x.index, x.values,color='red')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)
            with col2:
                st.dataframe(new_df)

            col1, col2 = st.columns(2)

            with col1:
                st.title('Most Messages deleted by')
                fig, ax = plt.subplots()
                ax.bar(md.keys(), md.values(), color='purple')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)
            with col2:
                st.title('Most Negative words by')
                x = analyzer.most_negative_messages(df)
                fig, ax = plt.subplots()
                ax.bar(x.keys(), x.values(), color='blue')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)

        if num_of_words != 0:

            # WordCloud
            st.title("Wordcloud")
            df_wc = analyzer.create_wordcloud(selected_user,df)
            fig,ax = plt.subplots()
            ax.imshow(df_wc)
            st.pyplot(fig)

            # most common words
            most_common_df = analyzer.most_common_words(selected_user,df)

            fig,ax = plt.subplots()

            ax.barh(most_common_df[0],most_common_df[1])
            plt.xticks(rotation='vertical')

            st.title('Most frequent words')
            st.pyplot(fig)

            # emoji analysis
            emoji_df = analyzer.emoji_helper(selected_user,df)
            if emoji_df.shape[0]!=0:
                st.title("Emoji Analysis")

                col1,col2 = st.columns(2)

                with col1:
                    st.dataframe(emoji_df)
                with col2:
                    fig,ax = plt.subplots()
                    ax.pie(emoji_df[1].head(),labels=emoji_df[0].head(),autopct="%0.2f")
                    st.pyplot(fig)

            #Timeline
            st.title('Activity Timeline')
            col1, col2 = st.columns(2)

            with col1:
                # daily timeline
                st.title("Daily Timeline")
                daily_timeline = analyzer.daily_timeline(selected_user, df)
                fig, ax = plt.subplots()
                ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='black')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)

            with col2:
                # monthly timeline
                st.title("Monthly Timeline")
                timeline = analyzer.monthly_timeline(selected_user, df)
                fig, ax = plt.subplots()
                ax.plot(timeline['time'], timeline['message'], color='green')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)

            # activity map
            st.title('Activity Map')
            col1, col2 = st.columns(2)

            with col1:
                st.header("Most busy day")
                busy_day = analyzer.week_activity_map(selected_user, df)
                fig, ax = plt.subplots()
                ax.bar(busy_day.index, busy_day.values, color='purple')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)

            with col2:
                st.header("Most busy month")
                busy_month = analyzer.month_activity_map(selected_user, df)
                fig, ax = plt.subplots()
                ax.bar(busy_month.index, busy_month.values, color='orange')
                plt.xticks(rotation='vertical')
                st.pyplot(fig)

            st.title("Weekly Activity HeatMap")
            user_heatmap = analyzer.activity_heatmap(selected_user, df)
            fig, ax = plt.subplots()
            ax = sns.heatmap(user_heatmap)
            st.pyplot(fig)
