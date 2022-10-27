## CTB2STB

**CCL2022** 中 **《句式结构树库的自动构建研究》** 树库转换的源代码。

## 环境配置

- lxml
- openpyxl
- tqdm
- pandas
您可以通过下述方法配置环境:
```
pip install -r requirements.txt
```

## 使用

### 运行

您可以修改 `run.sh` 以便于在您的数据集上运行。

您也可以运行 `run_sample.sh` 以便在小样本 `sample_data` 上测试我们的树库转换。

### 人工标注数据转换

```python
xml2tree_artificial.py
--inputdir /PATH/to/your/artificial/save/file/
--outputfile /PATH/to/your/artificial/result.txt
```

### 评估

```python
python eval_tag.py 
--gold /PATH/to/your/artificial/result.txt
--pred /PATH/to/your/result.modi.process.txt
--save_txt  /PATH/to/your/txt
--save_excel /PATH/to/your/xlsx
```

## 引用

```tex
@inproceedings{xie-etal-2022-ctb2stb,
    title = "句式结构树库的自动构建研究",
    author = "谢, 晨晖 and
      胡, 正升 and
      杨, 麟儿 and
      廖, 田昕 and
      杨, 尔弘",
    booktitle = "第二十一届全国计算语言学学术会议",
    year = "2022"
}
```





Code for the paper "Automatic Construction of Sentence Pattern Structure Treebank" on CCL 2022.

## Requirements
- lxml
- openpyxl
- tqdm
- pandas
In order to install them, you can run this command:
```
pip install -r requirements.txt
```

## Usage

### Run on sample data

You can run `run.sh` on your own dataset.

Or run `run_sample.sh` on the small sample data under the `sample_data` folder.

### Conversation on artificial annotated data

```python
xml2tree_artificial.py
--inputdir /PATH/to/your/artificial/save/file/
--outputfile /PATH/to/your/artificial/result.txt
```

### Evaluation

```python
python eval_tag.py 
--gold /PATH/to/your/artificial/result.txt
--pred /PATH/to/your/result.modi.process.txt
--save_txt  /PATH/to/your/txt
--save_excel /PATH/to/your/xlsx
```

## Citation

```tex
@inproceedings{xie-etal-2022-ctb2stb,
    title = "Automatic Construction of Sentence Pattern Structure Treebank",
    author = "Xie, Chenhui and
      Hu, Zhensheng and
      Yang, Liner and
      Liao, Tianxin and
      Yang, Erhong",
    booktitle = "Proceedings of the 21th Chinese National Conference on Computational Linguistics",
    year = "2022"
}
```

