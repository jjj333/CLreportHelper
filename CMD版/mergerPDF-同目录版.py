#!/usr/bin/env python3
# encoding: utf-8

"""
# File       : mergerPDF-同目录版.py
# Time       ：2023/10/7 11:06
# Author     ：HLJ
# python ver ：3.7
# version    ：0.1
# Description：实现pdf合并
"""

import os
from PyPDF2 import PdfMerger


def mergerPdf():
    target_path = os.getcwd()
    # print(target_path)
    pdf_lst = [f for f in os.listdir(target_path) if f.endswith('.pdf')]
    pdf_lst = [os.path.join(target_path, filename) for filename in pdf_lst]

    file_merger = PdfMerger()
    for pdf in pdf_lst:
        file_merger.append(pdf)     # 合并pdf文件

    file_merger.write(f"{target_path}/合并.pdf")


if __name__ == '__main__':
    mergerPdf()