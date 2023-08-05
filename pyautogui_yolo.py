#---------------------------------ウィンドウ表示------------------------------------------------------
import tkinter as tk
from tkinter import messagebox
from tkinter import StringVar
from tkinter import Tk
from tkinter import filedialog
from tkinter import ttk
from tkinter import *
#---------------------------------マウス自動操作------------------------------------------------------
from pynput import mouse
from pynput.keyboard import Key, Listener
import pyautogui
import time
import datetime
#---------------------------------Json------------------------------------------------------
import json#json用
#---------------------------------ChromeDriver------------------------------------------------------
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.action_chains import ActionChains
driver = None
#---------------------------------スレッド------------------------------------------------------
import threading as th
#--------------------------------その他------------------------------------------------------
import re #文字列から数字を取り出す関数
#---------------------------------YOLOv5------------------------------------------------------
import argparse

import os, sys
# limit the number of cpus used by high performance libraries
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import numpy as np
from pathlib import Path
import torch
import torch.backends.cudnn as cudnn

FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]  # yolov5 strongsort root directory
WEIGHTS = ROOT / 'weights'

if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH
if str(ROOT / 'yolov5') not in sys.path:
    sys.path.append(str(ROOT / 'yolov5'))  # add yolov5 ROOT to PATH
if str(ROOT / 'strong_sort') not in sys.path:
    sys.path.append(str(ROOT / 'strong_sort'))  # add strong_sort ROOT to PATH
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative

import logging
from yolov5.models.common import DetectMultiBackend
from yolov5.utils.mybackup.dataloaders_cut import VID_FORMATS, LoadImages, LoadStreams
from yolov5.utils.general import (LOGGER, check_img_size, non_max_suppression, scale_coords, check_requirements, cv2,
                                  check_imshow, xyxy2xywh, increment_path, strip_optimizer, colorstr, print_args, check_file)
