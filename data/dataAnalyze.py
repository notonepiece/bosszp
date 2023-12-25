import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from wordcloud import WordCloud
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from pyecharts.charts import Bar, Grid
from pyecharts import options as opts
import seaborn as sns
import utils

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
class PlotChart:
    def __init__(self, plt, title, content=''):
        self.plt = plt
        self.title = title
        self.content = content
class EChart:
    def __init__(self, chart, title):
        self.chart = chart
        self.title = title

# 各城市最高薪资和最低薪资柱状图
def pyecharts_city_salary(data):
    # 计算最低薪资众数
    mode_low_by_location = data.groupby('工作地址')['最低薪资'].apply(
        lambda x: x.mode().iloc[0] if not x.mode().empty else None).reset_index()
    mode_low_by_location = mode_low_by_location.rename(columns={'最低薪资': '最低薪资众数'})
    # 计算最高薪资众数
    mode_high_by_location = data.groupby('工作地址')['最高薪资'].apply(
        lambda x: x.mode().iloc[0] if not x.mode().empty else None).reset_index()
    mode_high_by_location = mode_high_by_location.rename(columns={'最高薪资': '最高薪资众数'})
    # 合并两个 DataFrame，以 '工作地址' 为键
    merged_data = pd.merge(mode_low_by_location, mode_high_by_location, on='工作地址')
    # 绘制柱状图
    bar = (
        Bar(init_opts=opts.InitOpts(width='650px', height='400px'))
        .add_xaxis(merged_data['工作地址'].tolist())
        .add_yaxis("最低薪资众数", merged_data['最低薪资众数'].tolist(), label_opts=opts.LabelOpts(is_show=True))
        .add_yaxis("最高薪资众数", merged_data['最高薪资众数'].tolist(), label_opts=opts.LabelOpts(is_show=True))
        .set_series_opts(label_opts=opts.LabelOpts(is_show=True))
        .set_global_opts(xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45, font_size=12)),
                         datazoom_opts=opts.DataZoomOpts(range_start=0, range_end=10))
    )
    chart = bar.render_embed()
    return EChart(chart=chart, title="各城市的最低和最高薪资柱状图")

# 不同岗位招聘数量前10的城市水平柱状图
def pyecharts_job_number(data):
    # 统计每个工作地址的招聘数量
    city_counts = data['工作地址'].value_counts()
    # 取前10个数量最多的城市
    top_cities = city_counts.head(10)
    bar = (
        Bar(init_opts=opts.InitOpts(width="430px", height="400px"))
        .add_xaxis(np.flip(top_cities.index).tolist())
        .add_yaxis("", np.flip(top_cities.values).tolist())
        .reversal_axis()
        .set_global_opts(legend_opts=opts.LegendOpts(is_show=False))
    )
    chart = bar.render_embed()
    return EChart(chart=chart, title="各城市招聘数量排行")

# 互联网行业薪资随工作经验的变化折线图
def plot_experience_salary(data):
    # 统计薪资随工作经验的变化
    experience_salary = data.groupby('工作经验')[['最低薪资', '最高薪资']].median()
    # 重新排序经验水平
    experience_order = ['经验不限', '在校/应届', '1年以内', '1-3年', '3-5年', '5-10年', '10年以上']
    experience_salary = experience_salary.reindex(experience_order)
    # 计算最低薪资变化率
    experience_salary['最低薪资变化率'] = experience_salary['最低薪资'].pct_change() * 100
    # 计算最高薪资变化率
    experience_salary['最高薪资变化率'] = experience_salary['最高薪资'].pct_change() * 100
    # 判断最低薪资趋势
    if (experience_salary['最低薪资变化率'].sum() > 0):
        min_trend = '最低薪资呈上升趋势'
    elif (experience_salary['最低薪资变化率'].sum() < 0):
        min_trend = '最低薪资呈下降趋势'
    else:
        min_trend = '最低薪资趋势变化不明显'
    # 判断最高薪资趋势
    if (experience_salary['最高薪资变化率'].sum() > 0):
        max_trend = '最低薪资呈上升趋势'
    elif (experience_salary['最高薪资变化率'].sum() < 0):
        max_trend = '最低薪资呈下降趋势'
    else:
        max_trend = '最低薪资趋势变化不明显'
    # 创建图形对象
    fig, ax = plt.subplots(figsize=(12, 8))
    # 绘制最低薪资的折线图
    ax.plot(experience_salary.index, experience_salary['最低薪资'], marker='o', label='最低薪资', color='#8ECFC9')
    # 绘制最高薪资的折线图
    ax.plot(experience_salary.index, experience_salary['最高薪资'], marker='o', label='最高薪资', color='#FFBE7A')
    # 显示图例
    ax.legend(fontsize=16)
    # 设置x轴标签倾斜及字体大小
    ax.tick_params(axis='x', labelrotation=45, labelsize=14)
    # 设置y轴字体大小
    ax.tick_params(axis='y', labelsize=16)
    return PlotChart(utils.plot_to_base64(plt), '薪资随工作经验的变化',
                     content=f'如图所示,随着工作经验的提示,{','.join([min_trend, max_trend])}')

