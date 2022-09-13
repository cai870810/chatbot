# -*- coding: UTF-8 -*- 

import re
import flask
from flask_sqlalchemy import SQLAlchemy
from flask import jsonify
from flask import request
from flask import make_response
from flask import render_template
from flask import Flask
import json
from ftplib import FTP
import os
import time
from datetime import datetime
from datetime import date
from datetime import timedelta
import jieba
from pymysql import Date

jieba.load_userdict('d:/NLP/userdict.txt')

def entry_to_list(entry_sentence):
    entry = jieba.cut(entry_sentence, cut_all=False)
    entry_list = list(entry)
    return entry_list

def str5(str0):
    str_ = str0 + '的動作是? 1. 開啟A' + str0 + ' 2. 關閉A' + str0 + ' 3. 開啟B' + str0 + ' 4. 關閉B' + str0 + ',若取消輸入則輸入no'
    return str_

db = SQLAlchemy()

app = Flask(__name__)

# 連線到資料庫
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
# engine_container = db.get_engine(app)

# 聊天機器人
@app.route('/Recommend', methods = ['POST'])
def recommend():
    # 取得POST資料
    request_recommend = request.get_json()

    # 使用者輸入
    entry = request_recommend['Message']
    user = request_recommend['User']

    # 使用jieba斷句
    entry_list = entry_to_list(entry)
    print(entry_list)

    # 環境前置
    str1 = '根據您的經驗，此預測分析狀態為:1.OO狀態 2.OO狀態 3.OO狀態'
    str2 = '感謝您寶貴的經驗，有沒有建議處理的方法(選項1: 有，選項2: 無)'
    str3 = '環境方面(選項1: 排風扇、選項2: 噴霧、選項3: 水濂、選項4: 內循環風扇)'
    str4 = '感謝您寶貴的經驗!'
    control = [{
        '1':None,
        '2':None,
        '3':None,
        '4':None
    }]
    options = {
        '1':None,
        '2':None,
        '3':None,
        '4':None
    }
    str6 = '還有需要調整的嗎?(選項1: 排風扇、選項2: 噴霧、選項3: 水濂、選項4: 內循環風扇) 若無需調整請輸入no，紀錄將上傳'
    option = ['排風扇','噴霧','水濂','內循環風扇']

    # 死雞前置
    keyword1 = ['死','死雞','病死','病死雞','病死禽']
    keyword2 = ['下雞','淘汰']
    keyword3 = ['公雞','公','公的']
    keyword4 = ['母雞','母','母的']
    keyword5 = ['正確','確定','對','沒錯','沒問題']
    keyword6 = ['錯誤','不','不正確']

    data = 'd:/NLP/NLP_recommend_' + user + '.json'

    try:
        # 嘗試讀取檔案
        with open(data,'r', encoding='utf-8') as f:
            output = json.load(f)
            print('舊資料')
    except FileNotFoundError:
        output = {
            "Message" : None,
            "Mode" : None,
            "Status" : None,
            "Recommendation" : None,
            "Record" : None,
            "ReRecord" : None,
            "Male" : None,
            "Female" : None,
            "Date" : None,
            "House_No" : None,
            "Feeding_Lot" : None
        }
        # 若無此檔案，則新建一個
        with open(data,'w', encoding='utf-8') as f:
            f.writelines(json.dumps(output))
            print('新建')
    
    # 輸入取消則刪除紀錄檔案
    for res in entry_list:
        if res == '取消':
            output['Message'] = "已取消"
            os.remove(data)
            return jsonify({"Code":0,"Message":None,"Result":output})
        elif res.upper() == 'HELLO':
            output['Message'] = '你好，我有什麼可以幫你的嗎?'
            os.remove(data)
            return jsonify({"Code":0,"Message":None,"Result":output})

    # yes or no
    if output['Mode'] is None:
        for res in entry_list:
            if res.upper() == 'YES':
                output['Mode'] = '環境控制'
                output['Message'] = str1
                '''
                資料庫查詢回復訊息，查詢有哪些狀態(str1)
                '''
                print(output)
                with open(data,'w', encoding='utf-8') as f:
                    f.writelines(json.dumps(output))
                return jsonify({"Code":0,"Message":None,"Result":output})
            elif res.upper() == 'NO':
                output['Mode'] = res.upper()
                output['Message'] = "(再次傳送錯誤訊息)"
                print(output)
                os.remove(data)
                return jsonify({"Code":0,"Message":None,"Result":output})
            elif res in keyword1:
                output['Mode'] = '死亡'
                break
            elif res in keyword2:
                output['Mode'] = '淘汰'
                break
    
    # 環境控制
    if output['Mode'] == '環境控制':
        if output['Status'] is None:
            for res in entry_list:
                if res == '1' or res == '2' or res == '3':
                    output['Status'] = res
                    output['Message'] = str2
                    print(output)
                    with open(data,'w', encoding='utf-8') as f:
                        f.writelines(json.dumps(output))
                    return jsonify({"Code":0,"Message":None,"Result":output})

        # 有沒有解決方法
        if output['Status'] is not None and output['Recommendation'] is None:
            for res in entry_list:
                if res == '1':
                    output['Recommendation'] = control
                    output['Message'] = str3
                    '''
                    資料庫查詢回復訊息，查詢控制方法(str3)
                    '''
                    print(output)
                    with open(data,'w', encoding='utf-8') as f:
                        f.writelines(json.dumps(output))
                    return jsonify({"Code":0,"Message":None,"Result":output})
                if res == '2':
                    output['Recommendation'] = res
                    output['Message'] = str4
                    print(output)
                    with open(data,'w', encoding='utf-8') as f:
                        f.writelines(json.dumps(output))
                    '''
                    看要不要上傳至資料庫，要的話在這裡
                    '''
                    os.remove(data)
                    return jsonify({"Code":0,"Message":None,"Result":output})
        
        # 要控制哪一項並記錄
        if output['Recommendation'] is not None and output['Record'] is None:
            for res in entry_list:
                try:
                    if output['Recommendation'][0][res] is None:
                        output['Recommendation'][0][res] = options
                        output['Record'] = res
                        output['Message'] = str5(option[int(res)-1])
                        print(output)
                        with open(data,'w', encoding='utf-8') as f:
                            f.writelines(json.dumps(output))
                        return jsonify({"Code":0,"Message":None,"Result":output})

                    if output['Recommendation'][0][res] is not None:
                        output['Record'] = res
                        output['ReRecord'] = '1'
                        output['Message'] = "此選項已有輸入資料，請問需要重新填入嗎?(需要請輸入：yes，不需要請輸入：no)"
                        print(output)
                        with open(data,'w', encoding='utf-8') as f:
                            f.writelines(json.dumps(output))
                        return jsonify({"Code":0,"Message":None,"Result":output})

                except KeyError:
                    pass
                
                # 若無需再紀錄
                if res.upper() == 'NO' or res.upper() == 'N':
                    output['Message'] = "好的，資料上傳成功"
                    with open(data,'w', encoding='utf-8') as f:
                        f.writelines(json.dumps(output))
                    # 上傳

                    os.remove(data)
                    return jsonify({"Code":0,"Message":None,"Result":output})

        # 怎樣控制
        if output['Record'] is not None and output['ReRecord'] is None:
            for res in entry_list:
                if res.upper() == 'NO':
                    output['Recommendation'][0][output['Record']] = None
                    output['Record'] = None
                    output['Message'] = str6
                    print(output)
                    with open(data,'w', encoding='utf-8') as f:
                        f.writelines(json.dumps(output))
                    return jsonify({"Code":0,"Message":None,"Result":output})
                if res == '1' or res == '2' or res == '3' or res == '4' :  #1到4選項
                    output['Recommendation'][0][output['Record']][res] = '1'
            output['Record'] = None
            output['Message'] = str6
            print(output)
            with open(data,'w', encoding='utf-8') as f:
                f.writelines(json.dumps(output))
            return jsonify({"Code":0,"Message":None,"Result":output})

        # 是否重新輸入控制選項
        if output['Record'] is not None and output['ReRecord'] is not None:
            for res in entry_list:
                if res.upper() == 'YES':
                    output['Recommendation'][0][output['Record']] = options
                    output['ReRecord'] = None
                    output['Message'] = str5(option[int(output['Record'])-1])
                    print(output)
                    with open(data,'w', encoding='utf-8') as f:
                        f.writelines(json.dumps(output))
                    return jsonify({"Code":0,"Message":None,"Result":output})

                if res.upper() == 'NO':
                    output['Record'] = None
                    output['ReRecord'] = None
                    output['Message'] = "取消調整，" + str6
                    print(output)
                    with open(data,'w', encoding='utf-8') as f:
                        f.writelines(json.dumps(output))
                    return jsonify({"Code":0,"Message":None,"Result":output})

        output['Message'] = "輸入資料有誤，請再次輸入"
        return jsonify({"Code":-1,"Message":None,"Result":output})

    # 輸入死雞
    if output['Mode'] == '死亡' or output['Mode'] == '淘汰':
        if output['Feeding_Lot'] is None:
            # 連線到資料庫

            # 查詢使用者對應場域資訊
            # 先到Breeder找場域名稱
            sql_cmd = "SELECT * FROM Breeder WHERE Staff_ID = '" + user + "'"
            query_data = db.engine.execute(sql_cmd)
            staff_field = []
            for row in query_data:
                staff_field.append(row['Field_ID'])
            print(staff_field)
            if staff_field == []:
                return {"Code":0,"Message":"查無此使用者","Result":None}
            # 再到Lookup找DB名稱
            sql_cmd_lookup = "SELECT * FROM Lookup WHERE Field_ID = '" + staff_field[0] + "'"
            query_data_lookup = db.engine.execute(sql_cmd_lookup)
            DBName = []
            for row in query_data_lookup:
                DBName.append(row['DBName'])
            # 若找不到對應場域，回傳錯誤訊息
            if DBName == []:
                return {"Code":0,"Message":"查無此場域","Result":None}
            # clean DB
            cleanup(db.session)
            # 連線至使用者對應場域
            
            # 找到最新一筆飼養批次
            sql_cmd_batch = "SELECT House_No, Feeding_Lot, Staff_ID,\
                MAX(Date_Stamp) FROM Batch WHERE Staff_ID = '" + user +\
                "' GROUP by House_No"
            query_data_batch = db.engine.execute(sql_cmd_batch)
            batch_info = {
                'House_No':[],
                'Feeding_Lot':[]
            }
            for row in query_data_batch:
                batch_info['House_No'].append(row['House_No'])
                batch_info['Feeding_Lot'].append(row['Feeding_Lot'])
            print(batch_info)
            output['House_No'] = batch_info['House_No'][0]
            output['Feeding_Lot'] = batch_info['Feeding_Lot'][0]
            if output['Feeding_Lot'] == []:
                return {"Code":0,"Message":"無飼養批次，請先新建一個飼養批次。","Result":None}

        # 紀錄出現順序
        record = {
            'Number':[],
            'Male':[],
            'Female':[]
        }
        
        for i in range(len(entry_list)):
            try:
                number =  int(entry_list[i])
                if number > 500:
                    break
                record['Number'].append(i)
            except ValueError:
                pass
            if entry_list[i] in keyword3:
                record['Male'].append(i)
            if entry_list[i] in keyword4:
                record['Female'].append(i)
        print(record)

        # 兩個數字
        if len(record['Number']) == 2:
            # 公和母都有
            if record['Male'] != [] and record['Female'] != []:
                if record['Male'] > record['Female']:
                    output['Male'] = int(entry_list[record['Number'][1]])
                    output['Female'] = int(entry_list[record['Number'][0]])
                else:
                    output['Male'] = int(entry_list[record['Number'][0]])
                    output['Female'] = int(entry_list[record['Number'][1]])
                # print(output)
            # 沒有的話前面公後面母
            else:
                output['Male'] = int(entry_list[record['Number'][0]])
                output['Female'] = int(entry_list[record['Number'][1]])

        # 一個數字
        elif len(record['Number']) == 1:
            # 公的
            if record['Male'] != [] and record['Female'] == []:
                output['Male'] = int(entry_list[record['Number'][0]])
            # 母的
            elif record['Male'] == [] and record['Female'] != []:
                output['Female'] = int(entry_list[record['Number'][0]])
            # 都沒有
            else:
                # 公的沒有母的有
                if output['Male'] is None and output['Female'] is not None:
                    output['Male'] = int(entry_list[record['Number'][0]])
                # 公的有母的沒有
                elif output['Male'] is not None and output['Female'] is None:
                    output['Female'] = int(entry_list[record['Number'][0]])
                # 都沒有
                else:
                    output['Male'] = int(entry_list[record['Number'][0]])
            with open(data,'w', encoding='utf-8') as f:
                f.writelines(json.dumps(output))
    
        if output['Male'] is None and output['Female'] is None:
            output['Message'] = '請輸入公雞和母雞' + output['Mode'] + '數量'
        elif output['Male'] is not None and output['Female'] is None:
            output['Message'] = '請輸入母雞' + output['Mode'] + '數量'
        elif output['Male'] is None and output['Female'] is not None:
            output['Message'] = '請輸入公雞' + output['Mode'] + '數量'
        else:
            output['Message'] = '公雞' + output['Mode'] + '數量為' +\
                str(output['Male']) + '隻，母雞' + output['Mode'] +\
                '數量為' + str(output['Female']) + '隻，飼養批次為：' +\
                output['Feeding_Lot'] + '，日期為：' +\
                time.strftime("%Y-%m-%d",time.localtime(time.time())) +\
                '，資訊正確請回覆正確，若日期、死亡隻數需修改則請再次輸入。'
            output['Date'] = time.strftime("%Y-%m-%d",time.localtime(time.time()))

        with open(data,'w', encoding='utf-8') as f:
            f.writelines(json.dumps(output))

        if output['Date'] is not None:
            for res in entry_list:
                if res in keyword5:
                    # 上傳

                    # 刪除紀錄檔
                    output['Message'] = '好的，資料上傳成功。'
                    os.remove(data)
                elif res in keyword6:
                    output['Message'] = '請輸入欲修改的資訊'
        # close db
        cleanup(db.session)

        print(output)
            
        return jsonify({"Code":0,"Message":None,"Result":output})
    
    if output['Mode'] is None:
        output['Message'] = '你好，有什麼可以幫你的嗎?'
    return jsonify({"Code":0,"Message":None,"Result":output})


# 清除資料庫
def cleanup(session):
    """
    This method cleans up the session object and also closes the connection pool using the dispose method.
    """
    engine_container = db.get_engine(app)
    session.close()
    engine_container.dispose()

if __name__ == "__main__":
    # app.run()
    app.run(host="0.0.0.0", port=8090)