from yolov5.utils.torch_utils import select_device, time_sync
from yolov5.utils.plots import Annotator, colors, save_one_box
from strong_sort.utils.parser import get_config
from strong_sort.strong_sort import StrongSORT
#----------------------ウィンドウ表示-------------------------------------------------------------------
window_list = {}#ウィンドウで取得したデータを格納
class MainFrame(ttk.Frame):
    def __init__(self, master):
        #Windowの初期設定を行う
        super().__init__(master)
        self.configure(padding=(6, 4))
        self.pack(expand=1, fill="x", anchor="n")
        self.make_style()
        self.create_widgets()
    
    def make_style(self):
        pass

    def create_widgets(self):#ウィンドウ設定、ボタンやラベルなどの位置や大きさを設定
        font = "MSゴシック"#フォントを設定
        size = 10#フォントのサイズを設定

        #ボタンはLabelみたいにフォント設定できないのでスタイルを作成して設定する
        style_button = ttk.Style()
        style_button.configure("office.TButton", font=(font, 10))
        
        self.label1 = ttk.Label(self, text="仮想カメラ番号", font=(font, size))
        #self.label1.pack(side="left", padx=(0, 2))
        self.label1.grid(row=0, column=0, sticky=tk.W+tk.E)

        path = "/dev/"#ビデオデバイスがあるパス
        self.video_list = []
        for i in os.listdir(path):
            if "video" in i:
                self.video_list.append(i)

        #プルダウン
        self.entry1_var = StringVar()
        #self.entry1 = ttk.Entry(self, textvariable=self.entry1_var, width=32)
        self.entry1 = ttk.Combobox(self,values=self.video_list, font=(font, size), textvariable=self.entry1_var)
        #self.entry1.state(["readonly"])
        #self.entry1.pack(side="left", expand=1, fill="x", padx=(0, 6))
        self.entry1.insert(tk.END, self.video_list[0])#初期値入力
        self.entry1.grid(row=0, column=1, columnspan=2, padx=5, pady=5, sticky=tk.W+tk.E)

        self.label2 = ttk.Label(self, text="Blenderターゲットの名前", font=(font, size))
        #self.label2.pack(side="left", padx=(0, 2))
        self.label2.grid(row=1, column=0, sticky=tk.W+tk.E)

        self.entry2_var = StringVar()
        self.entry2 = ttk.Entry(self, textvariable=self.entry2_var, width=32)
        #self.entry2.state(["readonly"])
        #self.entry2.pack(side="left", expand=1, fill="x", padx=(0, 6))
        self.entry2.insert(tk.END, "target")#初期値入力
        self.entry2.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky=tk.W+tk.E)
        
        #プルダウン
        self.label3 = ttk.Label(self, text="検出する物体の種類", font=(font, size))
        #self.label2.pack(side="left", padx=(0, 2))
        self.label3.grid(row=2, column=0, sticky=tk.W+tk.E)

        #検出できるもの
        self.detect_type_list = ["人", "自転車", "車", "バイク", "飛行機", "バス", "電車", "トラック", "船", "信号", "消火栓", "ストップサイン", "パーキングメーター", "ベンチ", "鳥", "猫", "犬", "馬", "羊", "牛", "ゾウ", "クマ", "シマウマ", "キリン", "バックパック", "傘", "ハンドバッグ", "ネクタイ", "スーツケース", "フリスビー", "スキー", "スノーボード", "スポーツボール", "カイト", "バット", "グローブ", "スケートボード", "サーフボード", "ラケット", "テニス", "ボトル", "ワイングラス", "カップ", "フォーク", "ナイフ", "スプーン", "ボウル", "バナナ", "りんご", "サンドイッチ", "オレンジ", "ブロッコリー", "にんじん", "ホットドッグ", "ピザ", "ドーナツ", "ケーキ", "椅子", "ソファ", "鉢植え", "ベッド", "食卓", "テーブル", "トイレ", "洗面台", "浴槽", "机", "ダイニングテーブル", "トイレ", "テレビ", "ノートパソコン", "マウス", "リモコン", "キーボード", "時計", "電子レンジ", "はさみ", "トースター", "シンク", "歯ブラシ", "冷蔵庫", "本", "オーブン", "花瓶", "テディベア", "ヘアドライヤー"]
        self.entry3_var = StringVar()
        self.entry3 = ttk.Combobox(self,values=self.detect_type_list, font=(font, size), textvariable=self.entry3_var)
        self.entry3.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky=tk.W+tk.E)

        self.label4 = ttk.Label(self, text="ウィンドウ画面座標", font=(font, size))
        #self.label2.pack(side="left", padx=(0, 2))
        self.label4.grid(row=3, column=0, sticky=tk.W+tk.E)

        self.entry4_var = StringVar()
        self.entry4 = ttk.Entry(self, textvariable=self.entry4_var, width=32)
        self.entry4.configure(state='readonly')#書き込み不可
        #self.entry2.state(["readonly"])
        #self.entry2.pack(side="left", expand=1, fill="x", padx=(0, 6))
        self.entry4.grid(row=3, column=1, columnspan=2, padx=5, pady=5, sticky=tk.W+tk.E)

        self.label5 = ttk.Label(self, text="マウス移動可能領域座標", font=(font, size))
        #self.label2.pack(side="left", padx=(0, 2))
        self.label5.grid(row=4, column=0, sticky=tk.W+tk.E)

        self.entry5_var = StringVar()
        self.entry5 = ttk.Entry(self, textvariable=self.entry5_var, width=32)
        self.entry5.configure(state='readonly')#書き込み不可
        #self.entry2.state(["readonly"])
        #self.entry2.pack(side="left", expand=1, fill="x", padx=(0, 6))
        self.entry5.grid(row=4, column=1, columnspan=2, padx=5, pady=5, sticky=tk.W+tk.E)

        self.label6 = ttk.Label(self, text="Blenderスクリプト欄座標", font=(font, size))
        #self.label2.pack(side="left", padx=(0, 2))
        self.label6.grid(row=5, column=0, sticky=tk.W+tk.E)

        self.entry6_var = StringVar()
        self.entry6 = ttk.Entry(self, textvariable=self.entry6_var, width=32)
        self.entry6.configure(state='readonly')#書き込み不可
        #self.entry2.state(["readonly"])
        #self.entry2.pack(side="left", expand=1, fill="x", padx=(0, 6))
        self.entry6.grid(row=5, column=1, columnspan=2, padx=5, pady=5, sticky=tk.W+tk.E)

        self.help_button = ttk.Button(self, text="ヘルプ", style="office.TButton", command=self.run)#styleでフォント設定
        #self.button5.pack(side="left")
        self.help_button.grid(row=6, column=2)
        
        self.button7 = ttk.Button(self, text="座標取得", style="office.TButton", command=self.pos_get_insert)#styleでフォント設定
        #self.button5.pack(side="left")
        self.button7.grid(row=6, column=1, padx=10, pady=5, ipadx=5, ipady=0, sticky=tk.W+tk.E)

        self.button8 = ttk.Button(self, text="開始", style="office.TButton", command=self.execution_dialog)#styleでフォント設定
        #self.button5.pack(side="left")
        self.button8.grid(row=7, column=1, padx=10, pady=5, ipadx=5, ipady=0, sticky=tk.W+tk.E)

    def run(self):
        print("Thread Start!")
        th.Thread(target = self.help_web).start()
    
    def execution_dialog(self):
        print("excution_dialog関数")
        global window_list#ウィンドウで取得したデータを格納
        
        #ウィンドウで取得したデータを格納
        window_list["camera_num"] = re.sub(r"\D", "", self.entry1_var.get())#仮想カメラ番号,番号のみを取り出す
        window_list["target_name"] = self.entry2_var.get()#Blender内のターゲットの名前
        window_list["detect_type"] = self.entry3_var.get()#検出する物体の種類
        window_list["detect_type_num"] = self.list_num_get(self.detect_type_list, self.entry3_var.get())#検出する物体の種類の番号
        
        window_list["moniter_pos"] = self.moniter_pos_list#ウィンドウ画面座標
        window_list["layout_pos_list"] = self.layout_pos_list#マウス移動可能範囲座標
        window_list["mouse_pos_list"] = self.mouse_pos_list#スクリプト欄座標
        self.master.destroy()#このmasterはrootのこと
        #return siten_code

    def list_num_get(self, detect_type_list, detect_type):#検出番号を取得する
        for i in range(len(detect_type_list)):
            if detect_type_list[i] == detect_type:
                return i
        messagebox.showinfo('エラー', '該当する文字列がないため終了してください')
        sys.exit("該当する文字列がないので終了します")

    def pos_get_insert(self):#ウィンドウなどの座標を取得する
        #モニター大きさ取得
        print("モニターの大きさを指定します")
        print("Blenderが写っているモニターの左上と右下をクリックしてください")
        monitor = Monitor_mouse(2)#クリック回数を引数とする
        self.moniter_pos_list = monitor.start()
        self.entry4.configure(state='normal')#書き込み可
        self.entry4.delete(0,tk.END)#テキストボックス内文字列クリア
        self.entry4.insert(tk.END, self.moniter_pos_list)#ウィンドウ画面座標入力
        self.entry4.configure(state='readonly')#書き込み不可

        #マウス移動可能範囲座標取得
        print("マウス移動可能範囲を指定します")
        print("マウス移動可能範囲の左上と右下をクリックしてください")
        monitor = Monitor_mouse(2)#クリック回数を引数とする
        self.layout_pos_list = monitor.start()
        self.entry5.configure(state='normal')#書き込み可
        self.entry5.delete(0,tk.END)#テキストボックス内文字列クリア
        self.entry5.insert(tk.END, self.layout_pos_list)#マウス移動可能範囲座標入力
        self.entry5.configure(state='readonly')#書き込み不可

        #BlenderPythonスクリプト実行ボタン座標取得
        print("スクリプト記入部分をクリックしてください")
        monitor = Monitor_mouse(1)#クリック回数を引数とする
        self.mouse_pos_list = monitor.start()
        self.entry6.configure(state='normal')#書き込み可
        self.entry6.delete(0,tk.END)#テキストボックス内文字列クリア
        self.entry6.insert(tk.END, self.mouse_pos_list)#スクリプト欄座標入力
        self.entry6.configure(state='readonly')#書き込み不可

    def help_web(self):#使い方が書いてあるWEBページに飛ぶ
        driver = webdriver.Chrome(ChromeDriverManager(path="./").install())
        driver.get('https://docs.google.com/document/d/1qQQNEGcFJHJJpZncCeKzcbVp3bROVST3WfJ6fDvbTpg/edit?usp=sharing')
        while True:
            pass
            try:#ブラウザがあるか検知
                driver.find_element(By.XPATH, '//*[@id="docs-branding-logo"]/div')
            except Exception as e:
                #print(e)
                print("ブラウザ削除")
                break
        driver.close()


