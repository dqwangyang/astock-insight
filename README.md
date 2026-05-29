# 📊 astock-insight / asi

> **A-share Market Terminal Toolkit** | A股行情终端工具，一行命令看遍大盘、板块、龙虎榜、个股

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)]()
[![GitHub](https://img.shields.io/badge/github-dqwangyang%2Fastock--insight-brightgreen)](https://github.com/dqwangyang/astock-insight)

---

## 🇨🇳 中文

### 为什么需要它？

每天开盘前，散户投资者通常要打开多个 App —— 东方财富看大盘、同花顺看板块、雪球看龙虎榜，手动把数据拼成一张完整的市场图景。

**astock-insight 解决了这一切** —— 打开终端，一行命令，30 秒内拿到完整的 A 股全景分析报告。

> 特别适合：量化交易者、Python 用户、终端工作者、不想被 App 推送打扰的人。

### 安装

```bash
git clone https://github.com/dqwangyang/astock-insight.git
cd astock-insight
pip install -e .
```

安装后 `asi` 和 `astock-insight` 两个命令都可直接使用。

### 快速上手

```bash
asi                    # 查看帮助
asi all                # 全景报告（大盘 + 板块 + 龙虎榜 + 热点）
asi q sh600519         # 个股行情（含30日K线走势图）
asi q sh600519,sz300750 -w    # 多股盯盘（每5秒自动刷新，无闪烁）
asi market -w          # 大盘实时盯盘
asi sec                # 行业板块排行
asi h -w               # 热门板块持续刷新
asi b sh600519,sz300750       # 批量行情对比
```

### 功能一览

| 命令 | 短名 | 功能 | 自动刷新 |
|------|------|------|---------|
| `all` | — | 全景报告（市场概况+指数+板块+龙虎榜+热点） | `-w` |
| `market` | — | 7大指数实时行情 + 涨跌家数统计 | `-w` |
| `sectors` | `sec` / `s` | 28个申万一级行业板块排行 | `-w` |
| `hot` | `h` | 热门概念板块 + 市场热点 | `-w` |
| `lhb` | — | 龙虎榜（全部/机构/游资三榜） | `-w` |
| `quote` | `q` | 个股行情（含PE/换手率/K线走势图） | `-w` |
| `batch` | `b` | 批量个股行情对比 | `-w` |
| `status` | — | 市场交易状态 | — |

> 所有查询命令加 `-w` 进入持续刷新模式（无闪烁，光标覆盖刷新）

### 输出示例

```
$ asi q sh600519

  个股行情
  sh600519  |  16:05:58  |  状态: 已收盘
  ════════════════════════════════════════════

  贵州茅台  sh600519
  现价: 1326.00  涨幅: +3.92%  涨跌: +50.02
  开盘: 1270.60  最高: 1329.00  最低: 1270.00  昨收: 1275.98
  成交量: 7.65亿  成交额: 4.35亿  换手率: 0.61%
  市盈率: 20.04  振幅: 4.62%

  走势 (30日): █▇▅▅▅▅▆▇▅▅▅▅▄▄▄▄▃▃▃▃▂▂▂▂▁▁▁▂▁▂
  区间: 1467.50 → 1326.00  (-141.50, -9.64%)
```

> 涨绿色 / 跌红色，所有价格字段按方向着色。

### 数据来源

- **腾讯财经** (`qt.gtimg.cn`) — 指数行情、个股行情、K线数据
- **东方财富** (`push2.eastmoney.com`) — 板块排行、龙虎榜、市场热点

所有数据来自公开 API，无需注册、无需 API Key。

> ⚠️ 数据延迟约 1-3 分钟，不构成投资建议，请以交易所官方数据为准。

### 技术特点

- 纯 Python 实现，零外部依赖（仅用标准库）
- 无需 API Key、无需注册、开箱即用
- 自动终端宽度适配
- 涨跌 ANSI 颜色标注
- Unicode Sparkline K线走势图（`▁▂▃▄▅▆▇█`）
- 无闪烁自动刷新模式（光标覆盖写入）

---

## 🇬🇧 English

### Why astock-insight?

Every trading day, retail investors typically open multiple apps — East Money for indices, Flush for sectors, Xueqiu for block trades — then manually stitch the data together.

**astock-insight solves this**: open your terminal, one command, and get a complete A-share market overview in 30 seconds.

> Perfect for: quants, Python devs, terminal lovers, anyone tired of app notifications.

### Installation

```bash
git clone https://github.com/dqwangyang/astock-insight.git
cd astock-insight
pip install -e .
```

Both `asi` and `astock-insight` commands are available after installation.

### Quick Start

```bash
asi                    # Show help
asi all                # Full market report (indices + sectors + block trades + trends)
asi q sh600519         # Stock quote with 30-day K-line sparkline
asi q sh600519,sz300750 -w    # Watch multiple stocks (auto-refresh every 5s, no flicker)
asi market -w          # Real-time index monitoring
asi sec                # Industry sector ranking
asi h -w               # Hot sector auto-refresh
asi b sh600519,sz300750       # Batch stock comparison
```

### Feature Overview

| Command | Alias | Description | Watch Mode |
|---------|-------|-------------|-----------|
| `all` | — | Full market report | `-w` |
| `market` | — | 7 major indices + up/down count | `-w` |
| `sectors` | `sec` / `s` | 28 SW-classified industry sectors | `-w` |
| `hot` | `h` | Hot concept sectors | `-w` |
| `lhb` | — | Block trades (all/institutional/retail) | `-w` |
| `quote` | `q` | Stock quote (PE/turnover/K-line chart) | `-w` |
| `batch` | `b` | Batch stock comparison | `-w` |
| `status` | — | Market trading status | — |

> Add `-w` to any query command for flicker-free auto-refresh mode.

### Output Preview

```
$ asi q sh600519

  Stock Quote
  sh600519  |  16:05:58  |  Status: Closed
  ════════════════════════════════════════════

  Kweichow Moutai  sh600519
  Price: 1326.00  Change: +3.92%  +/-: +50.02
  Open: 1270.60  High: 1329.00  Low: 1270.00  Prev: 1275.98
  Volume: 765M  Amount: 435M  Turnover: 0.61%
  P/E: 20.04  Amplitude: 4.62%

  K-line (30d): █▇▅▅▅▅▆▇▅▅▅▅▄▄▄▄▃▃▃▃▂▂▂▂▁▁▁▂▁▂
  Range: 1467.50 → 1326.00  (-141.50, -9.64%)
```

> Green for up, Red for down — all price fields colored by direction.

### Data Sources

- **Tencent Finance** (`qt.gtimg.cn`) — Indices, stock quotes, K-line data
- **East Money** (`push2.eastmoney.com`) — Sector rankings, block trades, market trends

All data from public APIs. No registration or API keys required.

> ⚠️ Data delay ~1-3 minutes. Not investment advice. Always refer to official exchange data.

### Tech Highlights

- Pure Python, zero external dependencies (stdlib only)
- No API keys, no registration
- Auto terminal width detection
- ANSI color-coded by direction (green up / red down)
- Unicode sparkline K-line chart (`▁▂▃▄▅▆▇█`)
- Flicker-free auto-refresh via cursor-overwrite

---

## ☕ Support / 支持项目

If you find this tool helpful, feel free to buy me a coffee ❤️

如果这个工具对你有帮助，欢迎扫码请我喝杯咖啡 ☕

<p align="center">
  <img src="./qrcode_alipay.jpg" alt="支付宝收款码 / Alipay QR" width="250"/>
</p>
<p align="center">
  <sub>Every coffee keeps the project alive ☕</sub>
</p>

---

## License

MIT
