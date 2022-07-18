## 4个函数，不依赖自定义类，可优先实现
import pandas as pd
from pyspark.sql import SparkSession
import math

def split_sequence(result,start,end,num_parts):
    '''
    函数说明：
    split_sequence函数用于分配线程数，结果存储在result里
    参数说明：
    num_parts是线程个数，根据线程个数，分三种情况分配
    start和end应该是split候选节点的index
    '''
    if num_parts == 1:
        result.append(start)
        result.append(end+1)
        return
    
    if num_parts > (end - start + 1):
        for i in range(start,end+2):
            result.append(i)
        return
    
    length = end - start + 1
    part_length_short = length // num_parts
    part_length_long = math.ceil(length/num_parts)
    cut_pos = length % num_parts

    for i in range(start, int(start+cut_pos*part_length_long), part_length_long):
        result.append(i)
    
    for i in range(int(start+cut_pos*part_length_long),end+2,part_length_short):
        result.append(i)

# 判断first和second是否相等【这个函数在python里应该没啥用
def equal_doubles(first,second,epsilon):
    if math.isnan(first):
        return math.isnan(second)
    return abs(first - second) < epsilon

def load_data(file_name):
    """
    input: file_name
    output: [data,(num_rows,num_cols)]
    dtype: {file_name: string, data: pd.DataFrame, num_rows: int, num_cols: int}
    """
    # load data
    data = pd.read_csv(file_name) # pandas.dataframe类型，注意所读的数据在存储时不能存储index
    return [data,data.shape]

    # pyspark类型
    # data = spark.read\
    #     .option("inferSchema","true") \
    #     .option("header","true") \
    #     .csv(file_name)
    # return [data,[data.count(),len(data.columns)]]

def load_data_pyspark(df_data):
    df_data.cache() # df_data是pyspark的dataframe
    return [df_data,[df_data.count(),len(df_data.columns)]]


# 这里和cpp原版存在区别，因为python取数不需要用到num_rows，所以，传入的data参数只需要是data即可，不需要data pair
def set_data(data,row,col,value):
    data.iloc[row,col] = value