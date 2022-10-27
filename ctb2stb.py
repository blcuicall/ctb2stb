'''
Author: hzs
Date: 2021-12-16 08:38:33
LastEditors: hzs
LastEditTime: 2022-06-14 10:57:55
Description: 拷贝jbw_new_add_jbwtag.py 规则列表删除了att对应的ADJP 添加<jbw> <ju id=''>标签
添加了状语adv的其他规则
重新定义小句
'''
import argparse
from tkinter import N
#from tree import Tree
from xml.etree import ElementTree as etree
from xml.dom import minidom
from xml.etree.ElementTree import Element,SubElement,ElementTree
import re
class Node(object):
    """
    构造节点

    """
    def __init__(self,val=None,children=None,father = None,tag=None,rel=None):
        self.val = val
        self.children = []
        self.father = father
        self.tag = tag 
        # rel记录特殊标记 如同位语
        self.rel = rel

class N_Tree(object):
    def __init__(self):
        """初始化一个空的二叉树"""
        self.root = None
        self.node_dict = {}
    def build(self,node_list):
        final = node_list[-1]
        num = final.count('| ')
        tag = final.strip().rsplit('| ',1)[-1]
        # 处理终端节点
        if tag.endswith('_terminal'):   #endswith()函数用于判断字符串是否以指定后缀结尾，是则返回true：str.endswith(suffix[, start[, end]])
            tag = tag.rsplit('_',1)[0]  #rsplit() 方法从右侧开始将字符串拆分为列表。
        max_len = len(node_list)
        if (tag,max_len) not in self.node_dict:
            de = Node(tag)
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
                    parent_node = Node(parent_tag)
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
                if current.val == 'NP-SBJ':
                    root = Element( 'xj' )
                    sbj = SubElement(root, 'sbj' )
                sub.append(current.val)
                if current.children != None:
                    for j in current.children:
                        cur_queue.append(j)
            res.append(sub)
        return res
    
    def find_parent(self,node):
        return node.father

    # 寻找tag为1的父节点
    def find_father(self,node):
        node_father = node.father
        while node_father.tag != 1:
            node_father = node_father.father
        return node_father

    # 处理小句导致的乱序情况
    def find_have_bro_node(self,node):
        while node.val !='TOP' and node.father and node.father.children[-1] == node:
            node = node.father
        if node.val == 'TOP':
            return node.children[0]
        else:
            return node.father

        
    # 寻找最顶层的TOP节点
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
        return node_res,sent_res

    # 读取转换规则
    def read_rules(self,file_path):
        rules_dict = {}
        with open(file_path,'r',encoding = 'utf-8') as rf:
            for line in rf:
                line = line.strip()
                line_list = line.split()
                key = line_list[:-1]
                value = line_list[-1]
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
            for index,cur_node in enumerate(node.father.children):  #列出元素和下标
                if cur_node == node:
                    left_index = index - 1
            if left_index >= 0:
                left_node = node.father.children[left_index]
                return left_node
            else:
                return 1

    # 规则转换
    def rule_conversion(self,node_res,sent_res,ju_index):
        rules_dict = self.read_rules('./dict/ctb_to_jbw_new3.dict')
        pos_dict = self.read_pos('./dict/ctb_to_jbw_pos.dict')
        xml_dict = {}
        for node in node_res:
            node.val = node.val.lstrip('(') #lstrip截掉字符串左边的空格或指定字符
            # 解决标点、 xml右侧条件 cc_COO 标签
            if node.rel == 'cc_coo':
                finded_node = self.find_father(node)
                father_xml = xml_dict[finded_node]
                cc = SubElement(father_xml, 'cc')
                cc.set('fun','COO')
            if node.rel == 'APP':
                    finded_node = self.find_father(node)
                    father_xml = xml_dict[finded_node]
                    cc = SubElement(father_xml, 'cc' )
                    cc.set('fun','APP')

            if node.rel == 'uni':
                finded_node = self.find_father(node)
                father_xml = xml_dict[finded_node]
                cc = SubElement(father_xml, 'cc')
                cc.set('fun','UNI')

            if node.rel == 'pvt':
                finded_node = self.find_father(node)
                father_xml = xml_dict[finded_node]
                cc = SubElement(father_xml, 'cc')
                cc.set('fun','PVT')

            #同位语
            if node.val in rules_dict and rules_dict[node.val] == 'app':
                for index,i in enumerate(node.father.children):
                    if i == node:
                        bro_index = index

                # 同位右侧可能没有节点 为了测试先注释这一行
                if bro_index+1 <= len(node.father.children) -1:
                    node.father.children[bro_index+1].rel = 'APP'

