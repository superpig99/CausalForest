## 4个函数，不依赖自定义类，可优先实现
import pandas as pd

def split_sequence(result,start,end,num_parts):
    pass

def equal_doubles(first,second,epsilon):
    pass

def load_data(file_name):
    """
    input: file_name
    output: [data,(num_rows,num_cols)]
    dtype: {file_name: string, data: pd.DataFrame, num_rows: int, num_cols: int}
    """
    # load data
    data = pd.read_csv(file_name)
    return [data,data.shape]

def set_data(data,row,col,value):
    pass