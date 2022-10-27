#!/usr/bin/env bash
set -e

# 生成层次结构
python tree.py -i ./sample_data/demo.ctb.trees --pp true > ./sample_data/demo.ctb.hier

# 将短语结构树库转换为句式结构树库
python ctb2stb.py --inputfile ./sample_data/demo.ctb.hier --outputdir ./sample_data/xml/

# 将xml格式转换为嵌套括号形式
python xml2tree_ctb.py --inputdir ./sample_data/xml/ --outputfile ./sample_data/demo.ctb.txt

# 处理None节点以及PVT、APP、COO、SYN、UNI等句法结构的位置
python process_tree_jbw.py --input ./sample_data/demo.ctb.txt > ./sample_data/demo.ctb.modi.txt

# 去除新闻电头文件
python remove_dateline.py --input ./sample_data/demo.ctb.modi.txt > ./sample_data/demo.ctb.modi.process.txt