# 学历要求占比饼图
def plot_education(data):
    education_data = data['学历要求'].value_counts()
    fig, ax = plt.subplots(figsize=(12, 8))
    colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#c2c2f0', '#ffb3e6', '#c2f0c2']
    # 绘制饼图
    ax.pie(education_data, autopct='', startangle=140, colors=colors, radius=1.4)
    legend_labels = education_data.index.tolist()
    legend_rects = [plt.Rectangle((0, 0), 1, 1, color=color) for color in colors]
    # 创建图例，设置大小和字体大小
    legend = ax.legend(legend_rects, [f'{label} ({percentage:.1f}%)' for label, percentage in
                                      zip(legend_labels, education_data / education_data.sum() * 100)],
                       title='学历要求',prop={'size': 16}, bbox_to_anchor=(0.1, 0.35))
    # 使用 set_fontsize 设置图例标题的字体大小
    legend.get_title().set_fontsize(18)
    max_education = education_data.idxmax()
    return PlotChart(utils.plot_to_base64(plt), '互联网行业工作学历要求分布',
                     content=f'如同所示,企业所要求的学历占比主要为{max_education}')

# 不同城市中编程语言需求量热力图
def plot_hot_job(data):
    keywords = ['python', 'java', 'nodejs', 'golang', 'php', 'c++', 'c#']
    for keyword in keywords:
        data[keyword] = data['岗位名称'].str.lower().str.contains(keyword)
    # 计算每个城市中各个编程语言的需求量
    city_counts = data.groupby('工作地址')[keywords].sum()
    plt.figure(figsize=(12, 8))
    heatmap = sns.heatmap(city_counts, annot=True, fmt='d', cmap='OrRd')
    # 修改 x 和 y 坐标轴的字体大小
    heatmap.tick_params(axis='x', labelsize=14)
    heatmap.tick_params(axis='y', labelsize=14)
    heatmap.set_xlabel('编程语言', fontsize='16')
    heatmap.set_ylabel('城市', fontsize='16')
    plt.tight_layout()
    return PlotChart(utils.plot_to_base64(plt), '不同城市中编程语言需求量',
                     content="如同所示,整体上java开发语言是主流,主要分布在北京,南京,杭州等城市")

# 学历与薪资的箱线图
def plot_education_salary(data):
    # 计算平均薪资
    data['平均薪资'] = (data['最低薪资'] + data['最高薪资']) / 2
    # 创建学历和薪资的箱线图
    plt.figure(figsize=(12, 8))
    sns.boxplot(x='学历要求', y='平均薪资', data=data, color='#ffd166')
    plt.xlabel('学历要求', fontsize=16)
    plt.ylabel('平均薪资', fontsize=16)
    # 设置 x 轴和 y 轴的字体大小
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    plt.yticks(range(0, int(data['平均薪资'].max()) + 10000, 10000))
    plt.tight_layout()
    return PlotChart(utils.plot_to_base64(plt), '学历与薪资的关系', content=f'如同所示,招聘薪资主要分布在本科和大专')

