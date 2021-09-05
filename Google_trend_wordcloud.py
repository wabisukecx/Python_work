# ----------------------------------------------------------------------------
# Name:        Google Trend to Wordcloud
# Author:      wabisuke
# Created:     29/08/2021
# Copyright:   (c) wabisuke 2021
# ----------------------------------------------------------------------------
import itertools
import pandas as pd
import datetime
from pytrends.request import TrendReq
from wordcloud import WordCloud

total_rising_percentage = []
trending_searches_dict = {}
total_build_payload_dict = {}

trends = TrendReq(hl='ja-jp', tz=540)  # trend in japan
trending_result = trends.trending_searches(pn='japan')  # search top 20 trend keyword
df = pd.DataFrame(trending_result)  # extract only dataframe
trend_list = df.values.tolist()  # convert to list
trend_list = list(itertools.chain.from_iterable(trend_list))  # convert to 2d list to 1d list
trend_list_work = trend_list.copy()

for i in range(len(trend_list)):
    rising_percentage = 0
    topic_title_list = []
    value_list = []
    build_payload_dict = {}

    trends.build_payload(kw_list=trending_result[0][i:i + 1], timeframe='now 1-d', geo="JP")  # specify 1week
    rt = trends.related_topics()  # search related topics of trend
    print(trending_result[0][i:i + 1])
    no_data = rt[trend_list[i]]['rising']
    if not no_data.empty:  # no rising data ?
        for j in range(len(rt[trend_list[i]]['rising']['value'])):
            topic_title_list.append(rt[trend_list[i]]['rising']['topic_title'][j])  # set related topics
            value_list.append(rt[trend_list[i]]['rising']['value'][j])  # set rising percentage
            rising_percentage += rt[trend_list[i]]['rising']['value'][j]  # increment rising percentage
        build_payload_dict = dict(zip(topic_title_list, value_list))  # create dict build_payload
        total_build_payload_dict.update(build_payload_dict)  # merge each build_payload result
        total_rising_percentage.append(rising_percentage)  # add total rising percentage
        trending_searches_dict = dict(zip(trend_list_work, total_rising_percentage))  # create dict trending_searches
    else:
        trend_list_work.remove(trend_list[i])  # suppress no rising data keyword

now = datetime.datetime.now()
trending_searches_dict.update(total_build_payload_dict)  # merge each trending_searches result
word = WordCloud(font_path=r'C:\Windows\Fonts\YuGothR.ttc', width=1900, height=1080, background_color='black',
                 colormap='tab20').generate_from_frequencies(trending_searches_dict)
word.to_file('./word_cloud_{0:%y%m%d%H%M}.png'.format(now))