#----------------------クリック座標関係-------------------------------------------------------------------
class Monitor_mouse:#クリック座標取得クラス
    def __init__(self, in_over_count):#クリック回数を引数とする
        self.counter = 0
        self.over_count = in_over_count
        self.pos_list = []

    def count(self):
        self.counter += 1
        print('Count:{0}'.format(self.counter))

    def is_over(self):
        return True if self.counter >= self.over_count else False

    def call(self):
        self.count()
        if self.is_over():
            print('Done')
            self.listener.stop() # 規定回数過ぎたら終了

    def on_click(self, x, y, button, pressed):
        if pressed:
            print("Pressed at ", (x,y))
            self.pos_list.append((x,y))

        if pressed:
            self.call()

    def start(self):
        with mouse.Listener(
            on_click=self.on_click) as self.listener:
            self.listener.join()
        return self.pos_list
#-----------------キーボード読み取り-------------------------------------------------------------------
stop_Flg = False #Escキーを押したとき終了するための変数
def on_press(key):
    if key == Key.esc:#Escキーを入力すると終了
        # Stop listener
        return False

def on_release(key):
    pass

# Collect events until released
def keystart():
    global stop_Flg
    with Listener(
            on_press=on_press,
            on_release=on_release) as listener:
        listener.join()
    stop_Flg = True

