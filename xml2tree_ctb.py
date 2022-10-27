'''
Author: hzs
Date: 2021-03-29 21:27:40
LastEditors: hzs
LastEditTime: 2022-06-23 19:42:13
Description: 将转换完后的ctb数据(xml格式) 转成短语的格式
'''
import os
import argparse
import re

# 直接提取
def extract(input_dirs,outputfile):
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
                        tmp_str = f' ({tag} {word})'
                        consi_str += tmp_str
                    else:
                        if line.endswith('/>'):
                            if ' ' in line:
                                tag = re.sub(r' .*','', line)
                                tag = tag.strip('<').strip()
                            else:
                                tag = re.search(r'<(.*)/>', line).groups()[0]
                            tag_set.add(tag)
                            # if tag == 'sbj':
                            #     print(line)
                            tmp_scp = re.search(r'scp="(.+)".*/>$', line)
                            # if tmp_scp:
                            #     print(line)
                            tmp = re.search(r'fun="(.+)".*/>$', line)
                            if tmp:
                                prop = tmp.groups()[0]
                                tag_prop = tag +'_'+prop
                                tmp_str = f' ({tag_prop} -NONE-)'
                            elif tmp_scp:
                                prop = tmp_scp.groups()[0]
                                tag_prop = tag
                                tmp_str = f' ({tag_prop} -NONE-)'
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
                                tag = tag + '_' + fun_attri.groups()[0]

                            tmp_str = ' ('+tag
                            consi_str += tmp_str
                        elif re.search(r'<\/.*>',line):
                            tag =re.search(r'<\/(.*)>',line).groups()[0]
                            # 解决动态词
                            if tag != dtc_tag:
                                tmp_str = ')'
                                consi_str += tmp_str
                            else:
                                print('error')
                                return
                        else:
                            tag = re.search(r'<(.*)>', line).groups()[0]
                            tmp_str = ' ('+tag
                            consi_str += tmp_str
                if line == '</ju>':
                    consi_str = '(TOP' + consi_str + ')'
                    wf.write(consi_str+'\n')
                    consi_str = ''

def get_all_files(input_dir):
    for root, dirs, files in os.walk(input_dir):
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