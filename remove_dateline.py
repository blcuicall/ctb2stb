'''
Author: hzs
Date: 2022-06-11 21:47:11
LastEditors: hzs
LastEditTime: 2022-06-13 19:45:52
Description: file content
'''
import argparse

from numpy import append
from pandas import concat
def process(args):
    index_list = []
    with open('./index/news_index', 'r', encoding='utf8') as rf:
        for line in rf:
            index_list.append(int(line.strip()))
    with open(args.input, 'r', encoding='utf-8') as rf:
        content_list = rf.read().strip().split('\n')
    for index, sent in enumerate(content_list):
        if index+1 not in index_list:
            print(sent)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input')
    args = parser.parse_args()
    process(args)