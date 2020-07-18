import pandas as pd
from tqdm import tqdm
import dc_api

# for multiprocessing
from multiprocessing import Pool

dc_gall_list = ['baseball_new8', 'stock_new2', 'leagueoflegends3', 'etc_entertainment3', 'ib_new1', 'history']
df = pd.DataFrame(columns=['gall_name', 'cmt_contents'])


for gall_idx in range(len(dc_gall_list)):
    for doc, idx in tqdm(zip(dc_api.board(board_id=dc_gall_list[gall_idx]), range(1000))) :
        doc["comments"]
        for com in doc["comments"]:
            if type(com["contents"]) == str:
                data = {'gall_name': dc_gall_list[gall_idx], 'cmt_contents': com["contents"]}
                df = df.append(data, ignore_index=True)
            else:
                 continue
    print(df.tail())


df.replace(to_replace=[r"\\t|\\n|\\r", "\t|\n|\r"], value=["", ""], regex=True, inplace=True)
df.to_csv('./data/dc.csv', sep=',', encoding='utf-8')