def keyrun():
    print("Thread Start!")
    th.Thread(target = keystart).start()

#-----------------テキスト書き込み-------------------------------------------------------------------
def text_write(fpath, text):#テキスト上書き
    with open(fpath, mode='w') as f:
        f.write(text)

def text_add(fpath, text):#テキスト追記
    with open(fpath, mode='a') as f:
        f.write(text)

def text_read_all(fpath):#テキストすべて読み込み
    with open(fpath) as f:
        s = f.read()
    return s

def text_read_line(fpath):#テキスト一行ずつ読み込み
    with open(fpath) as f:
        text_list = f.readlines()
    return text_list
#---------------可能範囲算出---------------------------------------------------------------------
def drag_pos_get(layout_pos_list, yolo_pos_edit_list):#マウスがドラッグする範囲を計算する
    minx = layout_pos_list[0][0]
    miny = layout_pos_list[0][1]
    maxx = layout_pos_list[1][0]
    maxy = layout_pos_list[1][1]

    return [(possible_pos_get(yolo_pos_edit_list[0][0], minx, maxx), possible_pos_get(yolo_pos_edit_list[0][1], miny, maxy)), (possible_pos_get(yolo_pos_edit_list[1][0], minx, maxx), possible_pos_get(yolo_pos_edit_list[1][1], miny, maxy))]

def possible_pos_get(yolo_pos_edit, min_pos, max_pos):#座標を範囲内に修正する
    if min_pos >= yolo_pos_edit:#yolo座標が最小座標以下
        return min_pos
    elif max_pos <= yolo_pos_edit:#yolo座標が最大以上
        return max_pos
    else:#yolo座標が範囲内
        return yolo_pos_edit
#-------------------------------------------------------------------------------------------------
# remove duplicated stream handler to avoid duplicated logging
logging.getLogger().removeHandler(logging.getLogger().handlers[0])

