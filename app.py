import io
import os
import re

from flask import Flask, render_template, redirect, request, send_file, url_for
from config.db_config import DataBaseConfig
import secrets
from db import db
import pandas as pd
import utils
import data.dataAnalyze as analyze

JOB_DATA_PATH = './output/job_clean.csv'
UPLOADS_PATH = './uploads'

app = Flask(__name__)
app.config.from_object(DataBaseConfig)
# 设置会话加密
app.config['SECRET_KEY'] = secrets.token_hex(16)
db.init_app(app)
# 注册蓝图
from views.user import user_bp, login_required

app.register_blueprint(user_bp, url_prefix='/user')

@app.route('/')
def welcome():
    return redirect('/user/login')


@app.route('/index/<keyword>/<int:page>/')
@app.route('/index/<filename>/')
@app.route('/index/')
# @login_required
def index(keyword=None, page=None, filename=None):
    if filename is not None:
        job_data = pd.read_csv(os.path.join(UPLOADS_PATH, f"{filename}.csv"))
    else:
        job_data = pd.read_csv(JOB_DATA_PATH)
    # 概述信息
    overview = utils.get_overview(job_data)
    show = True
    if keyword is not None:
        # 根据关键字进行过滤
        filtered_jobs = job_data[job_data['岗位名称'].str.contains(re.escape(keyword.upper()))]
        # 概述信息
        overview = utils.get_overview(filtered_jobs)
        # 一页显示10条
        per_page = 10
        jobs, total_pages = utils.read_csv_and_paginate(filtered_jobs, page, per_page)
        bar_chart_city_salary = analyze.pyecharts_city_salary(filtered_jobs)
        bar_chart_job_number = analyze.pyecharts_job_number(filtered_jobs)
        if filtered_jobs.empty:
            show = False
        return render_template('index.html', keyword=keyword, page=page,
                               jobs=jobs, total_pages=total_pages, current_page=page,
                               bar_chart_city_salary=bar_chart_city_salary,bar_chart_job_number=bar_chart_job_number,
                               overview=overview, show=show)
    else:
        bar_chart_city_salary = analyze.pyecharts_city_salary(job_data)
        bar_chart_job_number = analyze.pyecharts_job_number(job_data)
        return render_template('index.html', keyword=None, bar_chart_city_salary=bar_chart_city_salary,
                               bar_chart_job_number=bar_chart_job_number, overview=overview, show=show)

@app.route('/data/<int:page>')
@app.route('/data/', defaults={'page': 1})
# @login_required
def data(page):
    # 每页显示的条目数
    per_page = 15
    job_data = pd.read_csv(JOB_DATA_PATH)
    # 分页
    jobs, total_pages = utils.read_csv_and_paginate(job_data, page, per_page)
    return render_template('data.html', jobs=jobs, total_pages=total_pages, current_page=page)

@app.route('/chart/')
# @login_required
def chart():
    job_data = pd.read_csv(JOB_DATA_PATH)
    data = [analyze.plot_experience_salary(job_data),
            analyze.plot_education(job_data),
            analyze.plot_education_salary(job_data),
            analyze.plot_hot_job(job_data),
            analyze.plot_number_company_size(job_data),
            analyze.plot_company_size(job_data),
            analyze.work_label_world_could(job_data),
            analyze.company_welfare_world_could(job_data),
            ]
    return render_template('chart.html', data=data)

@app.route('/down/<keyword>')
@app.route('/down/')
def down(keyword=None):
    filtered_excel_content = utils.save_excel(keyword)
    if keyword is None:
        keyword = ''
    return send_file(io.BytesIO(filtered_excel_content),
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True,
                     download_name=f'{keyword}岗位信息.xlsx')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return '没有文件部分'
    file = request.files['file']
    if file.filename == '':
        return '没有选择文件'
    # 将文件保存到指定文件夹
    file.save('uploads/' + file.filename)
    return redirect(url_for('index', filename=os.path.splitext(file.filename)[0]))

if __name__ == '__main__':
    app.run()
