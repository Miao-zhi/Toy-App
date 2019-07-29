# encoding:utf-8
import os
import jieba
import gensim
from gensim import corpora
from gensim import models
from gensim import similarities
from Godzilla.setting import MONGO_DB

contents = list(MONGO_DB.Content.find({}))

# print(contents)

all_doc_list = []
for doc in contents:
    doc_list = list(jieba.cut(doc.get("title")))
    all_doc_list.append(doc_list)


# 制作语料库
dictionary = corpora.Dictionary(all_doc_list)  # 制作词袋
corpus = [dictionary.doc2bow(doc) for doc in all_doc_list]
# 将corpus语料库(初识语料库) 使用Lsi模型进行训练
lsi = models.LsiModel(corpus)
# 文本相似度
index = similarities.SparseMatrixSimilarity(lsi[corpus], num_features=len(dictionary.keys()))


def get_content(Q):
    # 将需要寻找相似度的分词列表 做成 语料库 doc_test_vec
    doc_test_list = list(jieba.cut(Q))
    doc_test_vec = dictionary.doc2bow(doc_test_list)
    sim = index[lsi[doc_test_vec]]
    # 对下标和相似度结果进行一个排序,拿出相似度最高的结果
    cc = sorted(enumerate(sim), key=lambda item: -item[1])
    content = contents[cc[0][0]]

    return content


def create_file(filepath):
    """
    没有文件则新创建
    :param filepath:  文件路径
    :return:
    """
    os.path.exists(filepath)
    if os.path.isfile(filepath):
        filepath,filename = os.path.split(filepath)

    if not os.path.isdir(filepath):
        os.makedirs(filepath)

if __name__ == '__main__':
    a = "新年"
    get_content(a)
    # print(os.path.isfile(os.path.join("Qrcode","0faab06ccd34e07c882077a5d2114b5.jpg")))
