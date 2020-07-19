import os
import re
import json
import numpy as np
import pandas as pd
from tqdm import tqdm
from konlpy.tag import Okt
from keras.preprocessing.sequence import pad_sequences
from keras.preprocessing.text import Tokenizer

df_union = pd.read_csv('./data/dc_db.csv', sep=',', encoding='utf-8', index_col=0)
cmt_length = df_union['cmt_contents'].astype(str).apply(len)

def preprocessing(data, mecab, remove_stopwords=False, stop_words=[]):
    data_text = re.sub("[^가-힣ㄱ-ㅎㅏ-ㅣ\\s]", "", data)
    words = mecab.morphs(data_text)
    if remove_stopwords:
        words = [token for token in words]

    return words

okt = Okt()

stop_words = set(['은', '는', '이', '가', '하', '아', '것',
                  '들', '의', '있', '되', '수', '보', '주',
                  '등', '한'])

clean_cmt = []

for review in tqdm(df_union['cmt_contents']):
    if type(review) == str:
        clean_cmt.append(preprocessing(review, okt, remove_stopwords=True, stop_words=stop_words))
    else:
        clean_cmt.append([])

tokenizer = Tokenizer()
tokenizer.fit_on_texts(clean_cmt)
train_sequences = tokenizer.texts_to_sequences(clean_cmt)
word_vocab = tokenizer.word_index

MAX_SEQUENCE_LENGTH = 12

train_inputs = pad_sequences(train_sequences, maxlen=MAX_SEQUENCE_LENGTH, padding='post')
train_labels = np.array(df_union['label'])

data_configs = {}

data_configs['vocab'] = word_vocab
data_configs['vocab_size'] = len(word_vocab)

# 학습데이터 벡터화 및 라벨
os.makedirs('./data/word_dict', exist_ok=True)
np.save(open('./data/word_dict/input.npy', 'wb'), train_inputs)
np.save(open('./data/word_dict/label.npy', 'wb'), train_labels)

# 데이터 사전을 json 형태로 저장
json.dump(data_configs, open('./data/word_dict/data_configs.json', 'w', -1, "utf-8"), ensure_ascii=False)

def tokenize(doc):
    return ['/'.join(t) for t in okt.pos(doc)]
    #return ['/'.join(t) for t in mecab.pos(doc)]

def pos_preprocessing(data, okt, remove_stopwords=False, stop_words=[]):
    data_text = re.sub("[^가-힣ㄱ-ㅎㅏ-ㅣ\\s]", "", data)
    #words = mecab.morphs(data_text)
    words = tokenize(data_text)
    if remove_stopwords:
        words = [token for token in words]

    return words

okt = Okt()

stop_words = set(['은', '는', '이', '가', '하', '아', '것',
                  '들', '의', '있', '되', '수', '보', '주',
                  '등', '한'])

docs = []

for review in tqdm(df_union['cmt_contents']):
    if type(review) == str:
        docs.append(pos_preprocessing(review, okt, remove_stopwords=False, stop_words=stop_words))
    else:
        docs.append([])

tokenizer = Tokenizer()
tokenizer.fit_on_texts(docs)
train_sequences = tokenizer.texts_to_sequences(docs)
word_vocab = tokenizer.word_index

MAX_SEQUENCE_LENGTH = 12

train_inputs = pad_sequences(train_sequences, maxlen=MAX_SEQUENCE_LENGTH, padding='post')
train_labels = np.array(df_union['label'])

data_configs = {}

data_configs['vocab'] = word_vocab
data_configs['vocab_size'] = len(word_vocab)

# 학습데이터 벡터화 및 라벨
np.save(open('./data/word_dict/pos_input.npy', 'wb'), train_inputs)
np.save(open('./data/word_dict/pos_label.npy', 'wb'), train_labels)

# 데이터 사전을 json 형태로 저장
json.dump(data_configs, open('./data/word_dict/pos_data_configs.json', 'w', -1, "utf-8"), ensure_ascii=False)

print(docs)