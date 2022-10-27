#生成短语树的层次结构文件
python tree.py -i /PATH/to/your/file/pos --pp true > /PATH/to/your/file/tree

#树库转换
python ctb2jbw.py --inputfile /PATH/to/your/file/tree --outputdir /PATH/to/your/xml/file/

#将xml文件转换为短语嵌套括号的形式
python convert_jbw2constitency_ctb.py --inputdir /PATH/to/your/xml/file/ --outputfile /PATH/to/your/result.txt

#处理None节点以及PVT、APP、COO、SYN、UNI等句法结构的位置
python process_tree_jbw.py --input /PATH/to/your/result.txt > /PATH/to/your/result.modi.txt

#去除新闻电头文件
python code_2022/code/get_data.py --input /PATH/to/your/result.modi.txt > /PATH/to/your/result.modi.process.txt

