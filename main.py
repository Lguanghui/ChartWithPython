from PyQt5 import QtCore,QtGui
from PyQt5.QtCore import QCoreApplication,QFileInfo
from PyQt5.QtWidgets import QApplication,QMainWindow,QMessageBox,QLabel,QWidget,QGridLayout,QFileDialog,QColorDialog
from PyQt5.QtGui import QImage,QPixmap,QIcon
from UIfiles.UI import Ui_mainWindow
import sys
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
from matplotlib.figure import Figure
import data_process
#设置正常显示中文
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']

class MyFigure(FigureCanvas):
    def __init__(self,width, height, dpi=100):
        #新建一个Figure
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        #设置Figure窗口
        super(MyFigure,self).__init__(self.fig) #此句必不可少，否则不能显示图形

        # 创建一个子图，和matlab差不多
        self.axes = self.fig.add_subplot(111)

        # 设置x y轴主刻度标签为某数的倍数
        self.xmajorLocator = MultipleLocator(2)  # 这里可以引申为在x轴上每隔几个月显示一次年月份
        self.axes.xaxis.set_major_locator(self.xmajorLocator)
        self.axes.xaxis.set_tick_params(labelrotation=0, labelsize=10)  # 设置一些x轴的外观参数，比如坐标刻度旋转角度,刻度签字体大小


    #自己建立的画图函数
    def plot(self):
        pass


