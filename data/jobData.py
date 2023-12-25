import os, time, logging, csv, re
import pandas as pd
from cityData import CityData
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By

logging.basicConfig(level=logging.INFO)
pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
class JobData:
    """获取<互联网行业 100020>在各个省会城市的招聘信息"""
    # https://www.zhipin.com/wapi/zpCommon/data/industry.json 行业信息json
    def __init__(self, page=1, city='100010000', industry='100020'):
        """ 初始化
        :param page: 搜索页数 默认: 10
        :param city: 城市编号 默认：全国(100010000)
        :param industry: 行业编号
        baseUrl -> 起始URL
        OUTPUT_PATH -> 输出地址
        spiderData -> 获取到的数据
       """
        self.page = page
        self.city = city
        self.industry = industry
        self.baseUrl = "https://www.zhipin.com/web/geek/job?city=%s&page=%s&industry=%s"
        self.OUTPUT_PATH = os.path.join(os.path.abspath('..'), "output")
        self.job_list = []
        self.cityData_init()
        self.city_dict = CityData().get_city_dict()
        self.city_list = CityData().get_city_list()
    def isClean(self):
        """是否存在清洗后的岗位招聘信息
        :return 存在 True, 不存在 False
        """
        if not os.path.exists(os.path.join(self.OUTPUT_PATH, 'job_clean.csv')):
            return False
        return True

    def get_browser(self):
        """ 获取浏览器对象
        :return: 返回浏览器对象
        """
        # 指定 Firefox 浏览器的驱动程序路径
        firefox_driver_path = os.path.abspath('../resource/./geckodriver.exe')
        # 不跳出窗口，后台运行
        # options = webdriver.FirefoxOptions()
        # 创建 Firefox WebDriver 对象，并指定 GeckoDriver 的服务
        firefox_service = Service(executable_path=firefox_driver_path)
        # browser = webdriver.Firefox(service=firefox_service, options=options)
        browser = webdriver.Firefox(service=firefox_service)
        return browser

    def cityData_init(self):
        cityData = CityData()
        if not cityData.isClean():
            cityData.start()

    def set_job_list(self):
        """
        设置岗位招聘信息
        :return:
        """
        # 获取浏览器对象
        browser = self.get_browser()
        # 自定义选择城市
        # for city_key in self.city_dict.keys():
        #     print(f"{city_key},{self.city_dict[city_key]['城市']}")
        # city_choice = int(input("选择要获取的城市编号: "))
        # self.city = self.city_dict[city_choice]['编号']
        input('回车开始')
        city_names = list(self.city_dict.values())
        city_index = 0
        for city in self.city_list:
            self.city = city
            for page_index in range(self.page):
                logging.info(f"开始读取{city_names[city_index]['城市']}市第{page_index + 1}页数据，请稍后······")
                # 依次爬取url
                url = self.baseUrl % (self.city, str(page_index + 1), self.industry)
                # 模拟浏览器发起请求
                browser.get(url)
                # 休眠20秒确保页面加载完成
                time.sleep(10)
                # browser.implicitly_wait(10)
                job_list = browser.find_elements(By.XPATH, '//ul[@class="job-list-box"]/li')
                index = 1
                for job in job_list:
                    try:
                        logging.info(f"开始读取第{page_index + 1}页第{index}条数据，请稍后······")
                        index += 1
                        # 岗位名称
                        jobName = job.find_element(By.XPATH, './/span[@class="job-name"]').text
                        # 工作地址
                        jobArea = job.find_element(By.XPATH, './/span[@class="job-area"]').text
                        # 工作薪资
                        jobSalary = job.find_element(By.XPATH, './/span[@class="salary"]').text
                        infoTags = job.find_elements(By.XPATH, './/a[@class="job-card-left"]/div[contains(@class, "job-info")]/ul[@class="tag-list"]/li')
                        # 学历要求
                        education = infoTags[-1].text
                        # 工作经验
                        workExperience = infoTags[0].text
                        # 工作标签
                        jobTagList = job.find_elements(By.XPATH, './/div[contains(@class, "job-card-footer")]/ul[@class="tag-list"]/li')
                        jobTagList = [tag.text for tag in jobTagList if tag.text.strip()]
                        jobTag = ','.join(jobTagList)
                        # 企业名称
                        companyName = job.find_element(By.XPATH, './/h3[@class="company-name"]/a').text
                        companyInfo = job.find_elements(By.XPATH, './/div[@class="company-info"]/ul[@class="company-tag-list"]/li')
                        # 企业类型
                        companyType = companyInfo[0].text
                        # 企业规模
                        companySize = companyInfo[-1].text
                        # 企业福利
                        companyAdvantage = job.find_element(By.XPATH, './/div[@class="info-desc"]').text
                        # clic = job.find_element(By.CSS_SELECTOR, '.job-card-left')
                        # browser.execute_script('arguments[0].click()', clic)
                        # # 窗口切换到最新打开的页面
                        # browser.switch_to.window(browser.window_handles[-1])
                        # time.sleep(5)
                        # # 工作详情
                        # jobDetail = browser.find_elements(By.XPATH, '//div[@class="job-sec-text"]')[0].text.replace('\n', '')
                        self.job_list.append([
                            jobName, jobArea, jobSalary, education, workExperience, jobTag,
                            companyName, companyType, companySize, companyAdvantage
                        ])
                        # # 关闭窗口
                        # browser.close()
                        # browser.switch_to.window(browser.window_handles[0])
                    except Exception:
                        break

                logging.info(f"第{page_index + 1}页读取完毕")
            city_index += 1


    def save_job_list_to_csv(self, data):
        """ 保存文件"""
        CSV_PATH = os.path.join(self.OUTPUT_PATH, 'job.csv')
        if not os.path.exists(CSV_PATH):
            # utf-8-sig CSV文件需要加0xEF, 0xBB, 0xBF(BOM)
            with open(CSV_PATH, 'a', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(
                    ["岗位名称", "工作地址", "工作薪资", "学历要求", "工作经验", "工作标签",
                     "企业名称", "企业类型", "企业规模", "企业福利", "工作详情"])
                for row in self.job_list:
                    writer.writerow(row)
        else:
            with open(CSV_PATH, 'a', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(data)
                for row in self.job_list:
                    writer.writerow(row)

    def clean_job_data(self):
        def process_salary(salary):
            min_salary, max_salary = map(lambda x: float(x) * 1000, salary[:-1].split('-'))
            return pd.Series({'每月最低薪资': int(min_salary), '每月最高薪资': int(max_salary)})
        def process_advantage(row):
            if '·' in row['工作薪资'] and '薪' in row['工作薪资'].split('·')[-1]:
                salary_suffix = row['工作薪资'].split('·')[-1]
                row['企业福利'] += f",{salary_suffix}"
                row['工作薪资'] = row['工作薪资'].replace(f"·{salary_suffix}", '')
            return row
        job_data = pd.read_csv(os.path.join(self.OUTPUT_PATH, 'job.csv'))
        # 删除重复行
        job_data.drop_duplicates(inplace=True)
        # 将企业福利空值填充为'无'
        job_data['企业福利'] = job_data['企业福利'].fillna('无')
        job_data['企业福利'] = job_data['企业福利'].str.replace('，', ',')
        # 删除小时工
        job_data = job_data[
            ~(job_data['工作薪资'].str.contains('元/时')
              | job_data['工作薪资'].str.contains('元/天')
              | job_data['工作薪资'].str.contains('元/'))]
        # 删除岗位包含'某'的企业
        job_data = job_data[~(job_data['企业名称'].str.contains('某'))]
        # 删除包含知名的企业
        job_data = job_data[~job_data['岗位名称'].str.contains('知名')]
        # 将工作标签空值填充为'无'
        job_data['工作标签'] = job_data['工作标签'].fillna('无')
        job_data['工作标签'] = job_data['工作标签'].str.replace('/', ',')
        job_data['工作标签'] = job_data['工作标签'].str.replace('，', ',')
        # 新增实习生列 是实习生为1 反之为0
        job_data['实习生'] = job_data['岗位名称'].apply(lambda row: 1 if '实习生' in row else 0)
        # 字符都转成大写
        job_data['岗位名称'] = job_data['岗位名称'].str.upper()
        job_data['岗位名称'] = job_data['岗位名称'].str.replace('）', ')')
        job_data['岗位名称'] = job_data['岗位名称'].str.replace('（', '(')
        job_data['岗位名称'] = job_data['岗位名称'].str.replace('【', '(')
        job_data['岗位名称'] = job_data['岗位名称'].str.replace('】', ')')
        job_data['岗位名称'] = job_data['岗位名称'].str.replace(']', ')')
        job_data['岗位名称'] = job_data['岗位名称'].str.replace('[', '(')
        job_data['岗位名称'] = job_data['岗位名称'].str.replace(' ', '')
        # 删除括号中的内容
        job_data['岗位名称'] = job_data['岗位名称'].apply(lambda x: re.sub(r'\([^)]*\)', '', x))
        # 删除包含...的岗位名称
        job_data = job_data[~job_data['岗位名称'].str.contains(re.escape('...'))]
        # 删除包含知名的岗位名称
        job_data = job_data[~job_data['岗位名称'].str.contains('知名')]
        # 将岗位名称中含有特殊字符'！'的删除
        job_data = job_data[~(job_data['岗位名称'].str.contains('！'))]
        job_data = job_data[~(job_data['岗位名称'].str.contains('!'))]
        # 处理工作地址
        job_data['工作地址'] = job_data['工作地址'].apply(lambda area: area.split('·')[0])
        # 将·xx薪存到福利当中
        job_data = job_data.apply(process_advantage, axis=1)
        # 将10k-20k 处理为 最低薪资1000 最高薪资2000
        job_data[['最低薪资', '最高薪资']] = job_data['工作薪资'].apply(process_salary)
        # 删除不需要的列
        job_data.drop(columns=['工作薪资', '工作详情', '企业类型'], inplace=True)
        # 删除每列前后空格
        job_data = job_data[job_data['岗位名称'].str.strip() != '']
        job_data = job_data.apply(lambda x: x.str.strip() if x.dtype == 'object' else x)
        # 保存csv文件
        job_data.to_csv(os.path.join(self.OUTPUT_PATH, 'job_clean.csv'), index=False, encoding="utf-8-sig")

    def start(self):
        self.set_job_list()


if __name__ == "__main__":
    jobData = JobData()
    jobData.start()



