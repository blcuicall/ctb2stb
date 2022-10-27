'''
Author: hzs
Date: 2021-03-22 10:29:49
LastEditors: hzs
LastEditTime: 2022-06-23 20:06:55
Description: 转换句本位数据(人工标注的ctb的数据 dev test)格式成短语格式（括号格式）
'''
import os
import argparse
# import xml.etree.cElementTree as ET
from xml.etree import ElementTree as etr
from xml.dom import minidom
from xml.etree.ElementTree import Element,SubElement,ElementTree


from lxml import etree
import re

# 直接提取
def extract(input_dirs,outputfile):
    # 存储xml
    tag_set = set()
    wf = open(outputfile, 'w', encoding='utf-8')
    for fi in get_all_files(input_dirs):
        with open(fi, 'r', encoding='utf-8') as rf:
            dtc_tag = ''
            consi_str = ''
            for line in rf:
                line = line.strip()
                if 'xml version="1.0"' not in line and not line.startswith('</jbw>') and not line.startswith('<jbw>'):
                    # 表示单词节点
                    if re.search(r'<.*>.*</.*>',line):
                        word = re.search(r'>(.*)<',line).groups()[0]
                        tag = re.search(r'</(.*)>',line).groups()[0]
                        if word.strip() == '(':
                            word = '（'
                        if word.strip() == ')':
                            word = '）'
                        if word == '':
                            word = '-NONE-'
                        if re.search(r'<x>.+<\/x>',line):
                            print(fi)
                        tmp_str = f' ({tag} {word})'
                        consi_str += tmp_str
                    else:
                        if line.endswith('/>'):
                            tag = re.sub(r' .*','',line)
                            tag = tag.strip('<').strip()
                            tag_set.add(tag)
                            tmp_scp = re.search(r'scp="(.+)".*/>$',line)
                            if tmp_scp:
                                print(line)
                            tmp = re.search(r'fun="(.+)".*/>$',line)
                            if tmp:
                                prop = tmp.groups()[0]
                                tag = tag + '_' + prop
                                tmp_str = f' ({tag} -NONE-)'
                            elif tmp_scp:
                                prop = tmp_scp.groups()[0]
                                tag = tag
                                tmp_str = f' ({tag} -NONE-)'
                            else:
                                tmp_str = f' ({tag} -NONE-)'
                            consi_str += tmp_str
                        elif ' ' in line:
                            fun_attri = re.search(r'fun="(.+)".*>$',line)
                            attri = re.search(r'scp="(.+)".*>$',line)
                            tmp_tag = re.sub(r' .*','',line)
                            tag = tmp_tag.strip('<').strip()
                            if attri:
                                tag = tag
                            if fun_attri:
                                tag = tag +'_' + fun_attri.groups()[0]
                            if 'mod' not in line:
                                tmp_str = ' ('+tag
                                consi_str += tmp_str
                            else:
                                dtc_tag = tag
                        # </prd>
                        elif re.search(r'<\/.*>',line):
                            tag =re.search(r'<\/(.*)>',line).groups()[0]
                            # 解决动态词
                            if re.search(r'<x><\/x>',line):
                                print(fi)
                                tmp_str = ' (x -NONE-)'
                                consi_str += tmp_str
                            elif re.search(r'<x>.+<\/x>',line):
                                print(fi)
                            elif tag != dtc_tag:
                                tmp_str = ')'
                                consi_str += tmp_str
                            else:
                                dtc_tag = ""
                        else:
                            # <sbj>
                            tag = re.search(r'<(.*)>',line).groups()[0]
                            tmp_str = ' ('+tag
                            consi_str += tmp_str
                if line == '</ju>':
                    consi_str = '(TOP' + consi_str + ')'
                    wf.write(consi_str+'\n')
                    consi_str = ''

def get_all_files(input_dir):
    for root,dirs,files in os.walk(input_dir):
        for i in sorted(files):
            yield os.path.join(root,i)
                        
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--inputdir')
    parser.add_argument('--outputfile')
    args = parser.parse_args()
    extract(args.inputdir, args.outputfile)

if __name__ == '__main__':
    main()