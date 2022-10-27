'''
Author: hzs
Date: 2022-04-12 19:16:47
LastEditors: hzs
LastEditTime: 2022-05-29 09:53:14
Description: 去除ｘ下的none节点　转换PVT APP标签的位置
'''
from tree import Tree
import argparse
from diagram_convert3 import Node, N_Tree
def get_consi_parse(input_file):
    with open(input_file,'r',encoding='utf-8') as rf:
        consi_sents = rf.read().strip().split('\n')
    for i in consi_sents:
        yield i

def tree2str(root, children):
        if not root:
            return ""
        if not children:
            return " ".join(f"{root.val}".rsplit("_", 1))
        ret = f"{root.val}"
        for child in children:
            ret += f" ({tree2str(child, child.children)})"
        return ret

def get_tree_pp(sent,res_str):
    t = Tree.parse(sent)
    t.pp(res_str)
    return res_str

def get_tree(node_list):
    tree = N_Tree()
    tree.build(node_list)
    tree.root = tree.node_dict[('TOP', 1)]
    node_res, sent_res = tree.preorder(tree.root)
    for node in node_res:
        # 去除空节点　调整PVT的位置
        if node.children == None:
            pos, word = node.val.rsplit('_', 1)
            if word == '-NONE-':
                if pos == 'cc_COO' or pos == 'cc_APP' or pos == 'cc_SYN' or pos == 'cc_PVT' or pos == 'cc_UNI':
                    node.val = pos
                    cur_index = node.father.children.index(node)
                    left_bro = node.father.children[cur_index-1]
                    node.father.children.remove(left_bro)
                    node.children = [left_bro]
                    left_bro.father = node
                elif pos == 'cc_SER':
                    node.val = pos
                    cur_index = node.father.children.index(node)
                    right_bro = node.father.children[cur_index+1]
                    node.father.children.remove(right_bro)
                    node.children = [right_bro]
                    right_bro.father = node
                else:
                    if len(node.father.children) == 1:
                        if len(node.father.father.children) == 1 :
                            node.father.father.father.children.remove(node.father.father)
                        node.father.father.children.remove(node.father)
                    else:
                        node.father.children.remove(node)
    tree_str = tree2str(node_res[0],node_res[0].children)
    print(f"({tree_str})")
    return node_res

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input')
    args = parser.parse_args()
    for consi_sent in get_consi_parse(args.input):
        res_str =[]
        res = get_tree_pp(consi_sent,res_str)
        tree_node = get_tree(res)