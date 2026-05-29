# 📊 astock-insight

> **终端里的 A 股行情全景分析工具** | 不用打开 App，一行命令看遍大盘、板块、龙虎榜、个股

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)]()

---

## 为什么需要它？

每天开盘前，散户投资者通常要做这些事：

1. ❌ 打开多个 App —— 东方财富看大盘、同花顺看板块、雪球看龙虎榜
2. ❌ 手动记录数据 —— 把各个地方的数字拼成一张完整的市场图景
3. ❌ 等待加载 —— 每个 App 都要登录、看广告、等数据刷新

**astock-insight 解决了这一切** —— 打开终端，一行命令，30 秒内得到一份完整的 A 股全景报告。

> 特别适合：量化交易者、Python 用户、喜欢在终端工作的投资者、以及不想被 App 推送打扰的人。

---

## 快速开始

### 安装

```bash
# 方式一：从源码安装（推荐）
git clone https://github.com/astock-insight/astock-insight.git
cd astock-insight
pip install -e .

# 方式二：直接运行
git clone https://github.com/astock-insight/astock-insight.git
cd astock-insight
python -m astock_insight.cli all
```

### 使用

```bash
# 一键全景报告（推荐）
astock-insight all

# 只看大盘指数
astock-insight market

# 行业板块涨幅排行
astock-insight sectors

# 市场热门板块
astock-insight hot

# 龙虎榜（含机构榜 + 游资榜）
astock-insight lhb

# 个股行情
astock-insight quote sh600519

# 批量行情
astock-insight batch sh600519,sz000858,sz300750

# 市场交易状态
astock-insight status
```

---

## 功能一览

| 命令 | 功能 | 数据来源 |
|---|---|---|
| `all` | 全景报告：市场概况 + 指数 + 板块 + 龙虎榜 + 热点 | 腾讯财经/东方财富 |
| `market` | 大盘指数：上证、深证、创业板、科创50、沪深300、上证50、中证500 | 腾讯财经 |
| `sectors` | 申万一级行业板块涨幅排行（28个行业） | 东方财富 |
| `hot` | 热门板块 + 市场热点 | 东方财富 |
| `lhb` | 龙虎榜（全部/机构/游资三榜） | 东方财富 |
| `quote` | 个股实时行情（含PE、换手率、振幅、市值） | 腾讯财经 |
| `batch` | 批量个股行情对比 | 腾讯财经 |
| `status` | 市场交易状态（盘中/盘前/午间/收盘） | — |

### 数据来源

所有数据来自 **腾讯财经** 和 **东方财富** 的公开 API，合规、免费、无需注册。

> ⚠️ 数据延迟约 1-3 分钟，不构成投资建议，请以交易所官方数据为准。

---

## 输出预览

```
═══════════════════════════════════════════════════════
  📊 A股全景分析报告
  2026-05-29 15:10:43
═══════════════════════════════════════════════════════

▎ 市场概况
  市场状态: 交易中（下午）
  上涨 2856 家  (涨停 42 家)  | 下跌 1857 家  (跌停 8 家)  | 平盘 128 家
  总计: 4841 只股票

▎ 主要指数
  上证指数     3315.28   +15.67   +0.47%
  深证成指     11230.45  +89.23   +0.80%
  创业板指     2245.68   +22.15   +1.00%
  ...

▎ 行业板块涨幅排行 (Top 10)
  电子          +2.35%    +45.67
  计算机       +1.98%    +32.15
  通信         +1.45%    +18.90
  ...
```

---

## ⚙️ 技术细节

- 纯 Python 实现，零外部依赖（仅用标准库）
- 无需 API Key，无需注册，开箱即用
- 自动终端宽度适配
- 涨跌颜色标注（绿色涨 / 红色跌）

---

## ☕ 支持项目

如果这个工具对你有帮助，欢迎扫码请我喝杯咖啡 ❤️

<p align="center">
  <img src="./qrcode_alipay.jpg" alt="支付宝收款码" width="250"/>
</p>
<p align="center">
  <sub>你的每一杯咖啡，都是项目持续更新的动力 ☕</sub>
</p>

---

## License

MIT
