import requests, os, csv
import pandas as pd
class CityData:
    """
    获取热门城市及各省省会城市的信息
    如: 全国: 100010000
    """
    def __init__(self):
        self.city_list = []
        # 输出目录
        self.OUTPUT_PATH = os.path.join(os.path.abspath('..'), "output")
        self.province_capitals = [
            '北京', '天津', '石家庄', '太原', '呼和浩特', '沈阳', '长春', '哈尔滨', '上海', '南京',
            '杭州', '合肥', '福州', '南昌', '济南', '郑州', '武汉', '长沙', '广州', '南宁', '海口',
            '重庆', '成都', '贵阳', '昆明', '拉萨', '西安', '兰州', '西宁', '银川', '乌鲁木齐'
        ]

    def isClean(self):
        """是否存在清洗后的城市信息
            - 存在 True
            - 不存在 False
        """
        if not os.path.exists(os.path.join(self.OUTPUT_PATH, 'city_clean.csv')):
            return False
        return True

    # 设置城市信息
    def set_city_list(self):
        url = 'https://www.zhipin.com/wapi/zpCommon/data/cityGroup.json'
        city_data = requests.get(url).json()
        # city_all -> 所有城市
        city_all = [item for item in city_data['zpData']['cityGroup']]
        # cities -> 不同首字母所包含的城市
        for cities in city_all:
            for index, city in enumerate(cities['cityList']):
                self.city_list.append([index + 1, city['name'], city['code']])

    # 保存城市信息到csv文件
    def save_city_list_to_csv(self):
        CSV_PATH = os.path.join(self.OUTPUT_PATH, 'city.csv')
        if not os.path.exists(CSV_PATH):
            with open(CSV_PATH, 'a', newline='', encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(['id', '城市', '编号'])
                if self.city_list is not None:
                    for item in self.city_list:
                        writer.writerow(item)
    # 清洗城市信息
    def clean_city_list(self):
        df = pd.read_csv(os.path.join(self.OUTPUT_PATH, 'city.csv'), usecols=(1, 2))
        df = df[df['城市'].isin(self.province_capitals)]
        df = df.sort_values(by='编号')
        df.to_csv(os.path.join(self.OUTPUT_PATH, 'city_clean.csv'), encoding="utf-8-sig", index=False)

    # 获取城市编号列表
    def get_city_list(self):
        return pd.read_csv(os.path.join(self.OUTPUT_PATH, 'city_clean.csv'))['编号'].to_list()

    # 获取城市信息字典
    def get_city_dict(self):
        df = pd.read_csv(os.path.join(self.OUTPUT_PATH, 'city_clean.csv'))
        df['id'] = range(1, len(df) + 1)
        # 将DataFrame转换为字典
        result_dict = df.set_index('id').to_dict(orient='index')
        return result_dict

    # 启动
    def start(self):
        self.set_city_list()
        self.save_city_list_to_csv()
        self.clean_city_list()