class mainWindow(QMainWindow,Ui_mainWindow):
    def __init__(self):
        super(mainWindow, self).__init__()
        self.setupUi(self)
        self.initUI()
        self.grid_switch = False
        self.pltFigure = MyFigure(width=self.show_widget.width(),height=self.show_widget.minimumHeight())       #这里的height后面可以调调
        self.gridLayout_plt = QGridLayout(self.show_widget)
        self.gridLayout_plt.addWidget(self.pltFigure,0,0)

        # self.plotcos()
        self.init_grid()

        self.first_push = True
        self.line_style = 'bar'

    def initUI(self):

        self.color = '#FF8C00'
        self.dp = data_process.Data_Process()       #数据读取和处理实例

        # 刚开始，数据分析和导出按钮不可用
        self.ptn_analyse.setEnabled(False)
        self.ptn_output.setEnabled(False)

        self.radioButton_grid.clicked.connect(self.change_grid_switch)      #网格开关
        self.ptn_getData.clicked.connect(self.get_data)     #导入数据按钮
        self.ptn_analyse.clicked.connect(self.analyse_data) #分析数据按钮
        self.lineEdit_setTitle.returnPressed.connect(self.change_title) #更改图表题，以回车键作为触发信号

        #改变颜色
        self.ptn_set_color.clicked.connect(self.get_color_from_dialog)  #通过颜色盘获取并改变颜色
        self.lineEdit_set_color.returnPressed.connect(self.get_color_from_lineEdit)     #通过手动输入的颜色值获取并改变颜色

        #设置坐标轴标签
        self.lineEdit_set_xLabel.returnPressed.connect(self.set_xlabel)
        self.lineEdit_set_yLabel.returnPressed.connect(self.set_ylabel)

        #滑动条
        self.horizontalSlider_set_sample_num.valueChanged.connect(self.set_sample_num)

        # 线条类型：柱状图或者折线图
        self.ptn_switch_graph_style.clicked.connect(self.switch_graph_style)

        self.ptn_output.clicked.connect(self.save_output)

    def init_grid(self):
        #初始网格状态
        self.pltFigure.axes.xaxis.grid(False, which='major')
        self.pltFigure.axes.yaxis.grid(False, which='major')

    def change_grid_switch(self):
        '''更新网格开关'''
        if self.radioButton_grid.isChecked():
            self.grid_switch = True
        else:
            self.grid_switch = False

        #网格
        if self.grid_switch:
            self.pltFigure.axes.xaxis.grid(True, which='major')
            self.pltFigure.axes.yaxis.grid(True, which='major')
        else:
            self.pltFigure.axes.xaxis.grid(False, which='major')
            self.pltFigure.axes.yaxis.grid(False, which='major')

        if self.ptn_analyse.isEnabled():
            self.update_graph(self.color,self.sample_num)


    def update_graph(self,color,sample_num):
        '''更新显示的图'''
        self.analyse_data(color,sample_num)

    def get_data(self):
        '''读取csv数据'''
        # 选取文件
        path, ret = QFileDialog.getOpenFileName(self, '选取需要提交的文件', '.',
                                                 '(*.csv)')
        #选择了文件
        if ret:
            flag = self.dp.read_csv_file(path) #读取数据
            if flag:
                self.ptn_analyse.setEnabled(True)   #更新按钮状态

                #初始坐标轴标题
                self.xlabel = str(self.dp.labels[0])
                self.ylabel = str(self.dp.labels[1])

                self.sample_num = 10 if len(self.dp.index)>=10 else len(self.dp.index)    #初始样本显示数目
                self.horizontalSlider_set_sample_num.setMaximum(len(self.dp.index))     #更新设置滑动条最大值

                #得到文件名,并以文件名作为初始图标题
                fileInfo = QFileInfo(path)
                self.suptitle = fileInfo.baseName()
            else:
                #数据不符合要求
                QMessageBox.warning(self, 'warning', "导入数据不符合要求！", buttons=QMessageBox.Ok)
            print(path)

    def analyse_data(self,color = None,sample_num = None):
        '''分析处理数据
        color:指定图形颜色'''
        #没有传入颜色值或者样本数量的话，使用缺省值。这是保证第一次点击数据分析按钮时程序不崩溃
        if color == None or color == False:
            color = self.color
        if sample_num == None or sample_num == False:
            sample_num = 10 if len(self.dp.index)>=10 else len(self.dp.index)
        if self.first_push == True:
            self.show_represent_value()
            self.ptn_output.setEnabled(True)
            self.first_push = False

        self.pltFigure.fig.canvas.draw()    #画布重绘
        self.pltFigure.flush_events()   #画布刷新

        #柱状图
        if self.line_style == 'bar':
            self.pltFigure.axes.bar(self.dp.index[0:sample_num], self.dp.value[0:sample_num,1],color=str(color))        #作图
        #折线图
        else:
            self.pltFigure.axes.plot(self.dp.index[0:sample_num], self.dp.value[0:sample_num,1], 's-', color=str(color))

        self.pltFigure.axes.set_ylabel(self.ylabel)      #设置y轴标签
        self.pltFigure.axes.set_xlabel(self.xlabel)   #设置x轴标签

        self.pltFigure.fig.suptitle(self.suptitle)

        self.pltFigure.fig.canvas.draw()    #画布重绘
        self.pltFigure.flush_events()   #画布刷新


    def change_title(self):
        '''改变图标题'''
        #判断是否已经读取了数据
        if self.ptn_analyse.isEnabled():
            self.suptitle = self.lineEdit_setTitle.text()
            self.pltFigure.fig.suptitle(self.suptitle)
            self.update_graph(self.color,self.sample_num)

    def get_color_from_dialog(self):
        '''从颜色盘获取颜色值'''
        color = QColorDialog.getColor()
        if color.isValid() and self.ptn_analyse.isEnabled():
            color_name = color.name()
            self.lineEdit_set_color.setText(str(color_name))    #显示颜色值在文本输入框里面
            self.update_graph(str(color_name),self.sample_num)
            self.color = str(color_name)    #更新颜色值


    def get_color_from_lineEdit(self):
        '''从手动输入中获取颜色'''
        color = str(self.lineEdit_set_color.text())
        if self.ptn_analyse.isEnabled():
            try:
                self.analyse_data(color,self.sample_num)
                self.color = color
            except:
                # 颜色值不符合要求
                QMessageBox.warning(self, 'warning', "输入颜色值不符合要求！", buttons=QMessageBox.Ok)

    def set_xlabel(self):
        '''设置横轴标签'''
        if self.ptn_analyse.isEnabled():
            self.xlabel = str(self.lineEdit_set_xLabel.text())
            self.update_graph(self.color,self.sample_num)

    def set_ylabel(self):
        '''设置横轴标签'''
        if self.ptn_analyse.isEnabled():
            self.ylabel = str(self.lineEdit_set_yLabel.text())
            self.update_graph(self.color,self.sample_num)

    def set_sample_num(self):
        '''设置显示的样本数目'''
        if self.ptn_analyse.isEnabled():

            # 这里必须先清空一下坐标轴的数据，否则当滑块滑向较小值时不会使得样本显示数目变小。
            self.pltFigure.axes.cla()  # 清空坐标轴
            # 这里是为了在滑块滑动时保持网格开关的状态
            self.change_grid_switch()

            # 得到滑块的值，更新图像
            self.sample_num = int(self.horizontalSlider_set_sample_num.value())
            self.update_graph(self.color,self.sample_num)

    def show_represent_value(self):
        '''显示平均数 中位数 众数等'''
        self.max_value, self.min_value, self.avg_value, self.med_value, self.most_value = self.dp.get_represent_value()
        self.lineEdit_show_avg_value.setText(str(self.avg_value))
        self.lineEdit_show_max_value.setText(str(self.max_value))
        self.lineEdit_show_min_value.setText(str(self.min_value))
        self.lineEdit_show_med_value.setText(str(self.med_value))
        self.lineEdit_show_most_value.setText(str(self.most_value))

    def switch_graph_style(self):
        '''切换图类型'''
        if self.line_style == 'bar':
            self.line_style = 'line'
            self.ptn_switch_graph_style.setText('切换为柱状图')
            self.ptn_switch_graph_style.setIcon(QIcon(QPixmap("./ico/tubiaozhuzhuangtu")))
            self.pltFigure.axes.cla()  # 清空坐标轴

            self.change_grid_switch()

            self.update_graph(self.color, self.sample_num)
        else:
            self.line_style = 'bar'
            self.pltFigure.axes.cla()  # 清空坐标轴

            self.change_grid_switch()

            self.ptn_switch_graph_style.setText('切换为折线图')
            self.ptn_switch_graph_style.setIcon(QIcon(QPixmap('./ico/tubiaozhexiantu')))
            self.update_graph(self.color,self.sample_num)

    def save_output(self):
        '''保存图片'''
        if self.ptn_analyse.isEnabled():
            self.pltFigure.fig.savefig('output.jpg')
            QMessageBox.information(self, '保存结果', "结果已保存在本程序所在文件夹", buttons=QMessageBox.Ok)

if __name__ == '__main__':
    QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    mainWin = mainWindow()
    mainWin.show()
    sys.exit(app.exec())