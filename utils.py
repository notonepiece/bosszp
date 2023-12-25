import io
import numpy as np
import pandas as pd
import base64
from io import BytesIO
from matplotlib import pyplot as plt
JOB_DATA_PATH = './output/job_clean.csv'
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
class OverView:
    def __init__(self, city_counts, max_salary_by_city, max_num_by_city, company_counts):
        self.city_counts = city_counts
        self.max_salary_by_city = max_salary_by_city
        self.max_num_by_city = max_num_by_city
        self.company_counts = company_counts

# 分页
def read_csv_and_paginate(data, page, per_page):
    # 获取总条目数
    total_jobs = len(data)
    # 计算总页数
    total_pages = (total_jobs // per_page) + (1 if total_jobs % per_page > 0 else 0)
    # 计算起始和结束索引
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    # 获取当前页的数据
    jobs = data.iloc[start_idx:end_idx]
    return jobs, total_pages

# 转成base64编码
def plot_to_base64(fig):
    img = BytesIO()
    fig.savefig(img, format='png')
    img.seek(0)
    img_str = "data:image/png;base64," + \
        base64.b64encode(img.read()).decode('utf-8')
    plt.close()
    return img_str

# 保存excel
def save_excel(keyword):
    job_data = pd.read_csv(JOB_DATA_PATH)
    if keyword is not None:
        job_data = job_data[job_data['岗位名称'].str.contains(keyword.upper())]
    else:
        keyword = ''
    excel_bytes = io.BytesIO()
    with pd.ExcelWriter(excel_bytes, engine='xlsxwriter') as writer:
        job_data.to_excel(writer, index=False, sheet_name=f"{keyword}岗位信息")
    return excel_bytes.getvalue()

# 获取概述
def get_overview(data):
    '''获取概述信息'''
    if not data.empty:
        # 统计每个工作地址的招聘数量
        city_counts = data['工作地址'].value_counts()
        # 计算最低薪资众数
        mode_low_by_location = data.groupby('工作地址')['最低薪资'].apply(
            lambda x: x.mode().iloc[0] if not x.mode().empty else None).reset_index()
        # 计算最高薪资众数
        mode_high_by_location = data.groupby('工作地址')['最高薪资'].apply(
            lambda x: x.mode().iloc[0] if not x.mode().empty else None).reset_index()
        # 计算平均众数
        mode_low_high_avg = (mode_low_by_location['最低薪资'] + mode_high_by_location['最高薪资']) / 2
        # 找到平均众数最高的城市名
        max_avg_index = mode_low_high_avg.idxmax()
        max_avg_location = mode_low_by_location.loc[max_avg_index, '工作地址']
        # 获取招聘数量最多的公司名
        company_counts = data['企业名称'].value_counts()
        return OverView(len(data),  max_avg_location, city_counts.idxmax(), company_counts.idxmax())


