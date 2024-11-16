import sys
import os.path
import random
import json
import numpy as np
import threading
import cv2
import pandas as pd
import time
import pyautogui
import DB.DBConn as DB
import requests

from PyQt5 import QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QPainter, QColor, QPixmap
from PyQt5.QtCore import QPoint
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from tkinter import filedialog
from tkinter import *

class KeyValueItem(QListWidgetItem):
    def __init__(self, key, value, parent=None):
        super().__init__(f"{key}: {value}", parent)
        self.key = key
        self.value = value

class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        #
        try :
            external_ip = requests.get('http://ip.jsontest.com/').json()['ip']
            data = (external_ip, '', '', '')
            DB.call_procedure_tran('PY_insertSeatRandomLog %s, %s, %d, %d', data)
        except requests.RequestException as e:
            print(f'외부 ip주소 가져오기 실패 : {e}')


        #윈도우
        self.setWindowTitle('자리랜덤 배치 v1.5')
        self.setWindowIcon(QIcon(self.resource_path('favicon.png')))
        self.move(100, 100)
        self.resize(900, 670)

        self.Q_label_list = []
        self.Q_label_info_list = []
        self.Q_label_Table_list = []
        self.pixmap_list = []
        self.infomap_list = []
        self.img_location_list = {}
        self.nm_location_list = {}
        self.img_width = 60
        self.img_height = 80
        self.threadCnt = 0

        self.excelYN = False
        self.clickYN = False

        self.config_file = "recent_file_path.json"
    #툴바 설정
        # configAction = QAction(QIcon('images/common/config.png'), '인원선택', self)
        # configAction.setStatusTip('인원선택')
        # configAction.triggered.connect(self.show_popup)
        #
        # runAction = QAction(QIcon('images/common/run.png'), '실행', self)
        # runAction.setStatusTip('실행')
        # runAction.triggered.connect(self.show_result)
        #
        # self.toolbar = self.addToolBar('title')
        # self.toolbar.addAction(configAction)
        # self.toolbar.addAction(runAction)

        self.nameLabel = QLabel(self)
        self.nameLabel.setText('테이블당 좌석: ')
        self.nameLabel.move(20, 40)

        #self.lbl_img = QLabel(self)
        #self.lbl_img.setText('test')
        #self.lbl_img.move(190, 40)

        self.line = QLineEdit(self)
        self.line.move(120, 40)
        self.line.resize(50, 30)
        self.line.setValidator(QIntValidator(self))
        self.line.setValidator(QIntValidator(1, 100,self))

        confirmbutton = QPushButton('배치', self)
        confirmbutton.clicked.connect(self.clickMethod)
        confirmbutton.resize(50, 30)
        confirmbutton.move(180, 40)

        excelbutton = QAction(QIcon(''), '엑셀 열기', self)
        excelbutton.triggered.connect(self.excelopen)
        self.statusBar()

        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)
        filemenu = menubar.addMenu('&파일')
        filemenu.addAction(excelbutton)

        self.inbtnHeight = 250
        self.inpybutton = QPushButton(QIcon(self.resource_path('in.png')), '', self)
        self.inpybutton.clicked.connect(self.inMethod)
        self.inpybutton.resize(30, 30)
        self.inpybutton.move(130, self.inbtnHeight)

        self.outbtnHeight = 310
        self.outpybutton = QPushButton(QIcon(self.resource_path('out.png')), '', self)
        self.outpybutton.clicked.connect(self.outMethod)
        self.outpybutton.resize(30, 30)
        self.outpybutton.move(130, self.outbtnHeight)

        #선
        self.line_start = QPoint(290, 40)
        self.line_end = QPoint(290, 610)

        #리스트 위젯
        self.listwidget0 = QListWidget(self)
        self.listwidget0.resize(0, 0)
        self.listwidget0.move(0, 0)

        self.listwidget1 = QListWidget(self)
        self.listwidget1.resize(100,560)
        self.listwidget1.move(20, 80)

        self.listwidget2 = QListWidget(self)
        self.listwidget2.resize(100, 560)
        self.listwidget2.move(170, 80)

        #root = Tk()
        #root.filename = filedialog.askopenfilename(filedialog.askopenfilenames(initialdir="/", title = "파일을 선택 해 주세요", filetypes = (("*.txt","*txt","*xlsx"),("*.*","*"))))

        self.bathbutton = QPushButton('랜덤', self)
        self.bathbutton.clicked.connect(self.bathMethod)
        self.bathbutton.resize(70, 30)
        self.bathbutton.move(310, 40)

        #-------------스크롤 영역----------------------
        self.ScrollWidth = 580
        self.ScrollHeight = 560

        self.scroll_area = QScrollArea(self)
        self.scroll_area.move(310, 80)
        self.scroll_area.resize(self.ScrollWidth,self.ScrollHeight)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        self.main_label = QLabel(self.scroll_area)
        self.main_label.setFixedSize(800, 1200)
        #---------------------------------------------

        self.listwidget1.setDragEnabled(True)
        self.listwidget1.setAcceptDrops(True)
        self.listwidget2.setDragEnabled(True)
        self.listwidget2.setAcceptDrops(True)
        self.listwidget1.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.listwidget2.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.listwidget1.setDefaultDropAction(Qt.MoveAction)
        self.listwidget2.setDefaultDropAction(Qt.MoveAction)
        self.show()

    def changeEvent(self, event):
        super().changeEvent(event)

    def resizeEvent(self, event):
        old_Width = 900
        old_Height = 670
        old_line_Widht = 50
        old_line_Height = 30

        evt_size = event.oldSize()
        # print('-------------------')
        # print(evt_size.width())
        # print(evt_size.height())
        new_width = 0
        new_height = 0
        new_line_width = 0
        new_line_height = 0

        #스크롤
        self.ScrollWidth = 580
        self.ScrollHeight = 560
        #좌측 리스트 위젯
        line_Width = 50
        line_Height = 560
        #선
        line_draw = 650
        #버튼
        self.inbtnHeight = 250
        self.outbtnHeight = 310

        if old_Width > evt_size.width():
            # 마우스로 창을 키우면
            # 기본사이즈보다 클경우
            if(evt_size.width() != -1):
                # 최초 이벤트때는 실행안함
                new_width = old_Width - evt_size.width()
                self.ScrollWidth = self.ScrollWidth - new_width
                new_line_width = old_line_Widht - evt_size.width()
                line_Width = line_Width - new_line_width
        elif old_Width < self.width():
            # 기본사이즈보다 윈도우 창 사이즈가 크면
            new_width = self.width() - old_Width
            self.ScrollWidth = self.ScrollWidth + new_width
            new_line_width = self.width() - old_line_Widht
            line_Width = line_Width + new_line_width
        elif old_Width >= self.width():
            #윈도우 창 사이즈보다 기본 사이즈가 크면
            new_width = old_Width - self.width()
            self.ScrollWidth = self.ScrollWidth - new_width
            new_line_width = old_line_Widht - self.width()
            line_Width = line_Width - new_line_width
        else:
            if (evt_size.width() != -1):
                new_width = evt_size.width() - old_Width
                self.ScrollWidth = self.ScrollWidth + new_width
                new_line_width = evt_size.width() - old_line_Widht
                line_Width = line_Width + new_line_width

        if old_Height > evt_size.height():
            if (evt_size.height() != -1):
                new_height = old_Height - evt_size.height()
                self.ScrollHeight = self.ScrollHeight - new_height
                new_line_height = old_Height - evt_size.height()
                line_Height = line_Height - new_line_height
                line_draw = line_draw - new_line_height
                self.inbtnHeight = self.inbtnHeight - new_line_height
                self.outbtnHeight = self.outbtnHeight - new_line_height
        elif old_Height < self.height():
            new_height = self.height() - old_Height
            self.ScrollHeight = self.ScrollHeight + new_height
            new_line_height = self.height() - old_Height
            line_Height = line_Height + new_line_height
            line_draw = line_draw + new_line_height
            self.inbtnHeight = self.inbtnHeight + new_line_height
            self.outbtnHeight = self.outbtnHeight + new_line_height
        elif old_Height >= self.height():
            new_height = old_Height - self.height()
            self.ScrollHeight = self.ScrollHeight - new_height
            new_line_height = old_Height - self.height()
            line_Height = line_Height - new_line_height
            line_draw = line_draw - new_line_height
            self.inbtnHeight = self.inbtnHeight - new_line_height
            self.outbtnHeight = self.outbtnHeight - new_line_height
        else:
            if (evt_size.height() != -1):
                new_height = evt_size.height() - old_Height
                self.ScrollHeight = self.ScrollHeight + new_height
                new_line_height = evt_size.height() - old_Height
                line_Height = line_Height + new_line_height
                line_draw = line_draw + new_line_height
                self.inbtnHeight = self.inbtnHeight + new_line_height
                self.outbtnHeight = self.outbtnHeight + new_line_height

        self.scroll_area.resize(self.ScrollWidth, self.ScrollHeight)
        self.listwidget1.resize(100, line_Height)
        self.listwidget2.resize(100, line_Height)
        self.line_end = QPoint(290, line_draw)

        if self.inbtnHeight > 80:
            self.inpybutton.move(130, int(line_Height/2+30))
            self.outpybutton.move(130, int(line_Height/2+90))

    def keyPressEvent(self, e):
        if e.modifiers() & Qt.ShiftModifier:
            if e.modifiers() & Qt.AltModifier:
                if e.modifiers() & Qt.ControlModifier:
                    if int(self.line.text()) == int(444):
                        QMessageBox.about(self, '메세지', '여긴 지옥이야.... get out!!!!')
                    else:
                        return

    def resource_path(obj, relative_path):
        try:
            # PyInstaller에 의해 임시폴더에서 실행될 경우 임시폴더로 접근하는 함수
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        print(os.path.join(base_path, relative_path))
        return os.path.join(base_path, relative_path)

    # 최근 폴더경로 가져오기
    def load_recent_file_path(self):

        print('경로 가져오기')
        print(os.getcwd() + "\\" + self.config_file)
        if os.path.exists(os.getcwd() + "\\" + self.config_file):
            print('경로 확인 : ' + os.getcwd() + "\\" + self.config_file)
            with open(os.getcwd() + "\\" + self.config_file, 'r', encoding="utf-8") as f:
                print('파일오픈')
                config = json.load(f)
                print(config)
                return config.get('recent_file_path', '')

        return ''

    # 최근 열었던 폴더경로 저장
    def save_recent_file_path(self, file_path):

        try:
            print('경로저장')
            print(file_path)
            print(os.getcwd() + "\\" + self.config_file)
            with open(os.getcwd() + "\\" + self.config_file, 'w', encoding="utf-8") as f:
                print('저장경로 쓰기')
                json.dump({'recent_file_path': file_path}, f)
        except PermissionError:
            print("Error: Permission denied. Unable to write to the config file.")
        except IOError as e:
            print(f"Error: Unable to write to the config file. {e}")

    def excelopen(self):

        initial_dir = self.load_recent_file_path()

        root = filedialog.Tk()
        root.withdraw()

        # 2024.07.04 최근 열었던 폴더를 여는걸로 수정
        self.filename = filedialog.askopenfilename(initialdir=initial_dir)
        # self.filename = filedialog.askopenfilename(initialdir="/", title="choose your file",
        #                                            filetypes=(("xlsx files", "*.xlsx"), ("all files", "*.*")))
        print(self.filename)
        # df = pd.read_excel('경영정보부2.xlsx')
        try:
            print('??????????????????????')
            df = pd.read_excel(self.filename, header=None)
            print('??????????????????????')
            self.save_recent_file_path(os.path.dirname(self.filename))
            if df.get(0)[0] != '이름':
                QMessageBox.about(self, '메세지', '엑셀 파일이 양식에 맞지 않습니다.')
                return
        except:
            if self.filename != '':
                QMessageBox.about(self, '메세지', '암호화된 파일은 열 수 없습니다.')
            return

        df = pd.read_excel(self.filename)
        self.save_recent_file_path(os.path.dirname(self.filename))
        #'이름'열만 결측값 제거
        df = df[df['이름'].notna()]
        print(df)
        self.listwidget1.clear()
        self.listwidget2.clear()
        self.listwidget0.clear()

        for index, row in df.iterrows():
            # self.listwidget1.insertItem(index, row[0] + ' / ' + str(row[1]))
            self.listwidget1.insertItem(index, row[0])
            KeyValueItem(index, row[0], self.listwidget0)
            self.excelYN = True
        print(self.listwidget0)

    def bathMethod(self):

        print(str(self.threadCnt)+'번째 시작')
        if self.listwidget1.count() == 0 and self.excelYN == False:
            QMessageBox.about(self, '메세지', '파일 -> 엑셀 열기를 진행해주시길 바랍니다. ')
            return
        elif self.listwidget2.count() == 0:
            QMessageBox.about(self, '메세지', '대상 내역이 존재하지 않습니다.')
            return
        elif self.line.text() == '':
            QMessageBox.about(self, '메세지', '테이블당 좌석수를 입력해 주시길바랍니다.')
            return
        elif self.clickYN == False:
            QMessageBox.about(self, '메세지', '배치 버튼을 클릭해 주시길바랍니다.')
            return

        self.bathbutton.setDisabled(True)
        self.show()
        QApplication.processEvents()

        for i in range(5):
            time.sleep(0.4)
            alist = []  # 뽑은 a를 넣어 중복 방지해주는 리스트
            print('중복방지 시작')
            for n in range(len(self.pixmap_list)):
                a = random.randint(0, len(self.pixmap_list) - 1)
                while a in alist:
                    a = random.randint(0, len(self.pixmap_list)-1)
                alist.append(a)
            print('중복방지 종료')

            data1 = json.loads(self.img_location_list)
            data2 = json.loads(self.nm_location_list)

            n = 0
            print('좌표 셋팅 시작')
            for pixmap in self.pixmap_list:
                print('--원좌표--')
                print(self.Q_label_list[n].x())
                print('--상대좌표--')
                print(self.Q_label_list[alist[n]].x())
                print('--좌표이동--')
                self.Q_label_list[alist[n]].move(data1[n].get('x'), data1[n].get('y'))          #그림
                self.Q_label_info_list[alist[n]].move(data2[n].get('x'), data2[n].get('y'))     #이름
                print(self.Q_label_list[n].text())
                print('----------------------------------')

                n = n + 1

            print(str(i)+'번째 종료')
            self.show()
            QApplication.processEvents()


        #if self.threadCnt != 0:
            #print('랜덤 버튼 클릭')
            #self.threadCnt += 1
            #threading.Timer(0.3, self.bathMethod).start()
        #else:
        time.sleep(1)
        self.bathbutton.setDisabled(False)
        QApplication.processEvents()

        #data = ('ramen', 3, 5)
        #DB.call_procedure_tran('PY_insertSeatRandomLog %s, %d, %d', data)

        self.threadCnt = 0
        self.show()

        print(self.Q_label_info_list[0].text())
        # for i in self.Q_label_info_list :
        #     print(i.text())

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QColor(150, 150, 150))
        # painter.drawLine(QPoint(290, 40), QPoint(290, 610))
        painter.drawLine(QPoint(290, 40), self.line_end)

    def show_popup(self):
        self.hide()

    def clickMethod(self):
        if self.listwidget1.count() == 0 and self.excelYN == False:
            QMessageBox.about(self, '메세지', '파일 -> 엑셀 열기를 진행해주시길 바랍니다. ')
            return
        elif self.listwidget2.count() == 0:
            QMessageBox.about(self, '메세지', '대상 내역이 존재하지 않습니다.')
            return
        elif self.line.text() == '':
            QMessageBox.about(self, '메세지', '테이블당 좌석수를 입력해 주시길바랍니다.')
            return

        python_file_path = os.path.dirname(os.path.abspath(__file__))
        print(os.path.dirname(python_file_path))
        if os.path.isdir('./image') == True:
            print('폴더 존재')
        else:
            QMessageBox.about(self, '메세지','image폴더가 존재 하지 않습니다.\r\n\r\n폴더를 생성합니다.\r\n\r\nimage폴더에 엑셀에 작성된 이름으로 jpg파일을 넣어주시기 바랍니다. \r\n\r\nex) 홍길동.jpg')
            current_path = os.getcwd()
            os.mkdir(current_path + "/image")

        self.pixmap_list.clear()

        k = 0
        j = 0
        print('?')
        self.infomap_list.clear()
        while k < self.listwidget2.count():
            name = self.listwidget2.item(k).text()

            # 1. 한글 파일은 읽을 수 없어 변환
            # 2. openCV로 이미지를 읽고 해상도 맞추기
            # 3. openCV를 QImage로 객체 변환
            # 4. QImage를 PixmMap로 객체 변환
            if os.path.isfile(f'./image/{name}.jpg'):
                img_array = np.fromfile(f'./image/{name}.jpg', np.uint8)  # 컴퓨터가 읽을수 있게 넘파이로 변환
                curImg = cv2.imdecode(img_array, cv2.IMREAD_COLOR)  # 이미지를 읽어옴
                if type(curImg) == type(None):
                    img_array = np.fromfile(f'./image/default_img.jpg', np.uint8)  # 컴퓨터가 읽을수 있게 넘파이로 변환
                    curImg = cv2.imdecode(img_array, cv2.IMREAD_COLOR)  # 이미지를 읽어옴

                resize2 = cv2.resize(curImg, dsize=(self.width(), self.height()), fx=1, fy=1, interpolation=cv2.INTER_AREA)
                rgb_image = cv2.cvtColor(resize2, cv2.COLOR_BGR2RGB)

                #cv2.imshow("resize2", resize2)
                #cv2.imwrite('testaa.jpg', resize2)
                h, w, c = rgb_image.shape
                qImg = QtGui.QImage(rgb_image.data, w, h, w * c, QtGui.QImage.Format_RGB888)
                print(f'파일존재 : {name}')
            else:
                #img_array = np.fromfile(f'./image/default_img.jpg', np.uint8)  # 컴퓨터가 읽을수 있게 넘파이로 변환
                img_array = np.fromfile(self.resource_path('default_img.jpg'), np.uint8)  # 컴퓨터가 읽을수 있게 넘파이로 변환
                curImg = cv2.imdecode(img_array, cv2.IMREAD_COLOR)  # 이미지를 읽어옴
                resize2 = cv2.resize(curImg, dsize=(self.width(), self.height()), fx=1, fy=1, interpolation=cv2.INTER_AREA)
                rgb_image = cv2.cvtColor(resize2, cv2.COLOR_BGR2RGB)

                ##cv2.imwrite('test.jpg', rgb_image)
                #cv2.imshow("resize2", resize2)
                h, w, c = rgb_image.shape
                qImg = QtGui.QImage(rgb_image.data, w, h, w * c, QtGui.QImage.Format_RGB888)
                print(f'파일null : {name}')

            pixmap = QPixmap.fromImage(qImg)

            self.infomap_list.append(name)
            if len(self.Q_label_info_list) != 0:
                while j < len(self.Q_label_info_list):
                    self.Q_label_info_list[j].setHidden(True)
                    self.Q_label_list[j].setHidden(True)
                    j += 1

            k += 1
            self.pixmap_list.append(pixmap)

        imgdata = []
        nmdata = []
        mainwidth = 0
        infowidth = 0
        infoheight = 80
        img_resize_width = 50
        img_resieze_height = 10
        table_w = 15
        table_h = 10
        i = 1
        n = 0
        hideno = 0
        if len(self.Q_label_Table_list) != 0:
            while hideno < len(self.Q_label_Table_list):
                self.Q_label_Table_list[hideno].hide()
                hideno += 1

        self.Q_label_list.clear()
        self.Q_label_info_list.clear()
        self.Q_label_Table_list.clear()

        for pixmap in self.pixmap_list:
            self.Q_label_list.append('label' + str(i))
            self.Q_label_info_list.append('labelInfo' + str(i))

            self.Q_label_list[i-1] = QLabel(self.main_label)
            self.Q_label_info_list[i-1] = QLabel(self.main_label)

            self.Q_label_list[i-1].setFixedSize(self.img_width,self.img_height)
            self.Q_label_info_list[i-1].setFixedSize(70, 40)

            #cv2.imshow("resize2", resize2)

            scaled_pixmap = pixmap.scaled(self.Q_label_list[i-1].width(), self.Q_label_list[i-1].height())
            #scaled_pixmap = resize2

            self.Q_label_list[i-1].setPixmap(scaled_pixmap)
            self.Q_label_info_list[i-1].setText(self.infomap_list[i-1])
            font = self.Q_label_info_list[i-1].font()
            font.setPointSize(8)
            self.Q_label_info_list[i-1].setFont(font)
            self.Q_label_info_list[i-1].setAlignment(Qt.AlignCenter)
            #if i-1 == int(self.line.text()):
            #if self.listwidget2.count() / int(self.line.text()) == int(self.line.text()):

            print((i - 1) % int(self.line.text()))
            if (i - 1) % int(self.line.text()) == 0:
                self.Q_label_Table_list.append('labelTable' + str(n+1))
                self.Q_label_Table_list[n] = QLabel(self.main_label)
                font = self.Q_label_Table_list[n].font()
                font.setPointSize(15)
                self.Q_label_Table_list[n].setFont(font)
                self.Q_label_Table_list[n].setText(str(n+1))
                self.Q_label_Table_list[n].setFixedSize(30, 80)

                self.Q_label_Table_list[n].move(table_w, table_h)
                table_h += 110

                self.Q_label_Table_list[n].show()
                n += 1
            else:
                print('test')


            if (i-1) % int(self.line.text()) == 0 and i != 1:
                img_resize_width = 50

                infowidth = int(self.Q_label_list[i - 1].geometry().width() / 3 + img_resize_width - 6)
                if (i - 1) % int(self.line.text()) == 0:
                    img_resieze_height += 110
                    infoheight += 110

                self.Q_label_list[i-1].move(img_resize_width, img_resieze_height)
                self.Q_label_info_list[i-1].move(img_resize_width-3, infoheight)
            else:
                self.Q_label_list[i-1].move(img_resize_width, img_resieze_height)
                infowidth = int(self.Q_label_list[i - 1].geometry().width() / 3 + img_resize_width - 6)
                self.Q_label_info_list[i-1].move(img_resize_width-3, infoheight)

            if img_resize_width > mainwidth:
                mainwidth = img_resize_width

            print(len(self.infomap_list[i - 1]))
            print(self.infomap_list[i - 1])
            #if len(self.infomap_list[i - 1]) == 4:
                #infowidth = self.Q_label_info_list[i - 1].x() - 10
                #self.Q_label_info_list[i - 1].move(self.Q_label_info_list[i - 1].x() - 10, self.Q_label_info_list[i - 1].y())

            #if len(self.infomap_list[i - 1]) == 5:
                #infowidth = self.Q_label_info_list[i - 1].x() - 15
                #self.Q_label_info_list[i - 1].move(self.Q_label_info_list[i - 1].x() - 15, self.Q_label_info_list[i - 1].y())

            imgdata.append({
                "x" : img_resize_width,
                "y" : img_resieze_height
            })

            nmdata.append({
                "x": img_resize_width-3,
                "y": infoheight
            })

            #self.img_location_list.append(json.dumps(data))
            #self.nm_location_list.append('{"x":' + infowidth + '}')
            #self.nm_location_list.append('{"y":' + infoheight + '}')

            self.scroll_area.setWidget(self.main_label)
            vbox_layout = QVBoxLayout(self)
            vbox_layout.addWidget(self.scroll_area)

            #self.hbox = QHBoxLayout()
            #--------------스크롤 영역---------------
            #self.hbox.addWidget(self.Q_label_list[i - 1])
            #self.hbox.addWidget(self.Q_label_info_list[i - 1])

            #self.hbox.setAlignment(Qt.AlignLeft)

            #self.vbox.addWidget(self.main_label)
            #self.vbox.addLayout(self.hbox)


            self.Q_label_list[i-1].show()
            self.Q_label_info_list[i - 1].show()

            img_resize_width += 70
            infowidth += 110
            i += 1

        self.img_location_list = json.dumps(imgdata)
        self.nm_location_list = json.dumps(nmdata)
        self.main_label.setFixedSize(mainwidth+80, infoheight+30)

        self.clickYN = True
        #self.lbl_img.setPixmap(pixmap)

    def inMethod(self):
        #self.listwidget2.insertItem(self.listwidget1.currentRow(), self.listwidget1.item(self.listwidget1.currentRow()).text())
        selReadName = []

        selectedItems = [item for item in self.listwidget1.selectedItems()]
        selectedKeys = []

        for item in selectedItems:
            for i in range(self.listwidget0.count()):
                if item.text() == self.listwidget0.item(i).value:
                    selectedKeys.append(self.listwidget0.item(i).key)

        print(selectedKeys)
        for i in range(len(selectedKeys)):
            for j in range(len(selectedKeys)-i-1):
                if selectedKeys[j] > selectedKeys[j + 1]:
                    # print(selectedKeys[j])
                    # print(selectedKeys[j+1])
                    selectedKeys[j], selectedKeys[j + 1] = selectedKeys[j + 1], selectedKeys[j]
                    selectedItems[j], selectedItems[j + 1] = selectedItems[j + 1], selectedItems[j]

        # print(selectedKeys)
        for k in selectedItems:
            self.listwidget2.addItem(str(k.text()))
            self.listwidget1.takeItem(self.listwidget1.row(k))

        # for item in self.listwidget1.selectedItems():
        #     for i in range(self.listwidget0.count()):
        #         #print(self.listwidget0.item(1).value)
        #         #print(self.listwidget0.item(1).key)
        #         #print(selReadName[0])
        #         if item.text() == self.listwidget0.item(i).value:
        #             #print(self.listwidget0.item(i).key)
        #             self.listwidget2.insertItem(self.listwidget0.item(i).key, item.text())
        #             self.listwidget1.takeItem(self.listwidget1.row(item))

        # for item in self.listwidget1.selectedItems():
        #     #print(item.text())
        #     self.listwidget2.addItem(str(item.text()))
        #     self.listwidget1.takeItem(self.listwidget1.row(item))


        # lst_modelindex = self.listwidget1.selectedIndexes()
        # lst_index = []
        # lstCount = 0
        #
        # for modelindex in lst_modelindex:
        #     lst_index.append(modelindex.row())
        #     lstCount += 1
        #     #self.listwidget1.takeItem(modelindex.row())
        #
        #
        # for index in lst_modelindex:
        #     lstCount -= 1
        #     self.listwidget1.takeItem(lst_index[lstCount])

        #self.listwidget2.addItem(selReadName[1])
        #self.listwidget2.addItem(self.listwidget1.takeItem(self.listwidget1.currentRow()))


    def outMethod(self):
        #self.listwidget1.addItem(self.listwidget2.takeItem(self.listwidget2.currentRow()))
        selReadName = []

        selectedItems = [item for item in self.listwidget2.selectedItems()]
        selectedKeys = []

        for item in selectedItems:
            for i in range(self.listwidget0.count()):
                if item.text() == self.listwidget0.item(i).value:
                    selectedKeys.append(self.listwidget0.item(i).key)

        for i in range(len(selectedKeys)):
            for j in range(len(selectedKeys) - i - 1):
                if selectedKeys[j] > selectedKeys[j + 1]:
                    selectedKeys[j], selectedKeys[j + 1] = selectedKeys[j + 1], selectedKeys[j]
                    selectedItems[j], selectedItems[j + 1] = selectedItems[j + 1], selectedItems[j]

        # print(selectedKeys)
        for k in selectedItems:
            self.listwidget1.addItem(str(k.text()))
            self.listwidget2.takeItem(self.listwidget2.row(k))

        # 1.3버전-----------------------------------------------------
        # for item in self.listwidget2.selectedItems():
        #     selReadName.append(str(item.text()))
        #     print(self.listwidget2.item(2))
        #     print(item.text())
        #
        #     self.listwidget1.addItem(str(item.text()))
        #     self.listwidget2.takeItem(self.listwidget2.row(item))
        # 1.3버전-----------------------------------------------------

        # lst_modelindex = self.listwidget2.selectedIndexes()
        # lst_index = []
        # lstCount = 0
        #
        # for modelindex in lst_modelindex:
        #     lst_index.append(modelindex.row())
        #     lstCount += 1
        #     # self.listwidget1.takeItem(modelindex.row())
        #
        # for index in lst_modelindex:
        #     lstCount -= 1
        #     self.listwidget2.takeItem(lst_index[lstCount])

if __name__ == '__main__':
   app = QApplication(sys.argv)
   ex = MyApp()
   sys.exit(app.exec_())

