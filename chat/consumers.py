# chat/consumers.py
import json
import pandas as pd
from chat.capture_analyze_one_file import *
from channels.generic.websocket import WebsocketConsumer
import sys
import subprocess
import time
import signal
import datetime
from threading import Thread
import os
from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio
'''
def handler(signum, frame):
    # 处理ctrl+c信号，结束循环
    global running
    running = False
   
# 注册ctrl+c信号处理函数
signal.signal(signal.SIGINT, handler)
'''

global running
running = True
global df_all
df_all = pd.DataFrame(columns=['frame.number', 'http2.streamid', 'ip.src', 'ip.dst'])

def capture_process(duration, port):
    while running:
        # 获取当前时间作为文件名的一部分
        current_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        print("Cony, Please press Ctrl+C when capture is done. :)")
        capture_file = 'capture_' + current_time + '.pcap'
        p = subprocess.Popen(['tshark', '-i', 'ens18', '-a', 'duration:' + str(duration), '-f', 'tcp port ' + str(port), '-w', capture_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(duration)

def analyze_process():
    while running:
        files = [f for f in os.listdir() if f.startswith('capture_') and f.endswith('.pcap')]
        for capture_file in files:
            # 使用tshark对抓包文件进行解析后生成csv文件
            csv_file = capture_file.replace('.pcap', '.csv')
            p = subprocess.Popen(['tshark', '-r', capture_file, '-T', 'fields', '-E', 'header=y', '-E', 'separator=,', '-E', 'quote=d', '-e', 'frame.number', '-e', 'http2.streamid',  '-e', 'ip.src', '-e', 'ip.dst', '-e', 'grpc', '-e', 'protobuf.message.name', '-e', 'pbm.com.webank.ai.eggroll.api.networking.proxy.Packet', '-e', 'pbm.com.webank.ai.eggroll.api.networking.proxy.Data'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            with open(csv_file, 'w') as f:
                f.write(p.communicate()[0].decode('utf-8'))

    # running变为False时，检查是否还有文件未处理完，如果有，则处理完
    files = [f for f in os.listdir() if f.startswith('capture_') and f.endswith('.pcap')]
    for capture_file in files:
        # 使用tshark对抓包文件进行解析后生成csv文件
        print("Cony, Please wait to exit...")
        csv_file = capture_file.replace('.pcap', '.csv')
        p = subprocess.Popen(['tshark', '-r', capture_file, '-T', 'fields', '-E', 'header=y', '-E', 'separator=,', '-E', 'quote=d', '-e', 'frame.number', '-e', 'http2.streamid',  '-e', 'ip.src', '-e', 'ip.dst', '-e', 'grpc', '-e', 'protobuf.message.name', '-e', 'pbm.com.webank.ai.eggroll.api.networking.proxy.Packet', '-e', 'pbm.com.webank.ai.eggroll.api.networking.proxy.Data'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        with open(csv_file, 'w') as f:
            f.write(p.communicate()[0].decode('utf-8'))


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    #receive filename from webpage, push button to start show content of CSV
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        filename = text_data_json["message"]
        print('111')
        self.send(text_data=json.dumps({"message": filename}))
        self.send(text_data=json.dumps({"message": '-----start-----'}))
     
      
        files = [f for f in os.listdir() if f.startswith('capture_') and f.endswith('.pcap')]
        for capture_file in files:
            #csv_file = capture_file.replace('.pcap', '.csv')
            p = subprocess.Popen(['tshark', '-r', capture_file, '-T', 'fields', '-E', 'header=y', '-E', 'separator=,', '-E', 'quote=d','-e', 'frame.number', '-e', 'http2.streamid',  '-e', 'ip.src', '-e', 'ip.dst','-e', 'grpc','-e', 'protobuf.message.name'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print('222')
            df = pd.read_csv(p.stdout, sep=',')
            for row in df.itertuples():
                #print(dir(row)) 
                self.send(text_data=json.dumps({"message": row._1}))
                self.send(text_data=json.dumps({"message": row._2}))
                self.send(text_data=json.dumps({"message": row._3}))
                self.send(text_data=json.dumps({"message": row._4}))
                self.send(text_data=json.dumps({"message": row.grpc}))
                self.send(text_data=json.dumps({"message": row._6}))
                #os.remove(capture_file)
                #df_all = pd.concat([df_all, df])  
 
        print('444')
        self.send(text_data=json.dumps({"message": '-----end-----'}))
   