######################################################################################3
            if node.rel == 'cmp':#解决补语 新建一个节点值为cmp 当前节点的父亲节点为该节点
                # node.tag = 1
                # 找到当前结点的父结点
                finded_node = self.find_father(node)
                #获取到父结点的xml：father_xml
                father_xml = xml_dict[finded_node]
                #在其父结点下通过SubElement（）函数创建cmp结点
                xml_new_tag = SubElement(father_xml, 'cmp')
                #将创建的cmp结点的tag设置为1，以便后续查询
                tmp_node = Node('cmp')
                tmp_node.tag = 1
                #把当前结点赋给node.father
                node.father = tmp_node
                #把新加的cmp结点的加入xml_dict字典
                xml_dict[tmp_node] = xml_new_tag
            # 设置其左孩子
            left_node = None
            left_node_word = None
            left_node_pos = None
            right_bro_nodes_list = []
            # 找当前节点的左孩子节点
            if node.father:
                left_node = None
                # 找到当前节点的索引
                if len(node.father.children) > 1:
                    for index,no in enumerate(node.father.children):
                        tmp_index = index
                    if tmp_index -1 >= 0 and tmp_index -1 < len(node.father.children):
                        left_node = node.father.children[tmp_index - 1]
                        if not left_node.children:
                            left_node_word = left_node.val.strip().split('_',1)[1].strip()
                            left_node_pos = left_node.val.strip().split('_',1)[0].strip()
                    if tmp_index -2 >= 0:
                        left_left_node = node.father.children[tmp_index - 2]
                    right_bro_nodes_list = node.father.children[tmp_index:]
            if left_node and not left_node.children and (left_node_word=='，' or left_node_word=='；' or left_node_word=='：') and left_node_pos=='PU':
                finded_node = self.find_father(left_left_node)
                father_xml = xml_dict[finded_node]
                # 将该节点以及右侧所有的兄弟节点的 父节点 改为新建的xj节点
                if left_left_node in xml_dict:
                    if xml_dict[left_left_node].tag != 'sbj' and xml_dict[left_left_node].tag != 'adv' and xml_dict[left_left_node].tag != 'att':
                        ju = xml_dict['ju']
                        xj = SubElement(ju,'xj')    #SubElement（）函数有两个对象，父结点下一个新的结点
                        # 新建一个xj节点
                        new_node = Node('xj')
                        new_node_list = []
                        for i in right_bro_nodes_list:
                            new_node_list.append(i)
                        father = node.father
                        while father.father:
                            if father.father.children[-1] != father:
                                cur_index = father.father.children.index(father)
                                for i in father.father.children[cur_index+1:]:
                                    new_node_list.append(i)
                            father = father.father
                        new_node.tag = 1
                        xml_dict[new_node] = xj
                else:
                    if father_xml.tag != 'sbj' and father_xml.tag !='adv' and father_xml.tag != 'att':
                        ju = xml_dict['ju']
                        xj = SubElement(ju,'xj')    #SubElement（）函数有两个对象，父结点下一个新的结点
                        # 新建一个xj节点
                        new_node = Node('xj')
                        new_node_list = []
                        for i in right_bro_nodes_list:
                            new_node_list.append(i)
                        father = node.father
                        while father.father:
                            if father.father.children[-1] != father:
                                cur_index = father.father.children.index(father)
                                for i in father.father.children[cur_index+1:]:
                                    new_node_list.append(i)
                            father = father.father
                        for i in new_node_list:
                            i.father = new_node
                        new_node.children = new_node_list
                        new_node.tag = 1
                        xml_dict[new_node] = xj
            if node.val == 'TOP':
                root = Element( 'jbw' )
                ju = SubElement(root,'ju')  
                ju.set('txt',''.join(sent_res))
                ju.set('id',ju_index)
                # 存储ju
                xml_dict['ju'] = ju
                xj = SubElement(ju,'xj')
                xml_dict[node] = xj
                node.tag = 1
            # 叶子节点
            elif node.children == None:
                #处理兼语 不管是不是NONE 都要最后再进行一次判断 添加兼语
                if node.rel == 'pvt':
                    finded_node = self.find_father(node)
                    father_xml = xml_dict[finded_node]
                    cc = SubElement(father_xml, 'cc')
                    cc.set('fun','PVT')
                if node.val.strip().rsplit('_',1)[0]!='-NONE-':
                    finded_node = self.find_father(node)
                    father_xml = xml_dict[finded_node]
                    word = node.val.strip().split('_',1)[1].strip()
                    pos_tag = node.val.strip().split('_',1)[0].strip()
                    if pos_tag == 'VA':
                        for index,no in enumerate(node.father.father.children):
                            if no == node.father:
                                tmp_index = index
                                left_index = tmp_index - 1
                                left_node = node.father.father.children[left_index]
                        if left_node.children and left_node.children[0] and left_node.children[0].val.strip().rsplit('_',1)[0] != '-NONE-':
                            # 原来这句话是注释的 下面一行是打开的
                            finded_node = self.find_father(node)
                            father_xml = xml_dict[finded_node]
                            obj = SubElement(father_xml, 'prd')
                            cv_pos = pos_dict[pos_tag]
                            pos = SubElement(obj, cv_pos)
                            pos.text = word
                        else:
                            finded_node = self.find_father(node)
                            father_xml = xml_dict[finded_node]
                            cv_pos = pos_dict[pos_tag]
                            pos = SubElement(father_xml, cv_pos)
                            pos.text = word
                    # 原来if改成elif
                    elif pos_tag == 'VC' or pos_tag == 'VE' or pos_tag == 'VV':
                        prd_tag = False
                        if node.father.val != 'VSB':
                            finded_node = self.find_father(node)
                            father_xml = xml_dict[finded_node]
                            obj = SubElement(father_xml, 'prd')
                            # 新建prd标签 让VV的父节点为prd
                            cv_pos = pos_dict[pos_tag]
                            pos = SubElement(obj, cv_pos)
                            pos.text = word

                            # 处理prd上的属性
                            if len(node.father.children) > 1:
                                for index,cur_node in enumerate(node.father.children):
                                    if cur_node == node:
                                        tmp_index = index
                                tmp_list = []
                                for i in node.father.children[tmp_index:]:
                                    if i.val in rules_dict:
                                        if rules_dict[i.val]=='obj' or rules_dict[i.val] =='cmp':
                                            tmp_list.append(rules_dict[i.val])
                                    if i.rel == 'cmp':
                                        tmp_list.append('cmp')
                                total_rel = ''.join([j[0] for j in tmp_list])
                                if total_rel == 'o':
                                    obj.set('scp','VO')
                                elif total_rel == 'oo':
                                    obj.set('scp','VOO')
                                elif total_rel == 'c':
                                    obj.set('scp','VC')
                                elif total_rel == 'co':
                                    obj.set('scp','VCO')
                                elif total_rel == 'oc':
                                    obj.set('scp','VOC')
                                else:
                                    obj.set('scp','V')
                            if len(node.father.children) == 1:
                                obj.set('scp','V')
                            # 修改地方
                            prd_tag = True
                        else:
                            finded_node = self.find_father(node)
                            father_xml = xml_dict[finded_node]
                            cv_pos = pos_dict[pos_tag]
                            pos = SubElement(father_xml, cv_pos)
                            pos.text = word
                        # 趋向合成
                        if node.val.strip().split('_',1)[0].strip() == 'VV' or node.val.strip().split('_',1)[0].strip() == 'VC':
                            # SYN 修改规则 VV父结点是VP VV右兄弟结点是VP此VP的所有孩子结点中有VV
                            father_node = node.father
                            if node.father.val == 'VP' and len(node.father.children) == 2 and node.father.children[1].val == 'VP':
                                node_res,sent_res = self.preorder(node.father.children[1])
                                childs_val = [i.val if i.children else i.val.rsplit('_')[0] for i in node_res]
                                if 'VV' in childs_val:
                                    finded_node = self.find_father(node)
                                    father_xml = xml_dict[finded_node]
                                    cc = SubElement(father_xml, 'cc')
                                    cc.set('fun','SYN')
                        # 能愿
                        if node.val == 'VP':
                            if len(node.father.children) > 1:
                                    for index,no in enumerate(node.father.children):
                                        if no == node:
                                            tmp_index = index
                                    if node.father.val == 'VP':
                                            # bro_val 是 叶子节点 且词性是VC
                                            bro_node = node.father.children[tmp_index-1]
                                            if not bro_node.children:
                                                pos,word = bro_node.val.split('_')
                                                if pos == 'VV' or pos == 'VC':
                                                    if len(node.children) >= 1:
                                                        finded_node = self.find_father(node)
                                                        father_xml = xml_dict[finded_node]
                                                        cc = SubElement(father_xml, 'cc')
                                                        cc.set('fun','SYN')
                        # 处理兼语句
                        if pos_tag == 'VE':
                            if len(node.father.children) > 1:
                                for index,cur_node in enumerate(node.father.children):
                                    if cur_node == node:
                                        tem_index = index
                                if (tem_index + 1) < len(node.father.children):
                                    rig_bro_node = node.father.children[tem_index + 1]
                                    if rig_bro_node.val in rules_dict and rules_dict[rig_bro_node.val] == 'obj':
                                        if rig_bro_node.children[0].val in rules_dict and  rules_dict[rig_bro_node.children[0].val] == 'sbj':
                                            
                                            if len(rig_bro_node.children) > 1:
                                                finded_node = self.find_father(rig_bro_node)
                                                if rig_bro_node.children[1].children != None:
                                                    rig_bro_node.children[1].father = finded_node
                                                    rig_bro_node.children[1].rel = 'pvt'
                                                else:
                                                    if len(rig_bro_node.children) > 2:
                                                        if rig_bro_node.children[2].children != None:
                                                            rig_bro_node.children[2].father = finded_node
                                                            rig_bro_node.children[2].rel = 'pvt'
                        if pos_tag == 'VV':
                            if len(node.father.children) > 2:
                                for index,cur_node in enumerate(node.father.children):
                                    if cur_node == node:
                                        tem_index = index
                                if (tem_index + 1) < len(node.father.children) and (tem_index + 2) < len(node.father.children):
                                    first_rig_bro_node = node.father.children[tem_index + 1]
                                    sec_rig_bro_node = node.father.children[tem_index + 2]
                                    if first_rig_bro_node.val in rules_dict and rules_dict[first_rig_bro_node.val] == 'obj':
                                        if sec_rig_bro_node.children != None:
                                            child = sec_rig_bro_node.children[0]
                                            if child.val in rules_dict and rules_dict[child.val] == 'sbj':
                                                sec_rig_bro_node.rel = 'pvt'
                        if prd_tag:
                            new_prd = Node('prd')
                            node.father = new_prd
                            xml_dict[new_prd] = obj
                            new_prd.tag = 1
                    elif pos_tag == 'P':#介词位
                        finded_node = self.find_father(node)
                        father_xml = xml_dict[finded_node]
                        pp = SubElement(father_xml, 'pp')
                        cv_pos = pos_dict[pos_tag]
                        pos = SubElement(pp, cv_pos)
                        pos.text = word
                    elif pos_tag == 'BA' or pos_tag == 'LB':
                        finded_node = self.find_father(node)
                        father_xml = xml_dict[finded_node]
                        if len(node.father.children) > 1:
                            for i in node.father.children:
                                if i != node:
                                    bro_node = i
                            if re.search(r'.P-OBJ',bro_node.val) or re.search(r'.P-.P-OBJ',bro_node.val):
                                if bro_node.children[0].val in rules_dict:
                                    if rules_dict[bro_node.children[0].val] == 'sbj':
                                        adv = SubElement(father_xml, 'adv')
                                        pp = SubElement(adv, 'pp')
                                        cv_pos = pos_dict[pos_tag]
                                        pos = SubElement(pp, cv_pos)
                                        pos.text = word
                                        tmp_node = Node('adv')
                                        tmp_node.tag = 1
                                        bro_node.children[0].father = tmp_node
                                        xml_dict[tmp_node] = adv
                                    else:
                                        pp = SubElement(father_xml, 'pp')
                                        cv_pos = pos_dict[pos_tag]
                                        pos = SubElement(pp, cv_pos)
                                        pos.text = word
                                # 对于不符合条件的LB之前会漏掉
                                else:
                                    pp = SubElement(father_xml, 'pp')
                                    cv_pos = pos_dict[pos_tag]
                                    pos = SubElement(pp, cv_pos)
                                    pos.text = word
                            else:
                                pp = SubElement(father_xml, 'pp')
                                cv_pos = pos_dict[pos_tag]
                                pos = SubElement(pp, cv_pos)
                                pos.text = word
                    elif pos_tag == 'LC':#方位词
                        finded_node = self.find_father(node)
                        father_xml = xml_dict[finded_node]
                        ff = SubElement(father_xml, 'ff')
                        # 加入xml_dict 为了标点符号考虑
                        xml_dict[node] = ff
                        cv_pos = pos_dict[pos_tag]
                        pos = SubElement(ff, cv_pos)
                        pos.text = word
                    # 助位词
                    elif pos_tag == 'DEG' or pos_tag == 'DER' or pos_tag == 'DEV' or pos_tag == 'DEC':
                        finded_node = self.find_father(node)
                        father_xml = xml_dict[finded_node]
                        uu = SubElement(father_xml, 'uu')
                        # 加入xml_dict 为了标点符号考虑
                        xml_dict[node] = uu
                        cv_pos = pos_dict[pos_tag]
                        pos = SubElement(uu, cv_pos)
                        pos.text = word
                        # DER右侧节点为补语 之前代码少了一层if判断
                        if pos_tag == 'DER':
                            for index,i in enumerate(node.father.children):
                                if i == node:
                                    if index < len(node.father.children)-1:
                                        node.father.children[index+1].rel = 'cmp'
                                        break
                    elif pos_tag == 'ETC':
                        finded_node = self.find_father(node)
                        father_xml = xml_dict[finded_node]
                        uu = SubElement(father_xml, 'un')
                        # 加入xml_dict 为了标点符号考虑
                        xml_dict[node] = uu
                        cv_pos = pos_dict[pos_tag]
                        pos = SubElement(uu, cv_pos)
                        pos.text = word
                    elif pos_tag == 'SP' or pos_tag == 'AS' or pos_tag == 'SB' or pos_tag == 'MSP':
                        finded_node = self.find_father(node)
                        father_xml = xml_dict[finded_node]
                        uu = SubElement(father_xml, 'uv')
                        # 加入xml_dict 为了标点符号考虑
                        xml_dict[node] = uu
                        cv_pos = pos_dict[pos_tag]
                        pos = SubElement(uu, cv_pos)
                        pos.text = word
                    # 连词位
                    # elif pos_tag == 'CC' or pos_tag == 'CS':
                    elif pos_tag == 'CS' or pos_tag == 'CC' or pos_tag == 'ADVP-PRP':
                        if pos_tag == 'CC':
                            childs_val = [childs.val if childs.children else childs.val.split('_')[0] for childs in node.father.children]
                            cur_index = node.father.children.index(node)
                            if cur_index + 1 < len(node.father.children) and cur_index - 1 > -2:
                                right_node = node.father.children[cur_index+1]
                                left_node = node.father.children[cur_index-1]
                                finded_node = self.find_father(node)
                                father_xml = xml_dict[finded_node]
                                if cur_index == 0:
                                    finded_node = self.find_father(node)
                                    father_xml = xml_dict[finded_node]
                                    cv_pos = pos_dict[pos_tag]
                                    cc = SubElement(father_xml, 'cc')
                                    pos = SubElement(cc, cv_pos)
                                    pos.text = word
                                else:
                                    if node.father.val == 'VP' and left_node.val == 'VP' and right_node.val == 'VP':
                                        # right_node.rel = 'uni'
                                        cc = SubElement(father_xml, 'cc')
                                        cc.set('fun','UNI')
                                    elif node.father.val == 'IP' and left_node.val == 'IP' and right_node.val == 'IP':
                                        # right_node.rel = 'uni'
                                        cc = SubElement(father_xml, 'cc')
                                        cc.set('fun','UNI')
                                    else:
                                        # right_node.rel = 'cc_coo'
                                        cc = SubElement(father_xml, 'cc')
                                        cc.set('fun','COO')
                                    cv_pos = pos_dict[pos_tag]
                                    pos = SubElement(cc, cv_pos)
                                    pos.text = word
                            else:
                                finded_node = self.find_father(node)
                                father_xml = xml_dict[finded_node]
                                cv_pos = pos_dict[pos_tag]
                                pos = SubElement(father_xml, cv_pos)
                                pos.text = word
                        elif pos_tag == 'CS' or pos_tag == 'ADVP-PRP':
                            cc = SubElement(father_xml, 'cc')
                            cv_pos = pos_dict[pos_tag]
                            pos = SubElement(cc, cv_pos)
                            pos.text = word
                        else:
                            finded_node = self.find_father(node)
                            father_xml = xml_dict[finded_node]
                            cv_pos = pos_dict[pos_tag]
                            pos = SubElement(father_xml, cv_pos)
                            pos.text = word
                    # 独立语
                    elif pos_tag == 'IJ' or pos_tag == 'PRN' or pos_tag == 'NP-PN-SBJ-VOC' or pos_tag == 'INTJ-IJ':
                        finded_node = self.find_father(node)
                        father_xml = xml_dict[finded_node]
                        uu = SubElement(father_xml, 'ind')
                        # 加入xml_dict 为了标点符号考虑
                        xml_dict[node] = uu
                        cv_pos = pos_dict[pos_tag]
                        pos = SubElement(uu, cv_pos)
                        pos.text = word
                    elif pos_tag == 'PU':
                        left_node = self.process_pu(node)
                        if left_node != 1:
                            # 添加PU、 兄弟节点有CC 则在标点后加 空 cc_COO
                            if word == '、':
                                childs_val = [childs.val if childs.children else childs.val.split('_')[0] for childs in node.father.children]
                                cur_index = node.father.children.index(node)
                                if cur_index + 1 < len(node.father.children) and cur_index - 1 > -1:
                                    right_node = node.father.children[cur_index+1]
                                    left_node = node.father.children[cur_index-1]
                                    if 'CC' in childs_val:
                                        right_node.rel = 'cc_coo'
                                    if node.father.val == 'VP' and left_node.val == 'VP' and right_node.val == 'VP':
                                        right_node.rel = 'uni'
                                    if node.father.val == 'IP' and left_node.val == 'IP' and right_node.val == 'IP':
                                        right_node.rel = 'uni'

                            adjoin_node = self.find_left_word(left_node)
                            if adjoin_node in xml_dict:
                                father_xml = xml_dict[adjoin_node]
                            else:
                                finded_node = self.find_father(adjoin_node)
                                father_xml = xml_dict[finded_node]
                            cv_pos = pos_dict[pos_tag]
                            pos = SubElement(father_xml, cv_pos)
                            pos.text = word
                        else:
                            
                            cv_pos = pos_dict[pos_tag]
                            pos = SubElement(father_xml, cv_pos)
                            pos.text = word
                    else:
                        if pos_tag== '-NONE-':
                            pass
                        else:
                            cv_pos = pos_dict[pos_tag]
                            pos = SubElement(father_xml, cv_pos)
                            pos.text = word
                # 如果叶子节点为-NONE-                                                                                                                                      
                else:
                    if node.father.val in rules_dict and (rules_dict[node.father.val] == 'sbj' or rules_dict[node.father.val] == 'obj'):
                        finded_node = self.find_father(node)
                        father_xml = xml_dict[finded_node]
                        xml_new_tag = SubElement(father_xml, 'x')
                        xml_dict[node] = xml_new_tag
            # 如果节点的值不在规则列表中
            elif node.val not in rules_dict:
                if node.val == 'VSB' or node.val == 'VRD':
                    node.tag = 1
                    finded_node = self.find_father(node)
                    father_xml = xml_dict[finded_node]
                    xml_new_tag = SubElement(father_xml, 'prd')
                    xml_dict[node] = xml_new_tag
            # pass
                if node.val == 'QP' or node.val == 'DP':
                    if node.father.val.startswith('NP-'):
                        node.tag = 1
                        finded_node = self.find_father(node)
                        father_xml = xml_dict[finded_node]
                        xml_new_tag = SubElement(father_xml, 'att')
                        xml_dict[node] = xml_new_tag

                # 定语规则 右边是NP-SBJ或ADVP或NP-TMP的NP-LOC-PN
                if node.val == 'NP-LOC-PN':
                    # 找到当前节点的索引
                    if len(node.father.children) > 1:
                        for index,no in enumerate(node.father.children):
                            if no == node:
                                tmp_index = index
                        for i in node.father.children[tmp_index:]:
                            if i.val == 'NP-SBJ' or i.val == 'ADVP' or i.val == 'NP-TMP':
                                finded_node = self.find_father(node)
                                father_xml = xml_dict[finded_node]
                                cmp_tmp = SubElement(father_xml, 'att')
                                xml_dict[node] = cmp_tmp
                                node.tag = 1
                # 右边有兄弟节点的CP
                if node.val == 'CP':
                    # 找到当前节点的索引
                    if len(node.father.children) > 1:
                        for index,no in enumerate(node.father.children):
                            if no == node:
                                tmp_index = index
                        if tmp_index +1 <= len(node.father.children) - 1:
                            finded_node = self.find_father(node)
                            father_xml = xml_dict[finded_node]
                            cmp_tmp = SubElement(father_xml, 'att')
                            xml_dict[node] = cmp_tmp
                            node.tag = 1
                # 主语 右边是VP的NP-LOC-PN
                if node.val == 'NP-LOC-PN':
                    # 取到当前结点的索引
                    if len(node.father.children) > 1:
                        for index,no in enumerate(node.father.children):
                            if no == node:
                                tmp_index = index
                        for i in node.father.children[tmp_index:]:
                            if i.val == 'VP':
                                #找到当前结点的父结点
                                fined_node = self.find_father(node)
                                #取到父结点的xml
                                father_xml = xml_dict[fined_node]
                                #在父结点下创建obj结点
                                cmp_tmp = SubElement(father_xml, 'sbj')
                                #把新加的结点放进xml字典中：
                                xml_dict[node] = cmp_tmp
                                node.tag = 1
                # 主语 左边无VV兄弟结点的LCP-LOC
                if node.val == 'LCP-LOC':
                    for index,no in enumerate(node.father.children):
                        if no == node:
                            tmp_index = index
                            for i in node.father.children[:tmp_index]:
                                if i.val != 'VV':
                                    fined_node = self.find_father(node)
                                    father_xml = xml_dict[fined_node]
                                    cmp_tmp = SubElement(father_xml, 'sbj')
                                    xml_dict[node] = cmp_tmp
                                    node.tag =1
                # 主语 无ADVP子节点的...
                if node.val == 'NP-FOC' or node.val == 'NP-FOC-12' or node.val == 'NP-FOC-15' or node.val == 'NP-FOC-2' or node.val == 'NP-FOC-3' or node.val == 'NP-FOC-4' or node.val == 'NP-FOC-5' or node.val == 'NP-FOC-9':
                    # 先把当前结点的子节点进行编码：
                    for index,no in enumerate(node.children):
                        # 如果没有子节点，则定义为sbj
                        if index == 0:
                            fined_node = self.find_father(node)
                            father_xml = xml_dict[fined_node]
                            cmp_tmp = SubElement(father_xml, 'sbj')
                            xml_dict[node]=cmp_tmp
                            node.tag = 1
                        # 无ADVP子节点：
                        elif no.val != 'ADVP':
                            fined_node = self.find_father(node)
                            father_xml = xml_dict[fined_node]
                            cmp_tmp = SubElement(father_xml, 'sbj')
                            xml_dict[node]=cmp_tmp
                            node.tag = 1
            # 宾语
                #左边有VV兄弟节点的LCP-LOC
                if node.val =='LCP-LOC':
                    if len(node.father.children)>1:
                        for index,no in enumerate(node.father.children):
                            if no == node:
                                tmp_index = index                   
                            for i in node.father.children[:tmp_index]:
                                if i.val == 'VV':
                                    fined_node = self.find_father(node)
                                    father_xml = xml_dict[finded_node]
                                    cmp_tmp = SubElement(father_xml, 'obj')
                                    xml_dict[node] = cmp_tmp
                                    node.tag = 1
                #左侧有VV、VC、VE的QP-EXT
                if node.val =='QP-EXT':
                        if len(node.father.children)>1:
                            for index,no in enumerate(node.father.children):
                                if no == node:
                                    tmp_index = index
                            if tmp_index - 1 >= 0:
                                left_value = node.father.children[tmp_index - 1].val
                                if  left_value == 'VV' or left_value == 'VE' or left_value == 'VC':
                                    finded_node = self.find_father(node)
                                    father_xml = xml_dict[finded_node]
                                    node.tag = 1
                                    obj = SubElement(father_xml, 'obj')
                                    xml_dict[node] = obj
                                    
                                else:
                                    finded_node = self.find_father(node)
                                    father_xml = xml_dict[finded_node]
                                    node.tag = 1
                                    obj = SubElement(father_xml, 'cmp')
                                    xml_dict[node] = obj
                                left_bro = node.father.children[tmp_index-1]
                if node.val == 'VCD' and len(node.children) == 2: #联合
                    node.children[1].rel = 'uni'
                # 根据PP确定补语和状语
                if node.val == 'PP' and node.children[0].val.split('_')[0] != '-NONE-':
                    if len(node.father.children) > 1:
                        for index,no in enumerate(node.father.children):
                            if no == node:
                                tmp_index = index
                        # 右兄弟节点有VP的PP 不一定相邻
                        for bro_index in range(tmp_index,len(node.father.children)):
                            if node.father.children[bro_index].val == 'VP':
                                finded_node = self.find_father(node)
                                father_xml = xml_dict[finded_node]
                                cmp_tmp = SubElement(father_xml, 'adv')
                                xml_dict[node] = cmp_tmp
                                node.tag = 1
                # 状语 右兄弟节点有VP的PP-LOC、PP-LOC-2、PP-LOC-WH
                if node.val == 'PP-LOC' or node.val == 'PP-LOC-2' or node.val == 'PP-LOC-WH' and node.children[0].val.split('_')[0] != '-NONE-':
                    if len(node.father.children) > 1:
                        for index,no in enumerate(node.father.children):
                            if no == node:
                                tmp_index = index
                        # 右兄弟节点有VP 不一定相邻
                        for i in node.father.children[tmp_index:]:
                            if i.val == 'VP':
                                finded_node = self.find_father(node)
                                father_xml = xml_dict[finded_node]
                                cmp_tmp = SubElement(father_xml, 'adv')
                                xml_dict[node] = cmp_tmp
                                node.tag = 1
                # 这些节点的子节点有ADVP是状语
                if node.val == 'NP-FOC' or node.val == 'NP-FOC-12' or node.val == 'NP-FOC-15' or node.val == 'NP-FOC-2' or node.val == 'NP-FOC-3' or node.val == 'NP-FOC-4' or node.val == 'NP-FOC-5' or node.val == 'NP-FOC-9':
                    advp_tag = False
                    for index,no in enumerate(node.children):
                            if no.val == 'ADVP':
                                advp_tag = True
                    if advp_tag:
                        finded_node = self.find_father(node)
                        father_xml = xml_dict[finded_node]
                        cmp_tmp = SubElement(father_xml, 'adv')
                        xml_dict[node] = cmp_tmp
                        node.tag = 1
                # 处理连动 VP节点的左侧和父亲节点都是VP
                if node.val == 'VP' and node.father.val == 'VP':
                    if len(node.father.children) > 1:
                        for index,cur_node in enumerate(node.father.children):
                            if cur_node == node:
                                tmp_index = index
                        if tmp_index-1 >= 0 and node.father.children[tmp_index-1].val == 'VP':
                            finded_node = self.find_father(node)
                            father_xml = xml_dict[finded_node]
                            cc = SubElement(father_xml, 'cc')
                            cc.set('fun','SER')
                if node.val == 'PP' or node.val == 'PP-LOC':
                    if len(node.father.children) > 1:
                        for index,cur_node in enumerate(node.father.children):
                            if cur_node == node:
                                tma_index = index
                        if tma_index - 1 >= 0:
                            left_value = node.father.children[tma_index - 1].val.split('_')[0]
                            if  left_value == 'VV':
                                finded_node = self.find_father(node)
                                father_xml = xml_dict[finded_node]
                                node.tag = 1
                                #修正 此处应该是补语cmp：左兄弟节点有VV的PP、PP-LOC
                                cmp = SubElement(father_xml, 'cmp')
                                xml_dict[node] = cmp
            else:
                if len(node.children) == 1 and node.children[0].children == None and node.children[0].val.strip().rsplit('_',1)[0]=='-NONE-':
                    if rules_dict[node.val] == 'sbj' or rules_dict[node.val] == 'obj':
                        finded_node = self.find_father(node)
                        father_xml = xml_dict[finded_node]
                        node.tag = 1
                        xml_tag = rules_dict[node.val]
                        xml_new_tag = SubElement(father_xml, xml_tag )
                        xml_dict[node] = xml_new_tag
                else:
                    # 处理prd缺省
                    if node.val == 'QP-PRD' or node.val == 'NP-PRD' or node.val == 'PP-PRD':
                        if len(node.father.children) > 1:
                            for index,j in enumerate(node.father.children):
                                if j == node:
                                    left_index = index-1
                            left_node = node.father.children[left_index]
                            if left_node.val != 'VC':
                                finded_node = self.find_father(node)
                                father_xml = xml_dict[finded_node]
                                prd_tmp = SubElement(father_xml, 'prd')
                                xml_new_tag = SubElement(prd_tmp, 'x')
                    if node.val == 'NP-OBJ':
                        if len(node.father.children) > 2:
                            for index,no in enumerate(node.father.children):
                                if no == node:
                                    left_index = index-1
                                    right_index=index+1
                                    if left_index >= 0 and right_index <= len(node.father.children)-1:
                                        left_node = node.father.children[left_index]
                                        right_node = node.father.children[right_index]
                                        if left_node.val == 'VV' and right_node.val == 'IP' and node.father.val == 'VP':
                                            finded_node = self.find_father(node)
                                            father_xml = xml_dict[finded_node]
                                            cc = SubElement(father_xml, 'cc')
                                            cc.set('fun','PVT')                                        
                    # 解决重复定语情况 之前无if判断
                    if (node.val == 'ADJP' and node.father.val == 'DNP') or rules_dict[node.val]=='app':
                        pass
                    elif len(node.children) == 1 and node.children[0].children!=None and len(node.children[0].children) == 1 and node.children[0].children[0].children == None and node.children[0].children[0].val.strip().rsplit('_',1)[0]=='-NONE-':
                        pass
                    elif node.val == 'IP-OBJ':
                        if len(node.father.children) > 1:
                            for index,no in enumerate(node.father.children):
                                if no == node:
                                    left_index = index-1
                                    if left_index >= 0:
                                       left_node = node.father.children[left_index]
                                       if left_node.val.split('_')[0] == 'PU':
                                           pass
                                       else:
                                            finded_node = self.find_father(node)
                                            father_xml = xml_dict[finded_node]
                                            xml_tag = rules_dict[node.val]
                                            xml_new_tag = SubElement(father_xml, xml_tag )
                                            xml_dict[node] = xml_new_tag
                                            node.tag = 1  
                    else:
                        finded_node = self.find_father(node)
                        father_xml = xml_dict[finded_node]
                        xml_tag = rules_dict[node.val]
                        xml_new_tag = SubElement(father_xml, xml_tag )
                        xml_dict[node] = xml_new_tag
                        node.tag = 1
        xml_string = etree.tostring(root)
        tree = minidom.parseString(xml_string)
        return tree.toprettyxml()

def read_input(input_file):
    with open(input_file,'r',encoding = 'utf-8') as rf:
        content_list = rf.read().strip().split('\n\n')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--i')
    parser.add_argument('--inputfile')
    parser.add_argument('--outputdir')
    args = parser.parse_args()
    rf = open(args.inputfile, "r", encoding='utf-8')
    
    sent_list = rf.read().strip().split('\n\n')
    for index, sent in enumerate(sent_list):
        tree = N_Tree()
        node_list = sent.split('\n')
        tree.build(node_list)
        tree.root = tree.node_dict[('TOP',1)]
        node_res, sent_res = tree.preorder(tree.root)
        index = str(index+1).zfill(5)
        jbw_xml = tree.rule_conversion(node_res, sent_res, index)
        save_file = str(args.outputdir) + index + '.xml'

        with open(save_file, 'w', encoding='utf-8') as wf:
            wf.write(jbw_xml)