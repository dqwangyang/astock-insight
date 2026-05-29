# 推荐个终端 A 股行情工具：astock-insight 🐍📈

每天开盘前打开好几个 App 拼数据，体验挺割裂的。写了个小工具彻底解决了这件事——**终端里一行命令，30 秒看完整市场**。

## 亮点

✅ **纯 Python，零依赖**（就用了标准库）  
✅ **数据来源公开 API**（腾讯/东方财富），合规免费  
✅ **涨绿跌红**，所有价格字段按方向着色  
✅ **Unicode K 线走势图** `▁▂▃▄▅▆▇█`  
✅ **多股盯盘**，无闪烁自动刷新  
✅ **安装即用**，`asi` 短命令开箱即用

## 用法

```bash
# 安装
git clone https://github.com/dqwangyang/astock-insight.git
cd astock-insight && pip install -e .

# 一键全景报告
asi all

# 个股行情 + K线走势
asi q sh600519

# 多股盯盘（5秒自动刷新）
asi q sh600519,sz300750 -w

# 大盘指数、板块排行
asi market
asi sec
```

## 适合谁

- 平时在终端工作的开发者/量化交易者
- 不想装太多股票 App 的人
- 想快速了解市场全貌的投资者

---

**GitHub**: [github.com/dqwangyang/astock-insight](https://github.com/dqwangyang/astock-insight)

觉得有用的话点个 Star ⭐ 就行，也欢迎扫码打赏 ☕