@torch.no_grad()
def run(
        source='0',
        yolo_weights=WEIGHTS / 'yolov5m.pt',  # model.pt path(s),
        strong_sort_weights=WEIGHTS / 'osnet_x0_25_msmt17.pt',  # model.pt path,
        config_strongsort=ROOT / 'strong_sort/configs/strong_sort.yaml',
        imgsz=(640, 640),  # inference size (height, width)
        conf_thres=0.25,  # confidence threshold
        iou_thres=0.45,  # NMS IOU threshold
        max_det=1000,  # maximum detections per image
        device='',  # cuda device, i.e. 0 or 0,1,2,3 or cpu
        show_vid=False,  # show results
        save_txt=False,  # save results to *.txt
        save_conf=False,  # save confidences in --save-txt labels
        save_crop=False,  # save cropped prediction boxes
        save_vid=False,  # save confidences in --save-txt labels
        nosave=False,  # do not save images/videos
        classes=None,  # filter by class: --class 0, or --class 0 2 3
        agnostic_nms=False,  # class-agnostic NMS
        augment=False,  # augmented inference
        visualize=False,  # visualize features
        update=False,  # update all models
        project=ROOT / 'runs/track',  # save results to project/name
        name='exp',  # save results to project/name
        exist_ok=False,  # existing project/name ok, do not increment
        line_thickness=3,  # bounding box thickness (pixels)
        hide_labels=False,  # hide labels
        hide_conf=False,  # hide confidences
        hide_class=False,  # hide IDs
        half=False,  # use FP16 half-precision inference
        dnn=False,  # use OpenCV DNN for ONNX inference
):

    global stop_Flg #Escキーを押したとき終了するための変数
    keyrun()#スレッド開始
    #---------------------------------座標指定--------------------------------
    root = Tk()
    root.title('3Dモデル抽出システム')
    frame = MainFrame(master = root)
    # ウィンドウの表示開始
    frame.mainloop()
    time.sleep(2)

    #以下の書き方でウィンドウクラス内の戻り値を取得できる
    #a = frame.execution_dialog()
    #print(a)
    
    global window_list#ウィンドウで取得したデータを格納
    print(window_list)

    moniter_pos_list = window_list["moniter_pos"]#ウィンドウ画面座標
    layout_pos_list = window_list["layout_pos_list"]#マウス移動可能範囲座標
    mouse_pos_list = window_list["mouse_pos_list"]#スクリプト欄座標
    #------------------------前準備------------------------------------
    bcount = 0#Blenderでスクリプトを実行させた回数
    detectionFlg = False#検知したかどうか
    bfpath = '/home/omi/blenderpy/write.txt'#BlenderとYOLOをつなぐテキストパス
    bfpath_pre = '/home/omi/blenderpy/write_pre.txt'#BlenderとYOLOをつなぐテキストパス、一番最初にだけ読み込まれる、Blenderで処理するオブジェクトの名前を記入するためにある。
    bfpath_all = '/home/omi/blenderpy/allLog.txt'#すべてのログを記録する
    text_write(bfpath, "Blenderの準備:True\n")#テキスト上書き
    text_write(bfpath_pre, window_list["target_name"])#テキスト上書き
    text_add(bfpath, str(bcount) + "\n")#テキスト追記
    #一応すべて記録するためのログ
    text_add(bfpath_all, "Blenderの準備:True\n")#テキスト上書き
    text_add(bfpath_all, str(bcount) + "\n")#テキスト追記
    #スクリプト画面をクリック
    pyautogui.click(mouse_pos_list[0][0], mouse_pos_list[0][1], button="left")
    time.sleep(0.1)
    # altを押した状態でpを入力
    pyautogui.hotkey("alt", "p")
    #--------------------------------------------------------------------------
    #source = str(source)
    source = str(window_list["camera_num"])
    save_img = not nosave and not source.endswith('.txt')  # save inference images
    is_file = Path(source).suffix[1:] in (VID_FORMATS)
    is_url = source.lower().startswith(('rtsp://', 'rtmp://', 'http://', 'https://'))
    webcam = source.isnumeric() or source.endswith('.txt') or (is_url and not is_file)
    if is_url and is_file:
        source = check_file(source)  # download

    # Directories
    if not isinstance(yolo_weights, list):  # single yolo model
        exp_name = str(yolo_weights).rsplit('/', 1)[-1].split('.')[0]
    elif type(yolo_weights) is list and len(yolo_weights) == 1:  # single models after --yolo_weights
        exp_name = yolo_weights[0].split(".")[0]
    else:  # multiple models after --yolo_weights
        exp_name = 'ensemble'
    exp_name = name if name is not None else exp_name + "_" + str(strong_sort_weights).split('/')[-1].split('.')[0]
    save_dir = increment_path(Path(project) / exp_name, exist_ok=exist_ok)  # increment run
    (save_dir / 'tracks' if save_txt else save_dir).mkdir(parents=True, exist_ok=True)  # make dir

    # Load model
    device = select_device(device)
    model = DetectMultiBackend(yolo_weights, device=device, dnn=dnn, data=None, fp16=half)
    stride, names, pt = model.stride, model.names, model.pt
    imgsz = check_img_size(imgsz, s=stride)  # check image size

    # Dataloader
    if webcam:
        show_vid = check_imshow()
        cudnn.benchmark = True  # set True to speed up constant image size inference
        dataset = LoadStreams(source, img_size=imgsz, stride=stride, auto=pt)
        nr_sources = len(dataset)
    else:
        dataset = LoadImages(source, img_size=imgsz, stride=stride, auto=pt)
        nr_sources = 1
    vid_path, vid_writer, txt_path = [None] * nr_sources, [None] * nr_sources, [None] * nr_sources

    # initialize StrongSORT
    cfg = get_config()
    cfg.merge_from_file(opt.config_strongsort)

    # Create as many strong sort instances as there are video sources
    strongsort_list = []
    for i in range(nr_sources):
        strongsort_list.append(
            StrongSORT(
                strong_sort_weights,
                device,
                max_dist=cfg.STRONGSORT.MAX_DIST,
                max_iou_distance=cfg.STRONGSORT.MAX_IOU_DISTANCE,
                max_age=cfg.STRONGSORT.MAX_AGE,
                n_init=cfg.STRONGSORT.N_INIT,
                nn_budget=cfg.STRONGSORT.NN_BUDGET,
                mc_lambda=cfg.STRONGSORT.MC_LAMBDA,
                ema_alpha=cfg.STRONGSORT.EMA_ALPHA,

            )
        )
    outputs = [None] * nr_sources
    #--------------------------------------------------------------------------
    # Run tracking
    model.warmup(imgsz=(1 if pt else nr_sources, 3, *imgsz))  # warmup
    dt, seen = [0.0, 0.0, 0.0, 0.0], 0
    curr_frames, prev_frames = [None] * nr_sources, [None] * nr_sources
    for frame_idx, (path, im, im0s, vid_cap, s) in enumerate(dataset):
        if stop_Flg:#escキーが押されたらプログラムを終了
            text_write(bfpath, "Blenderの準備:True\n")#次の開始のためにEndからTrueに上書きしておく
            sys.exit("ESCキーが押されたのでプログラムを終了します")
        if "Fale" in text_read_line(bfpath)[0]:
            print("Blender側の処理がまだです")
            continue
        elif "End" in text_read_line(bfpath)[0]:
            print("処理は完了しました")
            text_write(bfpath, "Blenderの準備:True\n")#次の開始のためにEndからTrueに上書きしておく
            return

        t1 = time_sync()
        im = torch.from_numpy(im).to(device)
        im = im.half() if half else im.float()  # uint8 to fp16/32
        im /= 255.0  # 0 - 255 to 0.0 - 1.0
        if len(im.shape) == 3:
            im = im[None]  # expand for batch dim
        t2 = time_sync()
        dt[0] += t2 - t1

        # Inference
        visualize = increment_path(save_dir / Path(path[0]).stem, mkdir=True) if opt.visualize else False
        pred = model(im, augment=opt.augment, visualize=visualize)
        t3 = time_sync()
        dt[1] += t3 - t2

        # Apply NMS
        #pred = non_max_suppression(pred, opt.conf_thres, opt.iou_thres, opt.classes, opt.agnostic_nms, max_det=opt.max_det)
        pred = non_max_suppression(pred, opt.conf_thres, opt.iou_thres, int(window_list["detect_type_num"]), opt.agnostic_nms, max_det=opt.max_det)
        dt[2] += time_sync() - t3

        #辞書宣言
        pos = {}
        obj = {}

        # Process detections
        for i, det in enumerate(pred):  # detections per image
            seen += 1
            if webcam:  # nr_sources >= 1
                p, im0, _ = path[i], im0s[i].copy(), dataset.count
                p = Path(p)  # to Path
                s += f'{i}: '
                txt_file_name = p.name
                save_path = str(save_dir / p.name)  # im.jpg, vid.mp4, ...
            else:
                p, im0, _ = path, im0s.copy(), getattr(dataset, 'frame', 0)
                p = Path(p)  # to Path
                # video file
                if source.endswith(VID_FORMATS):
                    txt_file_name = p.stem
                    save_path = str(save_dir / p.name)  # im.jpg, vid.mp4, ...
                # folder with imgs
                else:
                    txt_file_name = p.parent.name  # get folder name containing current img
                    save_path = str(save_dir / p.parent.name)  # im.jpg, vid.mp4, ...
            curr_frames[i] = im0

            txt_path = str(save_dir / 'tracks' / txt_file_name)  # im.txt
            s += '%gx%g ' % im.shape[2:]  # print string
            imc = im0.copy() if save_crop else im0  # for save_crop

            annotator = Annotator(im0, line_width=2, pil=not ascii)
            if cfg.STRONGSORT.ECC:  # camera motion compensation
                strongsort_list[i].tracker.camera_update(prev_frames[i], curr_frames[i])

            if det is not None and len(det):
                # Rescale boxes from img_size to im0 size
                det[:, :4] = scale_coords(im.shape[2:], det[:, :4], im0.shape).round()

                # Print results
                for c in det[:, -1].unique():
                    n = (det[:, -1] == c).sum()  # detections per class
                    s += f"{n} {names[int(c)]}{'s' * (n > 1)}, "  # add to string

                xywhs = xyxy2xywh(det[:, 0:4])
                confs = det[:, 4]
                clss = det[:, 5]

                # pass detections to strongsort
                t4 = time_sync()
                outputs[i] = strongsort_list[i].update(xywhs.cpu(), confs.cpu(), clss.cpu(), im0)
                t5 = time_sync()
                dt[3] += t5 - t4
                
                cap_w = int(vid_cap.get(cv2.CAP_PROP_FRAME_WIDTH))#YOLO上での画面の横幅
                cap_h = int(vid_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))#YOLO上での画面の高さ
                pos_raito = int(moniter_pos_list[1][0]) / int(cap_w)#モニター座標とYOLO座標での比率

                print("===============================================")
                print("検知数:" + str(len(outputs[0])))#outputs[0]が検知している物体の数

                # draw boxes for visualization
                yolo_pos_edit_list = []
                yolo_pos_edit_list_mini = []
                if len(outputs[i]) > 0:
                    for j, (output, conf) in enumerate(zip(outputs[i], confs)):

                        pos["obj" + str(j)] = {}
                        obj["lx"] = int(output[0]*pos_raito)#left_x
                        obj["ly"] = int(output[1]*pos_raito)#left_y
                        obj["rx"] = int(output[2]*pos_raito)#right_x
                        obj["ry"] = int(output[3]*pos_raito)#right_y
                        obj["track_id"] = int(output[4])#トラッキングID
                        obj["obj_id"] = int(output[5])#物体ID
                        pos["obj" + str(j)].update(obj)
                        #add_rn = 15#バウンディングボックスよりすこし大きめにをもたせて切り取り座標を決める
                        yolo_pos_edit_list_mini = [(int(output[0]*pos_raito - 5), int(output[1]*pos_raito + 15)),(int(output[2]*pos_raito + 5), int(output[3]*pos_raito + 18))]
                        print(yolo_pos_edit_list_mini)

                        bboxes = output[0:4]
                        id = output[4]
                        cls = output[5]

                        if save_txt:
                            # to MOT format
                            bbox_left = output[0]
                            bbox_top = output[1]
                            bbox_w = output[2] - output[0]
                            bbox_h = output[3] - output[1]
                            # Write MOT compliant results to file
                            with open(txt_path + '.txt', 'a') as f:
                                f.write(('%g ' * 10 + '\n') % (frame_idx + 1, id, bbox_left,  # MOT format
                                                               bbox_top, bbox_w, bbox_h, -1, -1, -1, i))

                        if save_vid or save_crop or show_vid:  # Add bbox to image
                            c = int(cls)  # integer class
                            id = int(id)  # integer id
                            label = None if hide_labels else (f'{id} {names[c]}' if hide_conf else \
                                (f'{id} {conf:.2f}' if hide_class else f'{id} {names[c]} {conf:.2f}'))
                            annotator.box_label(bboxes, label, color=colors(c, True))
                            if save_crop:
                                txt_file_name = txt_file_name if (isinstance(path, list) and len(path) > 1) else ''
                                save_one_box(bboxes, imc, file=save_dir / 'crops' / txt_file_name / names[c] / f'{id}' / f'{p.stem}.jpg', BGR=True)
                    yolo_pos_edit_list.append(yolo_pos_edit_list_mini)
                LOGGER.info(f'{s}Done. YOLO:({t3 - t2:.3f}s), StrongSORT:({t5 - t4:.3f}s)')
                detectionFlg = True#検知できた
            else:
                detectionFlg = False#検知できなかった
                strongsort_list[i].increment_ages()
                LOGGER.info('No detections')

            # Stream results
            im0 = annotator.result()
            if show_vid:
                cv2.putText(im0, str(datetime.datetime.now()), (10, 30),
                    cv2.FONT_HERSHEY_PLAIN, 1.5,
                    (255, 255, 255), 1, cv2.LINE_AA)
                cv2.imshow(str(p), im0)
                cv2.waitKey(1)  # 1 millisecond

            # Save results (image with detections)
            if save_vid:
                if vid_path[i] != save_path:  # new video
                    vid_path[i] = save_path
                    if isinstance(vid_writer[i], cv2.VideoWriter):
                        vid_writer[i].release()  # release previous video writer
                    if vid_cap:  # video
                        fps = vid_cap.get(cv2.CAP_PROP_FPS)
                        w = int(vid_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                        h = int(vid_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    else:  # stream
                        fps, w, h = 30, im0.shape[1], im0.shape[0]
                    save_path = str(Path(save_path).with_suffix('.mp4'))  # force *.mp4 suffix on results videos
                    vid_writer[i] = cv2.VideoWriter(save_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))
                vid_writer[i].write(im0)

            prev_frames[i] = curr_frames[i]

            print(pos)
            bcount += 1
            pos_json = json.dumps(pos)#json形式に変換
            text_write(bfpath, "Blenderの準備:False\n")#テキスト上書き
            text_add(bfpath, str(bcount) + "\n")#テキスト追記
            text_add(bfpath, pos_json + "\n")#テキスト追記
            #一応すべて記録するためのログ
            text_add(bfpath_all, "Blenderの準備:False\n")#テキスト上書き
            text_add(bfpath_all, str(bcount) + "\n")#テキスト追記
            text_add(bfpath_all, pos_json + "\n")#テキスト追記

            if len(pos) > 0 and detectionFlg :#検知していた場合
                print("物体を検知したので切り取りを行います")
                #編集モードに切り替え
                pyautogui.moveTo(layout_pos_list[0][0], layout_pos_list[0][1])# マウスを移動可能範囲の左上に移動
                pyautogui.press("tab")
                time.sleep(1)
                #マウス移動可能範囲をドラッグして、すべてのオブジェクトを選択
                pyautogui.moveTo(layout_pos_list[0][0], layout_pos_list[0][1])# マウスを移動可能範囲の左上に移動
                pyautogui.dragTo(layout_pos_list[1][0], layout_pos_list[1][1], duration=1, button="left")#左ボタンを押しながら、マウスを移動可能範囲の右下までドラッグ
                #バウンディングボックス内だけをドラッグし、特定オブジェクトの選択を外す
                #print(yolo_pos_edit_list)
                drag_pos_list = drag_pos_get(layout_pos_list, yolo_pos_edit_list[0])#マウスがドラッグする範囲を計算する、ここあとで複数個対応できるように変更する。リスト0ではなくfor文などで順番に切り抜けるようにする
                print(drag_pos_list)
                pyautogui.moveTo(drag_pos_list[0][0], drag_pos_list[0][1])# マウスをバウンディングボックスの左上に移動
                time.sleep(1)
                pyautogui.keyDown('ctrl')
                time.sleep(1)
                pyautogui.dragTo(drag_pos_list[1][0], drag_pos_list[1][1], duration=1, button="left")# 左ボタンを押しながら、マウスをバウンディングボックスの右下までドラッグ
                time.sleep(1)
                pyautogui.keyUp('ctrl')
                time.sleep(1)
                #オブジェクト削除
                pyautogui.press("delete")
                time.sleep(1)
                pyautogui.press("enter")
                time.sleep(1)
                #編集モードから通常モードに切り替え
                pyautogui.press("tab")
                time.sleep(0.5)
            # Blenderスクリプト画面を一回左クリック
            time.sleep(2)#youtubeに反映されるまでの時間待機
            pyautogui.click(mouse_pos_list[0][0], mouse_pos_list[0][1], button="left")
            time.sleep(0.1)
            # altを押した状態でpを入力
            pyautogui.hotkey("alt", "p")
            time.sleep(2)

    # Print results
    t = tuple(x / seen * 1E3 for x in dt)  # speeds per image
    LOGGER.info(f'Speed: %.1fms pre-process, %.1fms inference, %.1fms NMS, %.1fms strong sort update per image at shape {(1, 3, *imgsz)}' % t)
    if save_txt or save_vid:
        s = f"\n{len(list(save_dir.glob('tracks/*.txt')))} tracks saved to {save_dir / 'tracks'}" if save_txt else ''
        LOGGER.info(f"Results saved to {colorstr('bold', save_dir)}{s}")
    if update:
        strip_optimizer(yolo_weights)  # update model (to fix SourceChangeWarning)


def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument('--yolo-weights', nargs='+', type=str, default=WEIGHTS / 'yolov5m.pt', help='model.pt path(s)')
    parser.add_argument('--strong-sort-weights', type=str, default=WEIGHTS / 'osnet_x0_25_msmt17.pt')
    parser.add_argument('--config-strongsort', type=str, default='strong_sort/configs/strong_sort.yaml')
    parser.add_argument('--source', type=str, default='0', help='file/dir/URL/glob, 0 for webcam')  
    parser.add_argument('--imgsz', '--img', '--img-size', nargs='+', type=int, default=[640], help='inference size h,w')
    parser.add_argument('--conf-thres', type=float, default=0.5, help='confidence threshold')
    parser.add_argument('--iou-thres', type=float, default=0.5, help='NMS IoU threshold')
    parser.add_argument('--max-det', type=int, default=1000, help='maximum detections per image')
    parser.add_argument('--device', default='', help='cuda device, i.e. 0 or 0,1,2,3 or cpu')
    parser.add_argument('--show-vid', action='store_true', help='display tracking video results')
    parser.add_argument('--save-txt', action='store_true', help='save results to *.txt')
    parser.add_argument('--save-conf', action='store_true', help='save confidences in --save-txt labels')
    parser.add_argument('--save-crop', action='store_true', help='save cropped prediction boxes')
    parser.add_argument('--save-vid', action='store_true', help='save video tracking results')
    parser.add_argument('--nosave', action='store_true', help='do not save images/videos')
    # class 0 is person, 1 is bycicle, 2 is car... 79 is oven
    parser.add_argument('--classes', nargs='+', type=int, help='filter by class: --classes 0, or --classes 0 2 3')
    parser.add_argument('--agnostic-nms', action='store_true', help='class-agnostic NMS')
    parser.add_argument('--augment', action='store_true', help='augmented inference')
    parser.add_argument('--visualize', action='store_true', help='visualize features')
    parser.add_argument('--update', action='store_true', help='update all models')
    parser.add_argument('--project', default=ROOT / 'runs/track', help='save results to project/name')
    parser.add_argument('--name', default='exp', help='save results to project/name')
    parser.add_argument('--exist-ok', action='store_true', help='existing project/name ok, do not increment')
    parser.add_argument('--line-thickness', default=3, type=int, help='bounding box thickness (pixels)')
    parser.add_argument('--hide-labels', default=False, action='store_true', help='hide labels')
    parser.add_argument('--hide-conf', default=False, action='store_true', help='hide confidences')
    parser.add_argument('--hide-class', default=False, action='store_true', help='hide IDs')
    parser.add_argument('--half', action='store_true', help='use FP16 half-precision inference')
    parser.add_argument('--dnn', action='store_true', help='use OpenCV DNN for ONNX inference')
    opt = parser.parse_args()
    opt.imgsz *= 2 if len(opt.imgsz) == 1 else 1  # expand
    print_args(vars(opt))
    return opt


def main(opt):
    check_requirements(requirements=ROOT / 'requirements.txt', exclude=('tensorboard', 'thop'))
    run(**vars(opt))


if __name__ == "__main__":
    opt = parse_opt()
    main(opt)
