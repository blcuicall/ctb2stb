'''
Author: hzs
Date: 2022-03-01 14:30:48
LastEditors: hzs
LastEditTime: 2022-04-28 10:13:01
Description: 词性标签设置为n
'''
from __future__ import print_function
import argparse
from cgi import print_directory
import enum
from itertools import count
from traceback import print_tb
from tree import Tree
from xml.etree import ElementTree as etree
from xml.dom import minidom
from xml.etree.ElementTree import Element,SubElement,ElementTree
import re
class Node(object):
    """
    构造节点

    """
    def __init__(self,val=None,children=None,father = None,tag=None,rel=None,level=0,flag=1):
        self.val = val
        self.children = []
        self.father = father
        self.tag = tag
        # rel记录特殊标记 如同位语
        self.rel = rel
        self.level = level
        self.flag = flag
class N_Tree(object):
    def __init__(self):
        """初始化一个空的二叉树"""
        self.root = None
        self.node_dict = {}
    def build(self,node_list):
        final = node_list[-1]
        num = final.count('| ')
        tag = final.strip().rsplit('| ',1)[-1]
        # print(tag)
        # tag = tag.lstrip('(')
        # 处理终端节点
        if tag.endswith('_terminal'):
            tag = tag.rsplit('_',1)[0]
        max_len = len(node_list)
        if (tag,max_len) not in self.node_dict:
            de = Node(tag,level=num)
        else:
            de = self.node_dict[(tag,max_len)]
        if final.endswith('_terminal'):
            de.children = None
        node_list.pop()
        node_list_len = len(node_list)
        for index,node in enumerate(node_list[::-1]):
            curr_len = node_list_len - index
            curr_num = node.count('| ')
            if curr_num == num - 1:
                parent_tag = node.strip().rsplit('| ',1)[-1]
                if (parent_tag,curr_len) not in self.node_dict:
                    parent_node = Node(parent_tag,level=curr_num)
                    self.node_dict[(parent_tag,curr_len)] = parent_node
                self.node_dict[(parent_tag,curr_len)].children.insert(0,de)
                de.father = self.node_dict[(parent_tag,curr_len)]
                break
        if len(node_list) == 1 and node_list[0].startswith('TOP'):
            return
        else:
            self.build(node_list)
    # 层序遍历
    def levelOrder(self,root):

        res = []
        cur_queue = []
        cur_queue.append(root)
        if not root:
            return res
        while len(cur_queue):
            sub = []
            for i in range(len(cur_queue)):
                current = cur_queue.pop(0)
                # print(current.val)
                if current.val == 'NP-SBJ':
                    root = Element( 'xj' )
                    sbj = SubElement(root, 'sbj' )

                sub.append(current.val)
                if current.children != None:
                    for j in current.children:
                        cur_queue.append(j)
                        # print(j.val)
            # print(sub)
            res.append(sub)
        return res
    
    def find_parent(self,node):
        return node.father
    # 寻找tag为1的父节点
    def find_father(self,node):
        node_father = node.father
        # print(node_father.tag)

        while node_father.tag != 1 :
            node_father = node_father.father
        return node_father
    # 寻找tag为1但是 不是prep的父节点
    def find_father_not_prep(self,node):
        node_father = node.father
        while node_father.tag != 1 or (node_father.tag == 1 and node_father.rel == 'prep'):
            node_father = node_father.father
        return node_father
    # 寻找tag为1但是 不是 limit 的父节点
    def find_father_not_limit(self,node,limit):
        if node.val == 'TOP':
            return node
        node_father = node.father
        # print(node_father.rel)
        while node_father.tag != 1 or (node_father.tag == 1 and node_father.rel == limit):
            node_father = node_father.father
        return node_father
    # 寻找tag为1但是 不是todo的父节点
    def find_father_not_todo(self,node):
        node_father = node.father
        while node_father.tag != 1 or (node_father.tag == 1 and node_father.rel == 'todo'):
            node_father = node_father.father
        return node_father
    # 寻找tag为1 且为 diagram或者cla的父节点
    def find_father_dia_cla(self,node):
        node_father = node.father
        print(node_father.val)
        print(node_father.father.val)
        while node_father.tag != 1 or (node_father.tag == 1 and (node_father.rel != 'dia' and node_father.rel != 'cla')):
            node_father = node_father.father
            print(node_father.val)
        return node_father
    



    # 从此节点找父节点　每个父节点都是VP 直到找到第二层的VP祖先节点　表示此节点是谓语
    def is_prd(self,node):
        node_father = node.father
        prd_flag = False
        # while node_father.val == 'VP' and node_father.children.index(node) == 0:
        while node_father.val == 'VP':
            if node_father.father.val == 'S' or node_father.father.val == 'SINV':
                prd_flag = True
                break
            else:
                node_father = node_father.father
        return prd_flag
    
    def vp_is_prd(self,node):
        # node_father = node.father
        prd_flag = False
        # while node_father.val == 'VP' and node_father.children.index(node) == 0:
        while node.val == 'VP':
            if node.father.val == 'S' or node.father.val == 'SINV':
                prd_flag = True
                break
            else:
                node = node.father
        return prd_flag


    # 先序遍历
    def preorder(self,root):
        xml_dict = {}

        if not root:
            return []

        q = [root]
        node_res = []
        sent_res = []
        num = 0
        while q:
            # 弹出列表尾部的一个元素
            node = q.pop()
            num+=1
            node_res.append(node)
            if node.children == None:
                word = node.val.rsplit('_',1)[1]
                sent_res.append(word)
            # 逆序加入，从右到左
            if node.children != None:
                for child in node.children[::-1]:
                    q.append(child)
        # xml_string = etree.tostring(root)
        # tree = minidom.parseString(xml_string)
        # print(tree.toprettyxml())
        return node_res,sent_res
    # 读取转换规则
    def read_rules(self,file_path):
        rules_dict = {}
        with open(file_path,'r',encoding = 'utf-8') as rf:
            for line in rf:
                line = line.strip()
                line_list = line.split()
                # print(line_list)
                key = line_list[:-1]
                # print(line_list[-1])
                value  = line_list[-1]
                for i in key:
                    rules_dict[i.strip()] = value
        return rules_dict
    # 读取词性规则
    def read_pos(self,file_path):
        pos_dict = {}
        with open(file_path,'r',encoding = 'utf-8') as rf:
            for line in rf:
                line = line.strip()
                line_list = line.split()
                value = line_list[-1]
                for i in line_list[:-1]:
                    pos_dict[i] = value
        return pos_dict


    def process_val(self,node):
        val = node.val
    

    # def extract_xj():
    # 找标点符号的邻居叶子节点
    def find_left_word(self,node):
        while node.children != None and node.children[-1] != None:
            node = node.children[-1]
        return node
        
    def find_left_final_node(self,node):
        while node.children != None and node.children[0] != None:
            node = node.children[0]
        return node


    # 处理标点符号，让他接在相邻的单词的后面
    def process_pu(self,node):
        if len(node.father.children) > 0:
            print(node.val)
            print('父节点',node.father.val)
            for index,cur_node in enumerate(node.father.children):
                print(cur_node.val)
                if cur_node == node:
                    # print(cur_node.val)
                    left_index = index - 1
                    # print(left_index)
                    # break
            # print(left_index)
            # print(node.val)
            if left_index >= 0:
                left_node = node.father.children[left_index]
                return left_node
            else:
                return 1


    # def rules(node):
    def find_xml_father(self,node,xml_dict):
        finded_node = self.find_father(node)
        father_xml = xml_dict[finded_node]
        return father_xml

    # 规则转换
    def rule_conversion(self,node_res,sent_res):
        # 根节点
        xml_dict = {}
        prd_list = []
        for node_index,node in enumerate(node_res):
            # print(node.val)

            # 如果非叶子节点的父节点xml为mod　则跳出该节点　mod下不在嵌套任何成分
            if xml_dict:
                father_xml = self.find_xml_father(node,xml_dict)
                if father_xml.tag == 'mod' and node.children:
                    continue
                

            if node.flag == 0:
                print("flag为0",node.val)
                # father_xml = self.find_xml_father(node,xml_dict)
                # pos_xml = SubElement(father_xml,'n')
                # if not node.children:
                #     wor = node.val.split('_')[1]
                #     pos_xml.text = wor
                continue

            # print(node.val,node.level)
            val = node.val
            lev = node.level

            
                
            


            # print(node.val)
            if val == 'TOP':
                root = Element( 'diagram' )
                node.tag = 1
                node.rel = 'dia'
                xml_dict[node] = root
            # 判断主语 
            if val == 'S' or val == 'SINV':
                # node.tag = 1
                



                # if node.children:
                childs = node.children
                val_list = [child.val if child.children else child.val.split('_')[0] for child in childs]

                # 句子并列
                yingwen_node = [w for w in val_list if not re.search(r'[^A-Za-z]',w)]
                if set(yingwen_node) == set(['S','CC']) or set(yingwen_node) == set(['SBAR','CC']):
                    father_xml = self.find_xml_father(node,xml_dict)
                    sencoo = SubElement(father_xml,'sencoo')
                    node.tag = 1
                    xml_dict[node] = sencoo
                
                    
                        
                        
                            


                if 'NP' in val_list:
                    sbj_index = val_list.index('NP')
                    childs[sbj_index].rel = 'sbj'
                elif 'S' not in val_list:
                    if val_list.count('VP') == 2:
                        sbj_index = val_list.index('VP')
                        if childs[sbj_index].children[0].val == 'VBG':
                            childs[sbj_index].children[0].rel = 'sbj'
                elif 'VP' in val_list:
                    sbj_index = val_list.index('S')
                    childs[sbj_index].rel = 'sbj'
                
            if node.rel == 'sbj':
                father_xml = self.find_xml_father(node,xml_dict)
                # 如果父节点是cla或diagra或sencoo 才新建sbj
                if father_xml.tag in ['cla','diagram','sencoo']:
                    sbj = SubElement(father_xml,'sbj')
                    # 表示是xml中的父节点
                    node.tag = 1
                    xml_dict[node] = sbj
                # node_res,sent_res = self.preorder(node)
                # word = ' '.join(sent_res)
                # sbj.set('word',word)
                # sbj.text = word
                # for node in node_res:
                #     node.flag = 0
            # 谓语 遇到VP 判断VP的tag为1的父节点是否是prd 是：直接追加 否：新建prd并tag为1
            if val == 'VP' and self.vp_is_prd(node):
                # print('11')
                # 短语并列
                childs = node.children
                val_list = [child.val if child.children else child.val.split('_')[0] for child in childs]

                # 并列
                yingwen_node = [w for w in val_list if not re.search(r'[^A-Za-z]',w)]
                # 谓语并列
                if yingwen_node == ['VP','CC','VP']:
                    father_xml = self.find_xml_father(node,xml_dict)
                    prdcoo = SubElement(father_xml,'phrcoo')
                    node.tag = 1
                    xml_dict[node] = prdcoo
                # for ch in node.chilren:
                #     if not ch.children:
                #         if not re.search(r'[^A-Za-z]',ch.val)]:

                        
                # yingwen_node = [w for w in val_list if not re.search(r'[^A-Za-z]',w)]
                # val_list = [child.val if child.children else child.val.split('_')[0] for child in childs]
                # cc_index = False
                # for index,i in enumerate(childs):
                #     if not i.children and i.val.split('_')[0] == 'CC':
                #         cc_index == index
                # if cc_index:
                #     if childs[cc_index-1].val == 'VP' and childs[cc_index + 1].val == 'VP':
                #         father_xml = self.find_xml_father(node,xml_dict)
                #         prdcoo = SubElement(father_xml,'phrcoo')
                #         node.tag = 1
                #         xml_dict[node] = prdcoo
                    
                # 伴随状语　advcla
                if node.father.val == 'S':
                    childs = node.children
                    # 孩子节点的值
                    val_list = [child.val if child.children else child.val.split('_')[0] for child in childs]
                    if 'VBG' in val_list or 'VBN' in val_list:
                        if 'VBG' in val_list:
                            vbg_index = val_list.index('VBG')
                        if 'VBN' in val_list:
                            vbg_index = val_list.index('VBN')
                        if vbg_index+1 < len(node.children):
                            bro_val = node.children[vbg_index + 1].val
                            if bro_val == 'PP' or bro_val == 'SBAR':
                                father_xml = self.find_xml_father(node,xml_dict)
                                # if father_xml.tag == 'diagram':
                                if father_xml.tag == 'prd':
                                    father = self.find_father_not_limit(node,'prd')
                                    father_xml = xml_dict[father]
                                advcla = SubElement(father_xml,'advcla')
                                node.tag = 1
                                node.rel = 'advcla'
                                xml_dict[node] = advcla
                            
                
                        


                # 谓语
                for i in node.children:
                    if not i.children:
                        pos,word = i.val.split('_')
                        if pos in ['VBP', 'VBD', 'VBZ', 'VBN', 'MD', 'VB']:
                            father_xml = self.find_xml_father(node,xml_dict)
                            # 如果父节点不是prd 不是todo 才新建
                            # if father_xml.tag != 'prd' and father_xml.tag != 'todo':
                            print("father_xml",father_xml.tag)
                            if father_xml.tag in ['diagram','cla','sencoo']:
                                prd = SubElement(father_xml,'prd')
                                node.tag = 1
                                xml_dict[node] = prd
                                print('11111111111')

                                # 可能有问题
                                node.rel = 'prd'
                            # 有问题
                            if father_xml.tag == 'prd' and node.father.val != 'VP':
                                print('谓语是')
                                father = self.find_father_not_limit(node,'prd')
                                father_xml = xml_dict[father]
                                prd = SubElement(father_xml,'prd')
                                node.tag = 1
                                xml_dict[node] = prd
                                node.rel = 'prd'
                                # print('11111')
                            # else:
                            #     father = self.find_father_not_prep(node)
                            #     xml_dict[father]
                               
                  
                
            #第二层的　ADJP RB PRN PRT-RP 为修饰 mod 先判断父节点是否是mod如果是mod则不考虑该节点
            if node.val in ['ADJP','RB','PRN','PRT-RP'] and lev == 2:
                father_xml = self.find_xml_father(node,xml_dict)
                mod = SubElement(father_xml,'mod')
                node.tag = 1
                node.rel = 'mod'
                xml_dict[node] = mod
                # node_res,sent_res = self.preorder(node)
                # word = ' '.join(sent_res)
                # mod.set('word',word)
                # sbj.text = word
                # for node in node_res:
                #     node.flag = 0
                

            # 从句
            if val == 'SBAR':
                father_xml = self.find_xml_father(node,xml_dict)
                # # if father_xml.tag == 'diagram':
                # cla = SubElement(father_xml,'cla')
                # node.tag = 1
                # xml_dict[node] = cla
                # del xml_dict['prd']
                # prd_list = []
                print('2222222')
                father_xml = self.find_xml_father(node,xml_dict)
                # if father_xml.tag == 'diagram':
                if father_xml.tag in ['cla','diagram','todo','prep','pred','sbj','obj']:
                    cla = SubElement(father_xml,'cla')
                    node.tag = 1
                    # node.tag = 'cla'
                    node.rel = 'cla'
                    xml_dict[node] = cla
                    print('11111')
                # cla如果在prd里 则要提取到外层
                if father_xml.tag == 'prd':
                    father = self.find_father_not_limit(node,'prd')
                    father_xml = xml_dict[father]
                    cla = SubElement(father_xml,'cla')
                    node.tag = 1
                    # node.tag = 'cla'
                    node.rel = 'cla'
                    xml_dict[node] = cla
                # if father_xml.tag == 'prep':
                #     father_node = self.find_father_not_prep(node)
                #     father_xml = xml_dict[father_node]
                #     # if father_xml.tag == 'prd':
                #     #     father_xml = self.find_father_not_limit(node,'prd')
                #     if father_xml.tag in ['cla','diagram','todo','prep','pred','sbj']:
                #         cla = SubElement(father_xml,'cla')
                #         node.tag = 1
                #         node.rel = 'cla'
                #         xml_dict[node] = cla
                #     # 如果SBAR嵌套在PP中则当做advcla修饰
                #     # advcla = SubElement(father_xml,'advcla')
                #     # 表示是xml中的父节点
                #     # node.tag = 1
                #     # xml_dict[node] = advcla

                #     # node_res,sent_res = self.preorder(node)
                #     # word = ' '.join(sent_res)
                #     # advcla.set('word',word)
                #     # for node in node_res:
                #     #     node.flag = 0
                    
                # else:
                    
                #     father_xml = self.find_xml_father(node,xml_dict)
                #     # if father_xml.tag == 'diagram':
                #     if father_xml.tag in ['cla','diagram','todo','prep','pred','sbj']:
                #         cla = SubElement(father_xml,'cla')
                #         node.tag = 1
                #         # node.tag = 'cla'
                #         node.rel = 'cla'
                #         xml_dict[node] = cla
                #         print('11111')
                #     # if 'prd' in xml_dict:
                #     #     del xml_dict['prd']
                #     #     prd_list = []
            if val == 'ADVP':
                prd_index = False
                for index,i in enumerate(node.father.children):
                    if i.val == 'MD':
                        prd_index = index
                        break
                    if i.val == 'VBD':
                        prd_index = index
                if prd_index and self.is_prd(node.father.children[prd_index]):
                    father_xml = self.find_xml_father(node,xml_dict)
                    mod = SubElement(father_xml,'mod')
                    


                
            # 叶子节点
            if not node.children:
                pos,word = node.val.split('_')
                # if node_index+1 < len(node_res) and not node_res[node_index+1].children:
                #     next_pos,next_word = node_res[node_index+1].val.split('_')
                # # print(node.val.split('_'))
                # # 处理标点符号紧接前一个单词
                #     if next_pos in ["''",",","-LRB-",'-RRB-',".",":","``"]:
                #         word += next_word
                #         node_res[node_index+1].flag = 0
                father_xml = self.find_xml_father(node,xml_dict)
                if pos in ['VBP', 'VBD', 'VBZ', 'VBN', 'MD', 'VB', 'VBG']:
                    if node.father.val == 'VP' and self.vp_is_prd(node.father):
                        father_xml = self.find_xml_father(node,xml_dict)
                        # 兄弟节点
                        bro_child = [j.val if j else j.val.split('_')[0] for j in node.father.children]
                        for j in node.father.children:
                            if j!=node:
                                if j:
                                    bro_child.append(j)
                                else:
                                    bro_child.append(j.val.split('_')[0])
                        if pos == 'VBG' and len(set(bro_child)&{'VB','VBG','VBD','VBZ','VBN','MD','VBP'}) ==0:
                            father = self.find_father_not_limit(node,'prd')
                            father_xml = xml_dict[father]
                        
                        # print(father_xml.text)
                        pos_xml = SubElement(father_xml,'n')
                        pos_xml.text = word
                        # if not father_xml.text:
                        #     father_xml.text == word
                        # else:
                        #     father_xml.text += word
                        # 记录该节点是谓语词
                        # print('222222')
                        node.rel = 'prd'
                    else:
                        print('单词',node.val)
                        # father_xml = self.find_father_not_limit(node,'prd')
                        father = self.find_father_not_limit(node,'prd')
                        father_xml = xml_dict[father]
                        # father_xml = self.find_xml_father(node,xml_dict)
                        # print(father_xml.text)
                        pos_xml = SubElement(father_xml,'n')
                        pos_xml.text = word
                    # prd_flag = self.is_prd(node)
                    # if prd_flag and node.father.children.index(node) == 0:
                    # if prd_flag:
                        
                        # father_xml = self.find_xml_father(node,xml_dict)
                        # 判断father_xml 是否是prd
                        # father_xml.text += word
                # 谓语中的修饰
                elif pos == 'RB':
                    father_xml = self.find_xml_father(node,xml_dict)
                    if father_xml.tag == 'cla':
                        mod = SubElement(father_xml,'wh')
                        pos_xml = SubElement(mod,'n')
                        pos_xml.text = word
                    else:
                    

                        prd_index = -1
                        # 谓语外的mod
                        out_prd_index = False
                        # RB的父节点是ADVP ADVP父节点是Ｓ ADVP的右兄弟节点是ＶP　VP的第一个孩子词性是谓语
                        if node.father.val == 'ADVP' and node.father.father.val == 'S':
                            advp_index = node.father.father.children.index(node.father)
                            if advp_index+1 < len(node.father.father.children):
                                advp_index_bro = node.father.father.children[advp_index+1]
                                if advp_index_bro.val == 'VP' and not advp_index_bro.children[0].children:
                                    pos,_ = advp_index_bro.children[0].val.split('_')
                                    if pos in ['VBP', 'VBD', 'VBZ', 'VBN', 'MD', 'VB', 'VBG']:
                                        out_prd_index= True
                        if node.father.val == 'ADVP' and node_index+1<len(node_res) and node_res[node_index+1].val == 'VP' and self.vp_is_prd(node_res[node_index+1]):
                            if not node_res[node_index+2].children:
                                tm_pos = node_res[node_index+2].val.split('_')[0]
                                if tm_pos in ['VBP', 'VBD', 'VBZ', 'VBN', 'MD', 'VB', 'VBG']:
                                    out_prd_index= True
                        # ADVP-RB
                        # elif node.father.val == 'ADVP':
                        #     out_prd_index = True
                            

                        
                        
                        for index,i in enumerate(node.father.children):
                            if not i.children:
                                pos,_ = i.val.split('_')
                                if pos == 'MD':
                                    prd_index = index
                                    break
                                if pos == 'VBD':
                                    prd_index = index
                                    # print(prd_index)
                        # if prd_index and self.is_prd(node.father.children[prd_index]):
                        # print(node.father.children[prd_index].rel)
                        if prd_index!=-1 and node.father.children[prd_index].rel == 'prd':
                            # print('111111')
                            father_xml = self.find_xml_father(node,xml_dict)
                            mod = SubElement(father_xml,'mod')
                            pos_xml = SubElement(mod,'n')
                            pos_xml.text = word
                        else:
                            
                                
                            
                            father_xml = self.find_xml_father(node,xml_dict)
                            # father_xml.tail = word
                            if re.search(r'[^A-Za-z]',pos):
                                pos = 'w'
                            if out_prd_index:
                                mod = SubElement(father_xml,'mod')
                                pos_xml = SubElement(mod,'n')
                                pos_xml.text = word
                            else:
                                # RB
                                if father_xml.tag == 'prd':
                                    father = self.find_father_not_limit(node,'prd')
                                    father_xml = xml_dict[father]
                                pos_xml = SubElement(father_xml,'n')
                                pos_xml.text = word
                            
                        # mod.text = word
                    # bro_node = [i.val for i in node.father.children]
                    # if 'MD' in bro_node or 'VBD' in bro_node:
                elif pos == 'IN' and father_xml.tag == 'cla':
                    
                    IN = SubElement(father_xml,'wh')
                    pos_xml = SubElement(IN,'n')
                    pos_xml.text = word
                
                elif pos == 'CC' and node.level == 2:
                    childs = node.father.children
                    val_list = [child.val if child.children else child.val.split('_')[0] for child in childs]

                    # 句子并列
                    yingwen_node = [w for w in val_list if not re.search(r'[^A-Za-z]',w)]
                    # 如果同一层没有S
                    if 'S' not in yingwen_node:
                        father_xml = self.find_xml_father(node,xml_dict)
                        sencoo = SubElement(father_xml,'sencoo')
                        # sencoo.text = word
                        # pos_xml = SubElement(sencoo,'n')
                        pos_xml = SubElement(sencoo,'cc')
                        new_pos_xml = SubElement(pos_xml,'n')
                        new_pos_xml.text = word
                    else:
                        # 除了S外还有其他节点
                        if set(yingwen_node) - set(['S']):
                            father_xml = self.find_xml_father(node,xml_dict)
                            sencoo = SubElement(father_xml,'sencoo')
                            # sencoo.text = word
                            # pos_xml = SubElement(sencoo,'n')
                            pos_xml = SubElement(sencoo,'cc')
                            new_pos_xml = SubElement(pos_xml,'n')
                            new_pos_xml.text = word
                        else:

                            father_xml = self.find_xml_father(node,xml_dict)
                            if father_xml.tag != 'sbj' and father_xml.tag != 'pred' and father_xml.tag != 'prep':
                                pos_xml = SubElement(father_xml,'cc')
                                new_pos_xml = SubElement(pos_xml,'n')
                                new_pos_xml.text = word
                            
                elif pos == 'CC' and node.level != 2:
                    father_xml = self.find_xml_father(node,xml_dict)
                    if father_xml.tag != 'sbj' and father_xml.tag != 'pred' and father_xml.tag != 'prep':
                        pos_xml = SubElement(father_xml,'cc')
                        new_pos_xml = SubElement(pos_xml,'n')
                        new_pos_xml.text = word
                    else:
                        pos_xml = SubElement(father_xml,'n')
                        pos_xml.text = word
                # elif word == 'which':
                #     father_xml = self.find_xml_father(node,xml_dict)
                #     which = SubElement(father_xml,'which')
                #     pos_xml = SubElement(which,'n')
                #     pos_xml.text = 'word'


                else:
                    # print('node的ｒｅｌ',node.rel)
                    # if not node.rel:
                    #     father_xml = self.find_father_not_limit(node,'prd')

                    father_xml = self.find_xml_father(node,xml_dict)
                    # 词节点不是谓语
                    if father_xml.tag == 'prd':
                        father = self.find_father_not_limit(node,'prd')
                        father_xml = xml_dict[father]
                    # father_xml.tail = word
                    if re.search(r'[^A-Za-z]',pos):
                        pos = 'w'
                    pos_xml = SubElement(father_xml,'n')
                    pos_xml.text = word

                    # # 解决标点问题 让其紧跟在前一个词语后面
                    # if node_index+1 < len(node_res) and not node_res[node_index+1].children:
                    #     next_pos,next_word = node_res[node_index+1].val.split('_')
                    #     # print(node.val.split('_'))
                    #     # 处理标点符号紧接前一个单词
                    #     if next_pos in ["''",",","-LRB-",'-RRB-',".",":","``"]:
                    #         # word += next_word
                    #         print("标点",next_pos)
                    #         node_res[node_index+1].flag = 0
                    #         pos_xml = SubElement(father_xml,'n')
                    #         pos_xml.text = next_word
                # print("叶子节点",node.val)
                if node.val == 'VB_rise':
                    print('最后一个叶子节点')
                    print(node_index)
                    print(len(node_res))
                # 解决标点问题 让其紧跟在前一个词语后面
                if node_index+1 < len(node_res) and not node_res[node_index+1].children:
                    next_pos,next_word = node_res[node_index+1].val.split('_')
                    # print(node.val.split('_'))
                    print("标点",word)
                    # 处理标点符号紧接前一个单词
                    if next_pos in ["''",",","-LRB-",'-RRB-',".",":","``"]:
                        # word += next_word
                        print("标点",next_pos)
                        node_res[node_index+1].flag = 0
                        pos_xml = SubElement(father_xml,'n')
                        pos_xml.text = next_word



                    if word == 'while':
                        print('father_xml:',father_xml.tag)

                        # if 'prd' not in xml_dict:
                             
                        #     father_xml = self.find_xml_father(node,xml_dict)
                        #     prd = SubElement(father_xml,'prd')
                        #     prd.set('word',word)
                        #     xml_dict['prd'] =prd
                        #     prd_list.append(node)
                        # else:
                        #     # father_xml = self.find_xml_father(node,xml_dict)
                        #     # if father_xml.tag == 'prep':
                        #     #     # xml_dict['prd'] = []
                        #     #     prd = SubElement(father_xml,'prd')
                        #     #     prd.set('word',word)
                        #     #     xml_dict['prd'] =prd
                                
                            
                        #         # del xml_dict['prd']

                        #     prd = xml_dict['prd']
                        #     org_word = prd.get('word')
                        #     word = org_word + ' ' +word
                        #     prd.set('word',word)
                        #     prd_list.append(node)
                #动词不定式规则
                # if pos == '' 
            # print('2222222')
            # 宾语
            if node.val == 'NP':
                father_xml = self.find_xml_father(node,xml_dict)
                # 宾语父节点xml必须是diagram 从句里的宾语不再转换
                # if father_xml.tag == 'diagram':
                # print(node.val)
                cur_index = node.father.children.index(node)
                if cur_index == 1:
                    left_bro = node.father.children[0]

                    if not left_bro.children and node == node.father.children[1]:
                        pos,word = left_bro.val.split('_')
                        print("谓语词",word)
                        # 直接宾语 直接宾语下不再嵌套细分
                        # 如果左兄弟节点是谓语且符合筛选的单词
                        if (left_bro.rel == 'prd' and word not in ['was','were','is','are','am'] and node_res[node_index +1].val != 'NP'):
                            print('进入条件')
                            father_xml = self.find_xml_father(node,xml_dict)
                            print("父节点标签",father_xml.tag)
                            node_res_sub,sent_res = self.preorder(node)
                            # if 'about' in sent_res:
                            #     obj  = SubElement(father_xml,'mod')
                            # else:
                            if father_xml.tag == 'prd':
                                print('进入下一循环')
                                father = self.find_father_not_limit(node,'prd')
                                father_xml = xml_dict[father]
                            if father_xml.tag in ['cla','diagram']:
                            
                                obj = SubElement(father_xml,'obj')
                                # 表示是xml中的父节点
                                node.tag = 1
                                xml_dict[node] = obj
                                node.rel = 'obj'
                                # childs = node.children
                                val_list = [child.val if child.children else child.val.split('_')[0] for child in node_res]
                                if 'SBAR' not in val_list:
                                    for nod in node_res_sub:
                                        if not nod.children:
                                            pos_xml = SubElement(obj,'n')
                                            pos_xml.text = nod.val.split('_')[1]
                                    # word = ' '.join(sent_res)
                                    # obj.text = word
                                    for node in node_res_sub:
                                        node.flag = 0
                if cur_index == 0:
                    if node.father.val == 'NP':
                        np_tmp_index = node.father.father.children.index(node.father)
                        if np_tmp_index > 0:
                            tmp_left = node.father.father.children[np_tmp_index -1]
                            if tmp_left.rel == 'prd' and word not in ['was','were','is','are','am']:
                                print('进入条件')
                                father_xml = self.find_xml_father(node,xml_dict)
                                print("父节点标签",father_xml.tag)
                                node_res_sub,sent_res = self.preorder(node)
                                # if 'about' in sent_res:
                                #     obj  = SubElement(father_xml,'mod')
                                # else:
                                if father_xml.tag == 'prd':
                                    print('进入下一循环')
                                    father = self.find_father_not_limit(node,'prd')
                                    father_xml = xml_dict[father]
                                if father_xml.tag in ['cla','diagram']:
                                
                                    obj = SubElement(father_xml,'obj')
                                    # 表示是xml中的父节点
                                    node.tag = 1
                                    xml_dict[node] = obj
                                    node.rel = 'obj'
                                    # childs = node.children
                                    val_list = [child.val if child.children else child.val.split('_')[0] for child in node_res]
                                    if 'SBAR' not in val_list:
                                        for nod in node_res_sub:
                                            if not nod.children:
                                                pos_xml = SubElement(obj,'n')
                                                pos_xml.text = nod.val.split('_')[1]
                                        # word = ' '.join(sent_res)
                                        # obj.text = word
                                        for node in node_res_sub:
                                            node.flag = 0

                #短语并列 第三层NP（主语、宾语、表语下的并列）下孩子节点NP+CC+NP
                if node.level == 3:
                    childs = node.children
                    # val_list = [child.val if child.children else child.val.split('_')[0] for child in childs]
                    cc_index = False
                    for index,i in enumerate(childs):
                        if not i.children and i.val.split('_')[0] == 'CC':
                            cc_index == index
                    if cc_index:
                        if childs[cc_index-1].val == 'VP' and childs[cc_index + 1].val == 'VP':
                            father_xml = self.find_xml_father(node,xml_dict)
                            prdcoo = SubElement(father_xml,'phrcoo')
                            node.tag = 1
                            xml_dict[node] = prdcoo


                            
                            
                    # 间接宾语内部不再嵌套
                    if cc_index == 2:
                        left_first_bro = node.father.children[0]
                        left_sec_bro = node.father.children[1]
                        # if self.is_prd(left_first_bro) and self.is_prd(left_sec_bro) and left_first_bro.father.children.index(node) == 0:
                        if left_first_bro.rel == 'prd':
                            father_xml = self.find_xml_father(node,xml_dict)
                            if father_xml.tag == 'prd':
                                father = self.find_father_not_limit(node,'prd')
                                father_xml = xml_dict[father]
                            if father_xml.tag in ['cla','diagram']:
                                lobj = SubElement(father_xml,'iobj')
                                # 表示是xml中的父节点
                                node.tag = 1
                                xml_dict[node] = lobj

                            node_res,sent_res = self.preorder(node)
                            # word = ' '.join(sent_res)
                            # lobj.text = word
                            for nod in node_res:
                                if not nod.children:
                                    pos_xml = SubElement(obj,'n')
                                    pos_xml.text = nod.val.split('_')[1]
                            for node in node_res:
                                node.flag = 0
            
            
            # print('node_val1',node.val)
            # 介词短语
            if node.val == 'PP':
                # 叶子节点
                childs_list = [i.val.split('_')[0] for i in node.children if (not i.children)]
                if 'IN' in childs_list or 'TO' in childs_list:
                    father_xml = self.find_xml_father(node,xml_dict)
                    if father_xml.tag != 'prep':
                        # 如果父节点不是prep 是prd prd提取到外层
                        if father_xml.tag == 'prd':
                            print('prd符合')
                            father = self.find_father_not_limit(node,'prd')
                            father_xml = xml_dict[father]
                            print(father_xml.tag)
                        if father_xml.tag == 'obj':
                            print('*'*20)
                            print('prd符合宾语')
                            
                            father = self.find_father_not_limit(node,'obj')
                            father_xml = xml_dict[father]
                            if father_xml.tag == 'prd':
                                father = self.find_father_not_limit(father,'prd')
                                father_xml = xml_dict[father]
                            print(father_xml.tag)
                            print('*'*20)
                        # 如果介词短语在sbj下或者pred 则忽略 sbj、pred下只考虑从句
                        # if father_xml.tag not in ['sbj','pred','obj','lobj']:
                        # prep只可能在todo cla diagram下
                        if father_xml.tag in ['todo','cla','diagram','advcla']:
                            prep = SubElement(father_xml,'prep')
                            node.tag = 1
                            node.rel = 'prep'
                            xml_dict[node] = prep

                    else:
                        # 如果父节点是 prep 则找tag为1且rel不为prep的祖先节点 
                        # 如果PP-IN 里面嵌套 PP-IN 则忽略这个PP-IN 
                        if 'IN' not in childs_list:
                            father = self.find_father_not_prep(node)
                            print('father:',father.val)
                            # prep可能嵌套在prd内 sent56
                            # 如果father是TOP 直接返回TOP
                            father = self.find_father_not_limit(father,'prd')
                            father_xml = xml_dict[father]


                            # father_xml = xml_dict[father]
                            if father_xml.tag in ['todo','cla','diagram','advcla']:
                                prep = SubElement(father_xml,'prep')
                                node.tag = 1
                                node.rel = 'prep'
                                xml_dict[node] = prep
                        
                        # tag_father = self.find_father(node)
                        # father_xml = self.find_xml_father(node,xml_dict)
                
                #从句 PP-VBG PP下不只有一个孩子节点　则该PP是伴随状语
                elif 'VBG' in childs_list:
                    father_xml = self.find_xml_father(node,xml_dict)
                    # if father_xml.tag == 'diagram':
                    if father_xml.tag == 'prd':
                        father = self.find_father_not_limit(node,'prd')
                        father_xml = xml_dict[father]
                    if len(node.father.children)>1:

                        advcla = SubElement(father_xml,'advcla')
                        node.tag = 1
                        xml_dict[node] = advcla

                # print('node_val1',node.val)
                # father_xml = self.find_xml_father(node,xml_dict)
                # print('node_val12',node.val)
                # # 介词短语父节点xml必须是diagram 从句里的宾语不再转换
                # if father_xml.tag == 'diagram':
                #     print('node_val13',node.val)
                #     pp_flag = 0
                #     node_res,sent_res = self.preorder(node)
                #     for index,no in enumerate(node_res):
                #         if no.val == 'SBAR':
                #             pp_flag = 1
                #             pp_index = index
                #     print('node_val14',node.val)
                #     if pp_flag==1:
                #         pp_word_list = node_res[:pp_index]
                #         pp_word = [no.val for no in pp_word_list if not no.children]
                        
                #         father_xml = self.find_xml_father(node,xml_dict)
                #         if node.children[0].children==None and node.children[0].val.split('_')[0] == 'TO':
                #             prep = SubElement(father_xml,'todo')
                #         else:
                #             prep = SubElement(father_xml,'prep')
                        
                #         # 表示是xml中的父节点
                #         node.tag = 1
                #         xml_dict[node] = prep
                #         prep.set('word',' '.join(pp_word))
                #         for no in pp_word_list:
                #             no.flag = 0
                #         print('node_val',node.val)

                #     else:
                #         print('node_valqq',node.val)
                #         father_xml = self.find_xml_father(node,xml_dict)
                #         # print(index)
                #         print('node_valqq',node.val)
                #         # print(val)
                #         print(node.children[0].children)
                #         if node.children[0].children==None:
                #             print(node.children[0].val.split('_')[0])
                #         if node.children[0].children==None and node.children[0].val.split('_')[0] == 'TO':
                #             prep = SubElement(father_xml,'todo')
                #         else:
                #             prep = SubElement(father_xml,'prep')
                        
                #         # 表示是xml中的父节点
                #         node.tag = 1
                #         xml_dict[node] = prep
                #         prep.set('word',' '.join(sent_res))

                #         # node_res,sent_res = self.preorder(node)
                #         # word = ' '.join(sent_res)
                #         # lobj.set('word',word)
                #         for node in node_res:
                #             node.flag = 0
            #动词不定式 S-VP-TO
            # 如果ADJP嵌套在todo里面如果处理 并列还是嵌套
            if node.val == 'ADJP' and node.father.val == 'S' and len(node.children) == 2 and not node.children[0].children and node.children[0].val.split('_')[0]=='JJ':
                if node.children[1].val == 'S' and len(node.children[1].children)==1  and node.children[1].children[0] == 'VP' and not node.children[1].children[0].children[0].children and node.children[1].children[0].children[0].split('_')[0] == 'TO':
                    father_xml = self.find_xml_father(node,xml_dict)
                    # if father_xml.tag not in ['sbj','pred','obj','lobj']:
                    # 如果todo的外层是prd 则提取到上一层
                    if father_xml.tag == 'prd':
                        father = self.find_father_not_limit(node,'prd')
                        father_xml = xml_dict[father]
                    # todo 只会嵌套在cla diagram中
                    if father_xml.tag in ['cla','diagram']:
                        todo = SubElement(father_xml,'todo')
                        node.tag = 1
                        node.rel = 'todo'
                        xml_dict[node] = todo
            if node.val == 'VP' and node.father.val == 'S' and (not node.children[0].children):
                pos ,word = node.children[0].val.split('_')
                if pos == 'TO':
                    father_xml = self.find_xml_father(node,xml_dict)
                    # TO dO 不嵌套在任何标签里面 属于最外层结构 
                    if father_xml.tag != 'todo':
                        if father_xml.tag == 'diagram' or father_xml.tag == 'cla':

                            todo = SubElement(father_xml,'todo')
                            node.tag = 1
                            node.rel = 'todo'
                            xml_dict[node] = todo
                        else:
                            # print(father_xml.tag)
                            father = self.find_father_dia_cla(node)
                            # print(father.val)
                            father_xml = xml_dict[father]
                            # print(father_xml.tag)
                            todo = SubElement(father_xml,'todo')
                            node.tag = 1
                            node.rel = 'todo'
                            xml_dict[node] = todo
                    else:
                        print('22222222222')
                        father = self.find_father_not_todo(node)
                        # print(father)
                        print(xml_dict[father].tag)
                        father = self.find_father_not_limit(father,'prd')
                        if father.val !='ADJP':
                            father_xml = xml_dict[father]
                            todo = SubElement(father_xml,'todo')
                            node.tag = 1
                            node.rel = 'todo'
                            xml_dict[node] = todo
            if node.val == 'S' and node.children[0].val == 'VP' and node.father.children[0].rel == 'prd' and not node.father.children[0].children and node.father.children[0].val.split('_')[1] in ['VBD','VBN']:
                
                if len(node.children[0].children) == 1 or (len(node.children[0].children)>1 and node.children[0].children[1].val == 'NP') and not node.children[0].children[0].children:
                    pos ,word = node.children[0].children[0].val.split('_')
                    if pos == 'VBG':
                        father_xml = self.find_xml_father(node,xml_dict)
                        todo = SubElement(father_xml,'todo')
                        node.tag = 1
                        node.rel = 'todo'
                        xml_dict[node] = todo
                # if len(node.children[0].children)>1 and node.children[0].children[1].val == 'NP':
            if node.val == 'S' and len(node.children) == 1 and node.children[0].val == 'VP' and len(node.children[0].children) ==1 and (not node.children[0].children[0].children) and node.children[0].children[0].val.split('_')[0] == 'NN':
                father_xml = self.find_xml_father(node,xml_dict)
                todo = SubElement(father_xml,'todo')
                node.tag = 1
                node.rel = 'todo'
                xml_dict[node] = todo

            #表语 
            if (node.val == 'ADJP' and len(node.children) == 1 and not node.children and node.children[0].val.split('_')[0] == 'JJ') or node.val == 'NP' or (node.val == 'ADVP' and not node.children[0].children and node.children[0].val.split('_')[0] != 'RB'):
                print("fdaed",node.children[0].val)
                childs = node.father.children
                cur_index = [index for index,i in enumerate(childs) if i == node]
                left_index = cur_index[0] -1
                if childs[left_index].rel == 'prd' and not childs[left_index].children and childs[left_index].val.split('_')[1] in ['was','were','is','are','am','has','have','had','been','will','could','might','be']:
                    father_xml = self.find_xml_father(node,xml_dict)
                    print('father_xml',father_xml.tag)
                    if father_xml.tag == 'prd':
                        father_node = self.find_father_not_limit(node,'prd')
                        father_xml = xml_dict[father_node]
                        print('father_xml',father_xml.tag)
                    if father_xml.tag in ['cla','diagram']:
                        pred = SubElement(father_xml,'pred')
                        xml_dict[node] = pred
                        node.tag = 1
            # wh WHNP标签
            if node.val == 'WHNP':
                father_xml = self.find_xml_father(node,xml_dict)
                if father_xml.tag == 'cla':
                    wh = SubElement(father_xml,'wh')
                    node.tag = 1
                    # node.rel = 'todo'
                    xml_dict[node] = wh



                    
                        
                        
                

               


                            
                    
                            
                
                
            
        xml_string = etree.tostring(root)
        # print(xml_string)
        tree = minidom.parseString(xml_string)
        # print(tree.toprettyxml())
        return tree.toprettyxml()        
                            

                        

                
            # 表示从句
            # if (val == 'S' and lev > 1) or (val == 'SBAR' and lev > 1):


                
            
            

        
        
