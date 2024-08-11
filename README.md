# 大麦抢票脚本

## 功能
- 一个通过在大麦手机版网页抢票的脚本。

## 使用说明

#### 注意事项
1. 初次使用没有 Cookie ，会自动唤起浏览器访问大麦官网登录获取 Cookie ，可选择任意你喜欢的方式进行登录，无论是扫码、短信还是账号密码。
2. 如果太久没用，请先手动删除目录下的 Cookie 存储文件`cookies.pkl`，然后再运行脚本重新登录。
3. 大麦账号必须先做好实名制认证，并至少添加一位购票人实名制信息。
4. 大麦手机版网页https://m.damai.cn ，也可在电脑端https://www.damai.cn 先选好需要抢票的网页，将网页网址的 id 参数复制到 config.json 中的`url`字段中。
5. 提前备好配送地址。
   
#### 环境准备
- Python3
    - Selenium (4.10.0以下版本)
- Chrome 以及配置与 Chrome 版本兼容的 ChromeDriver （当然，你也可以自行研究改用其它浏览器驱动）。

#### 脚本配置
- 参照config.json。

#### 脚本运行
python main.py



## 鸣谢
原作者：
- Guyungy https://github.com/Guyungy/damaihelper 提供的脚本基础逻辑！

## 免责声明
详见MIT License，此仓库仅用于个人参考学习，但如他人用本仓库代码用于商业用途（鄙视黄牛），侵犯到大麦网利益等，本人不承担任何责任。
