# bpyインポート
import bpy
# 型インポート
from mathutils import Vector
from mathutils import Quaternion
# 角度計算のため
import math
# copyインポート(参照型のコピーのため)
import copy

def ob_location(arg_objectname="Default", x=0, y=0, z=0):#特定のオブジェクトを座標移動させる
    # 他のオブジェクトに操作を適用しないよう全てのオブジェクトを走査する
    for ob in bpy.context.scene.objects:
        # 非選択状態に設定する
        ob.select_set(False)

    # 指定オブジェクトを取得する
    # (get関数は対象が存在しない場合 None が返る)
    selectob = bpy.data.objects.get(arg_objectname)

    # 指定オブジェクトが存在するか確認する
    if selectob == None:
        # 指定オブジェクトが存在しない場合は処理しない
        return False

    # 変更オブジェクトをアクティブに変更する
    bpy.context.view_layer.objects.active = selectob

    #アクティブオブジェクトを取得
    #obj = bpy.context.scene.objects.active

    #オブジェクトを移動させる
    selectob.location = (float(x), float(y), float(z))
    
    return True


def ob_rotation(arg_objectname="Default", x=0, y=0, z=0):#特定のオブジェクトを回転させる
    # 他のオブジェクトに操作を適用しないよう全てのオブジェクトを走査する
    for ob in bpy.context.scene.objects:
        # 非選択状態に設定する
        ob.select_set(False)
    # 指定オブジェクトを取得する
    selectob = bpy.data.objects.get(arg_objectname)
    # 指定オブジェクトが存在するか確認する
    if selectob == None:
        # 指定オブジェクトが存在しない場合は処理しない
        return False
    # 変更オブジェクトをアクティブに変更する
    bpy.context.view_layer.objects.active = selectob
    #オブジェクトを回転させる
    selectob.rotation_euler[0] = (math.radians(float(x)))
    selectob.rotation_euler[1] = (math.radians(float(y)))
    selectob.rotation_euler[2] = (math.radians(float(z)))
    return True

def ob_scale(arg_objectname="Default", x=0, y=0, z=0):#特定のオブジェクトのスケール変更させる
    # 他のオブジェクトに操作を適用しないよう全てのオブジェクトを走査する
    for ob in bpy.context.scene.objects:
        # 非選択状態に設定する
        ob.select_set(False)
    # 指定オブジェクトを取得する
    selectob = bpy.data.objects.get(arg_objectname)
    # 指定オブジェクトが存在するか確認する
    if selectob == None:
        # 指定オブジェクトが存在しない場合は処理しない
        return False
    # 変更オブジェクトをアクティブに変更する
    bpy.context.view_layer.objects.active = selectob
    #オブジェクトを移動させる
    selectob.scale = (float(x), float(y), float(z))
    return True

def convert_transform_eulerdegrees(arg_objectname="Default") -> dict:#指定オブジェクトの位置座標、回転(オイラー角、degree)、スケール情報を辞書型で返す。各数字は一定のところで四捨五入して返している。
    # 他のオブジェクトに操作を適用しないよう全てのオブジェクトを走査する
    for ob in bpy.context.scene.objects:
        # 非選択状態に設定する
        ob.select_set(False)
    # 指定オブジェクトを取得する
    selectob = bpy.data.objects.get(arg_objectname)
    # 指定オブジェクトが存在するか確認する
    if selectob == None:
        # 指定オブジェクトが存在しない場合は処理しない
        return False
    # 変更オブジェクトをアクティブに変更する
    bpy.context.view_layer.objects.active = selectob
    #辞書作成
    transform = {}
    #位置座標取得
    transform["location"] = [round(selectob.location[0], 2), round(selectob.location[1], 2), round(selectob.location[2], 2)]
    #角度取得
    transform["rotation"] = [round(math.degrees(selectob.rotation_euler[0]), 2), round(math.degrees(selectob.rotation_euler[1]), 2), round(math.degrees(selectob.rotation_euler[2]), 2)]
    #位置座標取得
    transform["scale"] = [round(selectob.scale[0], 3), round(selectob.scale[1], 3), round(selectob.scale[2], 3)]
    return transform

def set_origin_geometry(arg_objectname='Default'):#中心座標を変更
  # 他のオブジェクトの寸法を適用しないよう全てのオブジェクトを走査する
  for ob in bpy.context.scene.objects:
    # 非選択状態に設定する
    ob.select_set(False)
  # 指定オブジェクトを取得する
  selectob = bpy.data.objects[arg_objectname]
  # 変更オブジェクトをアクティブに変更する
  bpy.context.view_layer.objects.active  = selectob
  # 変更オブジェクトを選択状態にする  
  selectob.select_set(True)
  # オブジェクトの原点を3Dカーソル位置に移動する
  bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
  return

def set_mode_object() -> bool:#すべてのオブジェクトをオブジェクトモードにする
    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
    return True

def text_write(fpath, text):#テキスト上書き
    with open(fpath, mode='w') as f:
        f.write(text)

def text_add(fpath, text):#テキスト追記
    with open(fpath, mode='a') as f:
        #f.write('\nFour')
        f.write(text)

def text_read_all(fpath):#テキストすべて読み込み
    with open(fpath) as f:
        s = f.read()
        print(s)
    return s

def text_read_line(fpath):#テキスト一行ずつ読み込み
    with open(fpath) as f:
        text_list = f.readlines()
        print(text_list)
    return text_list

fpath = '/home/omi/blenderpy/write.txt' #pyautogui_yolo.pyと連携するためのテキストファイル
fpath_pre = '/home/omi/blenderpy/write_pre.txt'#BlenderとYOLOをつなぐテキストパス、一番最初にだけ読み込まれる、Blenderで処理するオブジェクトの名前を記入するためにある。
fpath_all = '/home/omi/blenderpy/allLog.txt'#すべてのログを記録する
object_name = text_read_line(fpath_pre)[0] #切り抜き対象オブジェクトの名前

if text_read_line(fpath)[1] == "0\n":#一番最初だけ実行
    set_mode_object()#すべてのオブジェクトをオブジェクトモードにする
    set_origin_geometry(object_name)#原点を中心に持ってくる
    ob_location(object_name, 0, 0, 0)#特定のオブジェクトを座標移動させる。x,y,zで指定した座標になる。
    ob_rotation(object_name, 90, 0, 0)#オブジェクトを回転をリセットする

if convert_transform_eulerdegrees(object_name)["rotation"][2] > 360:
    set_origin_geometry(object_name)#原点を中心に持ってくる
    ob_location(object_name, 0, 0, 0)#特定のオブジェクトを座標移動させる
    ob_rotation(object_name, 90, 0, 0)#オブジェクトを回転をリセットする
    text_write(fpath, "End")#テキスト上書き
    text_add(fpath_all, "End")#テキスト追記
else:
    print(text_read_all(fpath))#テキストすべて読み込み
    bcount = int(text_read_line(fpath)[1])
    ob_rotation(object_name, 90, 0, 10 * bcount)#オブジェクトを回転
    text_write(fpath, "Blenderの準備:True\n")#テキスト上書き
    text_add(fpath_all, "Blenderの準備:True\n")#テキスト追記
