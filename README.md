AutoTrade --- 自动化交易框架
====================

# 1 简介
AutoTrade是一款自动化交易框架. 注意, 是框架而不仅仅是一个券商交易接口(当然, 里面也包含了一个完整的券商接口,具体是哪个券商的,下面会介绍). 

## 1.1 什么是框架?
AutoTrade 是一个自动化交易框架, 类似于web设计里的MVC框架, AutoTrad也分为M(odel), T(rade), S(ocket) 三个部分.

Model 是指交易策略, 之所以叫model是因为AutoTrade采用模块化的思维管理策略, 也就是说, 在一个交易框架里允许多个策略同时运行, 每一个策略理论上可以做到互不干扰.
Model 是一个交易系统生存的灵魂, 这也是需要用户发挥想象力的地方.

Socket 是指交易的接口. AutoTrade已经实现了广发证券web接口的部分功能, 包括 股票的买入和卖出, 基金的申购和赎回, 分级基金的拆分和合并等等.
随着开发的继续, 功能还会继续完善.

Trade 是指交易管理, 例如交易的处理, 交易状态的维护等等.
Trade 是Socket(接口) 与 Model(策略)的桥梁,  对于Model来说, 不需要关心具体的下单细节, 只需要发出相应的买入卖出指令就可以了.

上面三个部分,`需要用户开发的只有Model`. 换句话说, 用户只要专注于交易策略, Socket和Trade会把剩下的所有交易细节都帮你做好.

## 1.2 AutoTrade可以做什么? 不能做什么?

> 可以做:
>> 股票的自动网格买卖<br>
>> 预设价格的自动盯盘交易<br>
>> 分级基金的自动化分拆/合并套利<br>
>> 股票异常价格捕捉和交易

>不能做:
>> 依靠速度取胜的策略<br>
>> 过于高频的交易<br>
>> 运算量过于庞大的策略<br>

## 1.3 AutoTrade是如何运行的?
AutoTrade 的运行分为三个大的阶段
> 1. 交易的准备
>> a. 登录券商系统<br>
>> b. 初始化log系统<br>

> 2. 策略的准备
>> a.载入用户策略<br>
>> b.将用户策略中关注的标的物加入关注表<br>

> 3. 策略的执行
>> a. 获取关注表中标的物的报价信息<br>
>> b. 将这些信息返回给策略模块<br>
>> c. 按照顺序执行各个策略模块(为了防止策略之间产生冲突, 策略模块按照顺序执行) <br>
>> d. 执行策略模块提交的交易请求<br>
>> e. 已经下达订单的状态更新等维护操作<br>

上面的三个阶段第1和第2均阶段在交易系统启动时执行一遍, 第三个阶段会反复执行, 直到发生错误或满足用户定义的退出条件.

![image](https://github.com/changye/AutoTrade/raw/master/Documents/image/start.jpg)

![image](https://github.com/changye/AutoTrade/raw/master/Documents/image/run.jpg)

# 准备工作
## 2.1 账户
使用本框架需要具备下面两个基本账户<br>
1. 广发证券账户, 作为下单账户<br>
2. 校验码在线识别账户, 本框架选择ruokuai.com进行校验码的在线识别(基本能够做到90%以上)<br>

## 2.2 广发证券登录秘钥生成
广发证券的web端口并不直接使用客户的用户名和交易密码登录, 它使用的是一个由用户名和密码加密后产生的秘钥对, 由于在网络上传输的是这个加密后的密钥对, 因此就不存在客户的真实用户名和密码泄露的情况.<br>
因此, 我们需要先生成加密后的秘钥对, 然后再使用这组密钥对登录广发证券的web接口. 生成密钥对利用了广发证券页面交易系统的web控件, 我们可以利用这个控件, 将密钥对生成并保存为配置文件, 这样AutoTrade框架就可以直接调用这个配置文件自动登录广发证券的web交易接口了.<br>

请按照下面的步骤获取交易密钥对:
1. 使用IE登录http://trade.gf.com.cn页面, 确保密码控件正确显示. (如果不显示,请按照提示安装控件)
![image](https://github.com/changye/AutoTrade/raw/master/Documents/image/控件准备.png)
2. 使用IE 打开Tools目录下的本地文件: "广发证券秘钥生成.html"
![image](https://github.com/changye/AutoTrade/raw/master/Documents/image/秘钥生成1.png)
3. 允许本地运行activex, 使控件可以在页面上正常显示
![image](https://github.com/changye/AutoTrade/raw/master/Documents/image/秘钥生成2.png)
4. 填写广发证券账号和密码, 点击生成秘钥. 注意, IE可能需要你允许ActiveX交互, 点击是,允许交互
![image](https://github.com/changye/AutoTrade/raw/master/Documents/image/秘钥生成3.png)
5. 生成秘钥后存储成文件, 建议不要使用windows自带的notepad, 使用sublime或者其他专业编辑文件, 并保存为utf8格式
![image](https://github.com/changye/AutoTrade/raw/master/Documents/image/秘钥生成4.png)
6. 将准备好的Socket.config.gf文件拷贝到AutoTrade的Configs目录下
至此, 广发证券的秘钥配置文件就准备好了


## 2.3 ruokuai账号申请


