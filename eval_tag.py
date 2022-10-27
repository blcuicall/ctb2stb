from tree import Tree
from collections import defaultdict
from tqdm import tqdm
import argparse
import pandas as pd

# 把括号形式的数据转化成树
def construct_trees(path):
    trees = []
    with open(path, "r") as f:
        lines = f.readlines()
    for line in lines:
        tree = Tree.parse(line)
        trees.append(tree.subs[0])
    return trees

def main(args):
    # 新闻标准答案
    gold_path = args.gold
    test_path = args.pred

    output_path = args.save_txt
    save_excel = args.save_excel

    gold_trees = construct_trees(gold_path)
    test_trees = construct_trees(test_path)

    gold_span_labels = defaultdict(int)
    test_span_labels = defaultdict(int)
    matched_span_labels = defaultdict(int)

    # 计数
    gold_barckets_all = 0
    test_brackets_all = 0
    matched_brackets_all = 0

    # 权重
    weight_zwb = 4
    weight_dzb = 2
    weight_others = 1

    # 不同成分技计数
    gold_barckets_zwb = 0
    test_barckets_zwb = 0
    matched_barckets_zwb = 0
    gold_barckets_dzb = 0
    test_barckets_dzb = 0
    matched_barckets_dzb = 0
    gold_barckets_others = 0
    test_barckets_others = 0
    matched_barckets_others = 0

    for gold_tree, test_tree in tqdm(zip(gold_trees, test_trees)):
        gold_barckets = len(gold_tree.all_label_spans())
        test_brackets = len(test_tree.all_label_spans())
        for bracket in gold_tree.all_label_spans():
            gold_span_labels[bracket[0]] += 1
            if bracket[0] == "sbj" or "prd" in bracket[0] or bracket[0] == "obj":
                gold_barckets_zwb += 1
            elif bracket[0] == "att" or bracket[0] == "adv" or bracket[0] == "cmp":
                gold_barckets_dzb += 1
            else:
                gold_barckets_others += 1
        matched_brackets = 0
        for bracket in test_tree.all_label_spans():
            test_span_labels[bracket[0]] += 1
            if bracket[0] == "sbj" or "prd" in bracket[0] or bracket[0] == "obj":
                test_barckets_zwb += 1
            elif bracket[0] == "att" or bracket[0] == "adv" or bracket[0] == "cmp":
                test_barckets_dzb += 1
            else:
                test_barckets_others += 1
            if bracket in gold_tree.all_label_spans():
                matched_brackets += 1
                matched_span_labels[bracket[0]] += 1
                if bracket[0] == "sbj" or "prd" in bracket[0] or bracket[0] == "obj":
                    matched_barckets_zwb += 1
                elif bracket[0] == "att" or bracket[0] == "adv" or bracket[0] == "cmp":
                    matched_barckets_dzb += 1
                else:
                    matched_barckets_others += 1

        gold_barckets_all += gold_barckets
        test_brackets_all += test_brackets
        matched_brackets_all += matched_brackets

    dicSortList = sorted(gold_span_labels.items(), key=lambda x: x[1], reverse=True)

    with open(output_path, "w") as fout:
        fout.write("label\tmatched\tgold\ttest\tPresition    Recall    F1_score\n")

    df_list = []

    with open(output_path, "a") as fout:
        for label in dicSortList:
            try:
                p = matched_span_labels[label[0]] / test_span_labels[label[0]]
                r = matched_span_labels[label[0]] / gold_span_labels[label[0]]
                f = 2 * p * r / (p + r)
            except:
                p = 0
                r = 0
                f = 0
            fout.write(label[0] + "\t" +
                    str(matched_span_labels[label[0]]) + "\t" +
                    str(gold_span_labels[label[0]]) + "\t" +
                    str(test_span_labels[label[0]]) + "\t" +
                    str(p) + "    " + str(r) + "    " + str(f) + "\n")
            # 保存到excel中
            tmp_list = []
            tmp_list.append(label[0])
            tmp_list.append(round(matched_span_labels[label[0]],2))
            tmp_list.append(round(gold_span_labels[label[0]],2))
            tmp_list.append(round(test_span_labels[label[0]],2))
            tmp_list.append(round(f,2))
            df_list.append(tmp_list)
    res_df = pd.DataFrame(df_list,columns=['label','matched','gold','prd','F1'])
    res_df.to_excel(save_excel,index=None)

    precision = matched_brackets_all / test_brackets_all
    recall = matched_brackets_all / gold_barckets_all
    f1_score = 2 * precision * recall / (precision + recall)

    with open(output_path, "a") as f:
        f.write("\n" + "precision: " + str(precision) + "\n" +
                "recall: " + str(recall) + "\n" +
                "f1_score:" + str(f1_score) + "\n")

    print(precision, recall, f1_score)

    weighted_precision = (matched_barckets_zwb * weight_zwb + matched_barckets_dzb * weight_dzb + matched_barckets_others * weight_others) / (test_barckets_zwb * weight_zwb + test_barckets_dzb * weight_dzb + test_barckets_others * weight_others)
    weighted_recall = (matched_barckets_zwb * weight_zwb + matched_barckets_dzb * weight_dzb + matched_barckets_others * weight_others) / (gold_barckets_zwb * weight_zwb + gold_barckets_dzb * weight_dzb + gold_barckets_others * weight_others)
    weighted_f1_score = 2 * weighted_precision * weighted_recall / (weighted_precision + weighted_recall)

    with open(output_path, "a") as f:
        f.write("\n" + "weigthed_precision: " + str(weighted_precision) + "\n" +
                "weigthed_recall: " + str(weighted_recall) + "\n" +
                "weigthed_f1_score:" + str(weighted_f1_score))

    print(weighted_precision, weighted_recall, weighted_f1_score)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--gold')
    parser.add_argument('--pred')
    parser.add_argument('--save_txt')
    parser.add_argument('--save_excel')
    args = parser.parse_args()
    main(args)
