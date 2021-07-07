import numpy as np

class Data_Process():
    def __init__(self):
        self.data = None
        self.value = None
        self.index = None
        self.labels = None
    def read_csv_file(self,filepath):
#         self.data = np.loadtxt(filepath,delimiter=",",encoding = 'gb2312',dtype={'names':('时间','货币和准货币(M2)供应量期末值(亿元)','货币和准货币(M2)供应量同比增长(%)','货币(M1)供应量期末值(亿元)'
# ,'货币(M1)供应量同比增长(%)','流通中现金(M0)供应量期末值(亿元)','流通中现金(M0)供应量同比增长(%)'),'formats':(np.str,np.float,np.float,np.float,np.float,np.float,np.float)},skiprows=3)
        self.data = np.loadtxt(filepath,str,delimiter=",",encoding = 'gb2312')
        self.data = self.data[2:-2]
        if self.data.shape[1]<2:
            return False
        self.index = self.data[1:,0]     #第一列，索引，是时间，几几年几月
        self.value = self.data[1:,1:]   #具体各项的数值
        self.labels = self.data[0,:]    #各项数值的名称，如'货币和准货币(M2)供应量期末值(亿元)'

        self.num_sample = len(self.index)    #样本数目

        # print(self.data.shape)
        # print(self.data[0])
        print(self.labels[0])
        # print(self.value[0])


        return True

    def get_represent_value(self):
        '''计算平均数、众数等典型值'''
        #争取一次循环计算完
        self.max_value = 0
        self.min_value = None
        self.avg_value = 0.0
        self.most_value = 0
        self.med_value = 0
        self.value_sort = self.value[:,1]
        self.value_sort = list(map(float,self.value_sort))
        self.value_sort = np.sort(self.value_sort)
        l = len(self.value_sort)
        sum = 0.0
        count = 0.0
        dc = {}
        for v in self.value_sort:
            self.max_value = v if v > self.max_value else self.max_value
            if self.min_value == None:
                self.min_value = v
            else:
                self.min_value = v if v< self.min_value else self.min_value
            sum = float(sum) + v
            count += 1
            if str(v) in dc:
                dc[str(v)] += 1
            else:
                dc[str(v)] = 1

        # 计算平均数
        self.avg_value = round(float(sum/count),4)
        #计算中位数
        if l%2 == 0:
            self.med_value = (float(self.value_sort[int(l/2)])+float(self.value_sort[int(l/2-1)]))/2
        else:
            self.med_value = float(self.value_sort[int(l/2)])
        # 计算众数
        tmp=0
        k = ''
        for key in dc.keys():
            if dc[key]>tmp:
                tmp = dc[key]
                k = key
        self.most_value = float(k)

        return self.max_value,self.min_value,self.avg_value,self.med_value,self.most_value






if __name__ == '__main__' :
    DP = Data_Process()
    path = '/Users/yunyi/Desktop/月度数据.csv'
    DP.read_csv_file(path)
    print(DP.get_represent_value())