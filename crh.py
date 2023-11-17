#!/usr/bin/env python3
# encoding: utf-8

"""
# File       : crh.py
# Time       : 2023/9/13 16:23
# Author     : HLJ
# python ver : 3.7
# version    : v1
# Description: 实现协会报告自动虚拟打印成pdf并保存成需要的文件名-配合GUI的模块
"""

import logging
import sys
import time
import win32gui
import platform
import pyautogui as pa
from PIL import Image
from PyQt5.QtWidgets import QApplication

sys.setrecursionlimit(3000)  # 将默认的递归深度修改为3000

retry_count = 1  # 重试次数
finish_count = 1  # 完成报告数
s_times = 0  # 寻找保存窗口的次数
f_times = 0  # 打印完成次数
fail_count = 1  # 检测弹窗超时次数
prt_win_title = "Print to PDF Document - Foxit Reader PDF Printer"  # 配合windows系统的虚拟打印窗口的标题
end_sign = 0


def check_sys():
    global prt_win_title
    sys_ver = int(platform.uname().version.split('.')[0])
    if sys_ver >= 10:  # 系统为win10
        prt_win_title = "将打印输出另存为"  # win10,使用微软自带pdf虚拟打印
    else:
        prt_win_title = "Print to PDF Document - Foxit Reader PDF Printer"


def log():
    logger = logging.getLogger()
    logger.setLevel(level=logging.INFO)  # INFO一定要大写

    formatter = logging.Formatter(
        "%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: 【函数%(funcName)s】：%(message)s"
    )

    file_handler = logging.FileHandler('log.txt', encoding="utf-8", mode="w")  # 覆盖模式，每次启动程序清空日志，否则过多的报错可能让日志文件暴涨
    file_handler.setLevel(level=logging.DEBUG)
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)


def windowEnumerationHandler(hwnd, windowlist):
    windowlist.append((hwnd, win32gui.GetWindowText(hwnd)))


def set_front_hwnd(title):
    # 通过枚举获取所有窗口的句柄和标题
    windowlist = []
    win32gui.EnumWindows(windowEnumerationHandler, windowlist)
    # print(windowlist)
    # 遍历所有窗口，指定要操作的窗口的标题的关键词
    for i in windowlist:
        if title in i[1].lower():
            # 按规则显示窗口，如果没有这一行，那么已最小化的窗口将无法激活，只能激活后台的未最小化的窗口。
            # 这里的数字4是根据实际情况填写的，有时候可能本来是最大化的窗口，但最终显示后却不是最大化，可根据最下面的图去选择最合适的数字。
            # 关于最后一个参数：https://learn.microsoft.com/zh-cn/windows/win32/api/winuser/nf-winuser-showwindow#概览
            win32gui.ShowWindow(i[0], 4)

            # 激活窗口到前台
            win32gui.SetForegroundWindow(i[0])

            # 显示句柄和标题方便查看
            # print(i)

            # 如果匹配“关键词”的窗口有多个，想一次性显示就应该延时一下，如果只需要随便显示其中一个就直接break结束
            # time.sleep(2)
            # break


def target_pic(bn_pic):
    bn_image = Image.open(f'./pic/{bn_pic}.png')
    # print(f'./pic/{bn_pic}.png')
    try:
        msg = pa.locateOnScreen(bn_image, grayscale=True, confidence=.9)
    except:
        msg = None
    return msg


def click_bn(bn_pic):
    msg = target_pic(bn_pic)
    if msg is not None:
        x, y, width, height = msg
        logging.info(f"图标\"{bn_pic}\"在屏幕中的位置是：X={x},Y={y}，宽{width}像素,高{height}像素")
        pa.click(msg)
    else:
        logging.info("没找到按钮！协会软件没开？还是没勾选报告？")


def save_pdf():
    global finish_count, s_times, f_times
    start_time = time.time()
    QApplication.processEvents()  # 处理GUI事件
    btn_pos_msg = None
    # with pysnooper.snoop("./debug.log"):        # 调试器
    while btn_pos_msg is None:
        timeout = 12  # 设置超时时间，秒
        tt = time.time() - start_time
        if tt < timeout and fail_count < 3:  # 寻找保存窗口
            # format_tt = '%.2f' % tt
            # print(f'\r寻找打印保存窗口中……{format_tt}s\n', end='')
            time.sleep(0.05)  # 延时保持稳定运行
            btn_pos_msg = target_pic('save_window')
            s_times += 1
            # print(f'第{s_times}次找窗口结束\n')
        elif timeout <= tt < timeout * 2 and fail_count < 3:  # 寻找“打印结束”
            f_times += 1
            # print(f'第{f_times}次找da_yin结束')
            find_finish('print_finish')
        else:
            logging.info(f'\n********小助手收工！********')
            sys.exit()

    else:  # 找到保存窗口后进行保存
        set_front_hwnd(prt_win_title)
        file_name = time.strftime('%Y%m%d%H%M%S')
        pa.typewrite(file_name)
        pa.press('enter')
        print_info = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), f"----->已保存第{finish_count}份报告\n"
        logging.info(print_info)
        finish_count += 1
        save_pdf()


def find_finish(bn_pic):
    global fail_count, end_sign
    set_front_hwnd("上海市建设工程检测信息管理系统 - 报告打印")
    pf_msg = target_pic(bn_pic)
    while pf_msg is None:  # 没找到“打印结束”
        logging.info(f"弹窗超时检测{fail_count}次")
        fail_count += 1
        save_pdf()
    else:  # 找到“打印结束”
        end_sign = 1
        logging.info("\n********打印结束！********")
        sys.exit()


def go_for_launch():
    log()
    check_sys()
    set_front_hwnd("上海市建设工程检测信息管理系统 - 报告打印")
    click_bn('print_button')
    save_pdf()


if __name__ == '__main__':
    go_for_launch()