def read_input(input_file):
    with open(input_file,'r',encoding = 'utf-8') as rf:
        content_list = rf.read().strip().split('\n\n')
        



    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--i')
    args = parser.parse_args()
    # rf = open('句本位转换/data/ctb7_tree.txt', "r", encoding='utf-8')
    rf = open('02-21.10way.clean_tree', "r", encoding='utf-8')
    # 22.auto.clean_tree
    # 02-21.10way.clean_tree
    # rf = open('02-21.10way.clean_tree', "r", encoding='utf-8')
    # rf = open('01_test.txt', "r", encoding='utf-8')
    # rf = open('句本位转换/data/tree_test12.txt', "r", encoding='utf-8')
    # rf = open('句本位转换/data/test_data/test', "r", encoding='utf-8')
    sent_list = rf.read().strip().split('\n\n')
    for index,sent in enumerate(sent_list):
        # if index>-1:
        # if index == 297 :
        # if index == 55 or index == 21 or index==1:
        # if index == 748:
        # if index == 677:
        # if index == 20: #宾语
        # if index == 22:
        # if index == 7:
        # print('1111111')
        # if index == 79:
        # if index == 56:
        if index > -1:
            # print(sent)
            tree = N_Tree()
            node_list = sent.split('\n')
            # print(node_list)
            tree.build(node_list)
            # print(tree.node_dict)
            tree.root = tree.node_dict[('TOP',1)]
        
            node_res,sent_res = tree.preorder(tree.root)
            print(sent_res)

            # for i in node_res:
            #     print(i.val)
            index = str(index+1).zfill(5)
            xml = tree.rule_conversion(node_res,sent_res,index)
            save_file = 'xml/0_21xml_7/' + index + '.xml'


            new_xml_list = [i for i in xml.strip().split('\n') if not i.strip().endswith('/>')]
            
            new_xml = '\n'.join(new_xml_list)
            # print(xml)
            # save_file = '句本位转换/data/ctb_5.1_gold_to_jbw_xml_7/train_xml/' + index +  '.xml'
            with open(save_file,'w',encoding = 'utf-8') as wf:
                wf.write(new_xml)
            

        # print(jbw_xml)
        
        # for i in pre_res:
        #     print(i)
        # for re in res:
        #     print(' '.join(re))
