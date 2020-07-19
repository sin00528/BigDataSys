import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from tqdm import tqdm
from PIL import Image
from wordcloud import WordCloud, STOPWORDS

df_union = pd.read_csv('./data/dc_db.csv', sep=',', encoding='utf-8', index_col=0)
df_union.head()

print('전체 데이터 개수 : ', len(df_union))

print('\n ===== 데이터 프레임 확인 ===== ')
cmt_length = df_union['cmt_contents'].astype(str).apply(len)
print(cmt_length.head(20))


# log-histogrom : comment length
plt.figure(figsize=(12,5))
plt.hist(cmt_length, bins=200, alpha=0.5, color='g', label='word')
plt.yscale('log', nonposy='clip')
plt.title('Log-Histogram of length of comments')
plt.xlabel('Length of review')
plt.ylabel('Number of review')
plt.show()

print('\n ===== 댓글 길이 분석 ===== ')
print('댓글 길이 최댓값 ', np.max(cmt_length))
print('댓글 길이 최솟값 ', np.min(cmt_length))
print('댓글 길이 평균값 ', np.mean(cmt_length))
print('댓글 길이 표준편차 ', np.std(cmt_length))
print('댓글 길이 중간값 ', np.median(cmt_length))
print('댓글 길이 제1사분위 ', np.percentile(cmt_length, 25))
print('댓글 길이 제3사분위 ', np.percentile(cmt_length, 75))


# log-histogrom : comment word count
word_counts = df_union['cmt_contents'].astype(str).apply(lambda x:len(x.split(' ')))

plt.figure(figsize=(10, 8))
plt.hist(word_counts, bins=50, facecolor='g', label='train')
plt.title('Log-Histogram of word count in comments', fontsize=15)
plt.yscale('log', nonposy='clip')
plt.legend()
plt.xlabel('Number of words', fontsize=15)
plt.xlabel('Number of comments', fontsize=15)
plt.show()

print('\n ===== 댓글 단어 개수 분석 ===== ')
print('댓글 단어 개수 최댓값 ', np.max(word_counts))
print('댓글 단어 개수 최솟값 ', np.min(word_counts))
print('댓글 단어 개수 평균값 ', np.mean(word_counts))
print('댓글 단어 개수 표준편차 ', np.std(word_counts))
print('댓글 단어 개수 중간값 ', np.median(word_counts))
print('댓글 단어 개수 제1사분위 ', np.percentile(word_counts, 25))
print('댓글 단어 개수 제3사분위 ', np.percentile(word_counts, 75))

# box-plot
plt.figure(figsize=(12,5))
plt.boxplot(cmt_length, labels=['counts'], showmeans=True)
plt.show()


# count-plot
fig, axe = plt.subplots(ncols=1)
fig.set_size_inches(6, 3)
sns.countplot(df_union['label'])
plt.show()

print('\n ===== 레이블 데이터 분석 ===== ')
print('욕설 댓글 개수', df_union['label'].value_counts()[1])
print('욕설이 아닌 댓글 개수', df_union['label'].value_counts()[0])


# wordCloud
path = 'c:/Windows/Fonts/malgun.ttf'

train_cmt = [cmt for cmt in df_union['cmt_contents'] if type(cmt) is str]
wordcloud = WordCloud(font_path=path,
                      relative_scaling=0.5,
                      background_color = 'white').generate(' '.join(train_cmt))
plt.figure(figsize=(8,6))
plt.imshow(wordcloud)
plt.axis("off")
plt.show()