# 招聘数量前10的公司名水平柱状图
def plot_number_company_size(data):
    # 统计公司名出现的次数
    company_counts = data['企业名称'].value_counts()
    # 获取前 10 个出现最多的公司名和它们的数量
    top_companies = company_counts.nlargest(10)
    plt.figure(figsize=(12, 8))
    # 创建水平柱状图
    plt.barh(np.flip(top_companies.index), np.flip(top_companies.values), color='#ef476f', height=0.8)
    # 在柱状图上标注具体的值
    for index, value in enumerate(np.flip(top_companies.values)):
        plt.text(value, index, str(value), ha='left', va='center_baseline', fontsize=16, color='black')
    # 设置 x 轴和 y 轴的字体大小
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    # 设置 x 标签和 y 标签的大小
    plt.xlabel('招聘数量', fontsize=16)
    plt.ylabel('企业名称', fontsize=16)
    plt.tight_layout()
    # 取排名第一的企业名
    most_recruitment_company = top_companies.index[0]
    return PlotChart(utils.plot_to_base64(plt), '公司招聘排行TOP10', content=f'如同所示,招聘数量最高的的公司是{most_recruitment_company}')

# 公司规模数量统计水平柱状图
def plot_company_size(data):
    # 统计不同规模的企业数量
    size_counts = data['企业规模'].value_counts()

    # 绘制水平柱状图
    plt.figure(figsize=(12, 8))
    size_counts.plot(kind='barh', color='#118AD5')
    plt.xlabel('数量', fontsize=16)
    plt.ylabel('企业规模', fontsize=16)
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    plt.tight_layout()
    return PlotChart(utils.plot_to_base64(plt), '不同规模企业的数量统计', content=f'如同所示,企业规模数量主要分布在20-99人')

# 工作标签词云
def work_label_world_could(data):
    data['工作标签'] = data['工作标签'].apply(lambda x: [tag.strip() for tag in x.split(',')])
    # 将所有标签扁平化并统计频次
    tags_frequency = pd.Series([tag for tags in data['工作标签'] for tag in tags]).value_counts()
    # 获取排名前50的标签
    top_tags = tags_frequency.head(50)
    # 生成词云
    wordcloud = WordCloud(width=800, height=400, background_color='white',
                          font_path='../resource/msyh.ttc').generate_from_frequencies(top_tags)
    # 显示词云图
    plt.figure(figsize=(12, 8))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    return PlotChart(utils.plot_to_base64(plt), '工作标签词云', '')

# 公司福利词云
def company_welfare_world_could(data):
    # 将企业福利拆分为单个词语
    data['企业福利'] = data['企业福利'].apply(lambda x: [tag.strip() for tag in x.split(',')])
    # 统计词频
    tags_frequency = pd.Series([tag for tags in data['企业福利'] for tag in tags]).value_counts()
    # 获取排名前50的标签
    top_tags = tags_frequency.head(50)
    # 生成词云
    wordcloud = WordCloud(width=800, height=400, background_color='white',
                          font_path='../resource/msyh.ttc').generate_from_frequencies(top_tags)
    # 显示词云图
    plt.figure(figsize=(12, 8))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    return PlotChart(utils.plot_to_base64(plt), '企业福利词云', '')

# 模型预测测试
def model_prediction(data):
    # 将文本映射为数字
    experience_mapping = {
        '经验不限': 0,
        '在校/应届': 1,
        '1年以内': 2,
        '1-3年': 3,
        '3-5年': 4,
        '5-10年': 5,
        '10年以上': 6
    }

    # 使用 replace 方法进行映射
    data['工作经验'] = data['工作经验'].replace(experience_mapping)
    # 特征选择：选择可能影响薪资的特征
    features = data[['工作经验']]
    # 目标变量：薪资范围的平均值作为目标变量
    target = (data['最低薪资'] + data['最高薪资']) / 2
    # 划分训练集和测试集
    X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)
    # 初始化线性回归模型
    model = LinearRegression()
    # 训练模型
    model.fit(X_train, y_train)
    # 预测测试集薪资范围平均值
    predictions = model.predict(X_test)
    # 评估模型性能
    mse = mean_squared_error(y_test, predictions)
    # 绘制实际薪资范围平均值和预测值的散点图
    plt.scatter(y_test, predictions)
    plt.xlabel('实际薪资范围平均值')
    plt.ylabel('预测薪资范围平均值')
    plt.title('薪资预测模型性能')
    plt.show()
