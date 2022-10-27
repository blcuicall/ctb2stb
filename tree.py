#!/usr/bin/env python

'''A Penn Treebank-style tree
   author: Liang Huang <lhuang@isi.edu>
'''

import sys
logs = sys.stderr
import argparse

from collections import defaultdict

class Tree(object):

    def __init__(self, label, span, wrd=None, subs=None):

        assert (wrd is None) ^ (subs is None), \
               "bad tree %s %s %s" % (label, wrd, subs)
        self.label = label
        self.span = span
        self.word = wrd
        self.subs = subs
        self._str = None
        self._hash = None
        # self.res_str = res_str

    def is_terminal(self):
        return self.word is not None

    def dostr(self):
        return "(%s %s)" % (self.label, self.word) if self.is_terminal() \
               else "(%s %s)" % (self.label, " ".join(map(str, self.subs)))

    def __str__(self):
        if self._str is None:
            self._str = self.dostr()
        return self._str

    __repr__ = __str__

    def __hash__(self):
        if self._hash is None:
            self._hash = hash(str(self))
        return self._hash

    def __eq__(self, other):
        ### CAUTION!
        return str(self) == str(other)

    def span_width(self):
        return self.span[1] - self.span[0]

    __len__ = span_width     

    def arity(self):
        return len(self.subs)

    def labelspan(self):
        return "%s" % (self.label)

    def spanlabel(self):
        return "[%d-%d]: %s" % (self.span[0], self.span[1], self.label)

    @staticmethod
    def _parse(line, pos=0, wrdidx=0, trunc=True):
        ''' returns a triple:
            ( (pos, wordindex), is_empty, tree)
            The is_empty bool tag is used for eliminating emtpy nodes recursively.
            Note that in preorder traversal, as long as the indices do not advance for empty nodes,
            it is fine for stuff after the empty nodes.
        '''
        ## (TOP (S (ADVP (RB No)) (, ,) (NP (PRP it)) (VP (VBD was) (RB n't) (NP (JJ Black) (NNP Monday))) (. .)))
        # print(line[pos])
        assert line[pos]=='(', "tree must starts with a ( ! line=%s, pos=%d, line[pos]=%s" % (line, pos, line[pos])
            
        empty = False
        # 第pos个空格
        space = line.find(" ", pos)
        # 标签
        label = line[pos + 1 : space]
        if trunc:
            ## remove the PRDs from NP-PRD
            if label[0] != "-":
                dashpos = label.find("-")            
                if dashpos >= 0:
                    label = label[:dashpos]

                ## also NP=2 coreference (there is NP-2 before)
                dashpos = label.find("=")            
                if dashpos >= 0:
                    label = label[:dashpos]

                ## also ADVP|PRT and PRT|ADVP (terrible!)
                dashpos = label.find("|")            
                if dashpos >= 0:
                    label = label[:dashpos]

            else:
                ## remove traces
                ## CAUTION: emptiness is recursive: (NP (-NONE- *T*-1))
                if label == "-NONE-":
                    empty = True
                
        newpos = space + 1
        newidx = wrdidx
        if line[newpos] == '(':
            ## I am non-terminal
            subtrees = []            
            while line[newpos] != ')':
                if line[newpos] == " ":
                    newpos += 1
                (newpos, newidx), emp, sub = Tree._parse(line, newpos, newidx, trunc)
                if not emp:
                    subtrees.append(sub)
                
            return (newpos + 1, newidx), subtrees==[], \
                   Tree(label, (wrdidx, newidx), subs=subtrees)
        
        else:
            ## terminal
            finalpos = line.find(")", newpos)
            word = line[newpos : finalpos]
            ## n.b.: traces shouldn't adv index!
            return (finalpos + 1, wrdidx + 1 if not empty else wrdidx), \
                   empty, Tree(label, (wrdidx, wrdidx+1), wrd=word)

    @staticmethod
    def parse(line, trunc=False):

        _, is_empty, tree = Tree._parse(line, 0, 0, trunc)

        assert not is_empty, "The whole tree is empty! " + line

        if tree.label != "TOP":
            # create another node
            tree = Tree(label="TOP", span=tree.span, subs=[tree])

        return tree
        
    def all_label_spans(self):
        '''get a list of all labeled spans for PARSEVAL'''

        if self.is_terminal():
            return []
        
        a = [(self.label, self.span)]
        for sub in self.subs:
            a.extend(sub.all_label_spans())

        return a

    def label_span_counts(self):
        '''return a dict mapping (label, span) -> count '''
        d = defaultdict(int)
        for a in self.all_label_spans():
            d[a] += 1
        return d

    def pp(self, res_str,level=0):
        if not self.is_terminal():
            # print("%s%s" % ("| " * level, self.labelspan()))
            tmp_str = "| " * level + self.labelspan()
            res_str.append(tmp_str)
            for sub in self.subs:
                sub.pp(res_str,level+1)
        else:
            tmp_str = "| "*level + self.labelspan() + '_' + self.word + '_terminal'
            res_str.append(tmp_str)

    def height(self, level=0):
        if self.is_terminal():
            return 1
        return max([sub.height() for sub in self.subs]) + 1            
            
###########################################

## attached code does empty node removal ##

###########################################

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", required=True, help="input file path")
    parser.add_argument("--max_len", default=400, help="maximum sentence length")
    parser.add_argument("--pp", default=False, help="pretty print")
    parser.add_argument("--height", default=False, help="output the height of each tree")
    parser.add_argument("--clean", default=False, help="clean up functional tags and empty nodes")
    FLAGS = parser.parse_args()
    with open(FLAGS.i, "r", encoding="UTF-8") as fr:
        for line in fr:
            t = Tree.parse(line.strip(), trunc=FLAGS.clean)
            res_str = []
            if len(t) <= FLAGS.max_len:
                if FLAGS.pp:
                    t.pp(res_str)
                    for item in res_str:
                        print(item)
                elif FLAGS.height:
                    print("%d\t%d" % (len(t), t.height()))
                else:
                    print(t)
            print()