"""
报告格式化模块 — 输出美观的终端表格和报告
"""

import shutil

# ANSI 颜色 (使用基础 8/16 色，兼容性更好)
GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
BOLD = "\033[1m"
RESET = "\033[0m"
DIM = "\033[2m"

# 判断终端是否支持颜色
import sys
_HAS_COLOR = sys.stdout.isatty()


def _c(color: str, text: str) -> str:
    """带颜色的文本，TTY 输出颜色，否则输出纯文本"""
    if _HAS_COLOR:
        return f"{color}{text}{RESET}"
    return text


def term_width() -> int:
    return shutil.get_terminal_size((80, 24)).columns


def _color_pct(pct: float) -> str:
    if pct > 0:
        return _c(GREEN, f"+{pct:.2f}%")
    elif pct < 0:
        return _c(RED, f"{pct:.2f}%")
    return f"{pct:.2f}%"


def _color_change(val: float) -> str:
    if val > 0:
        return _c(GREEN, f"+{val:.2f}")
    elif val < 0:
        return _c(RED, f"{val:.2f}")
    return f"{val:.2f}"


def _color_price(val: float) -> str:
    """价格着色：涨绿色，跌红色"""
    return str(val)


def _fmt_vol(v: float) -> str:
    if v > 10000:
        return f"{v / 10000:.2f}亿"
    if v > 1:
        return f"{v:.2f}亿"
    return f"{v * 10000:.0f}万"


def header_block(title: str, subtitle: str = "") -> str:
    w = term_width()
    lines = [f"\n{BOLD}{CYAN}  {title}{RESET}"]
    if subtitle:
        lines.append(f"  {DIM}{subtitle}{RESET}")
    lines.append(f"  {DIM}{'═' * w}{RESET}")
    return "\n".join(lines)


def section(title: str) -> str:
    w = term_width()
    return f"\n{BOLD}▎ {title}{RESET}\n  {DIM}{'─' * w}{RESET}"


def footer_line() -> str:
    w = term_width()
    lines = [
        f"\n  {DIM}{'─' * w}{RESET}",
        f"  {DIM}数据来源: 腾讯财经/东方财富公开API | 数据延迟约1-3分钟 | 不构成投资建议{RESET}",
        f"  {DIM}如果对你有用，欢迎扫码请我喝杯咖啡 ☕{RESET}",
    ]
    return "\n".join(lines)


def render_index_quotes(indices: list[dict]) -> str:
    if not indices:
        return "  (暂无数据)"
    lines = []
    col_w = max(len(idx["name"]) for idx in indices) + 2
    for idx in indices:
        name = idx["name"].ljust(col_w)
        price = f"{idx['price']:.2f}".rjust(10)
        chg = _color_change(idx["change"]).rjust(12)
        pct = _color_pct(idx["change_pct"]).rjust(12)
        lines.append(f"  {name} {price}  {chg}  {pct}")
    return "\n".join(lines)


def render_sectors(sectors: list[dict]) -> str:
    if not sectors:
        return "  (暂无数据)"
    lines = [
        f"  {DIM}{'名称'.ljust(16)} {'涨幅'.rjust(8)}  {'涨跌额'.rjust(8)}{RESET}",
        f"  {DIM}{'─' * 38}{RESET}",
    ]
    for s in sectors:
        name = s["name"][:10].ljust(16) if s["name"] else "".ljust(16)
        pct = _color_pct(s.get("change_pct", 0)).rjust(12)
        chg = _color_change(s.get("change", 0)).rjust(12)
        lines.append(f"  {name} {pct}  {chg}")
    return "\n".join(lines)


def render_market_overview(ov: dict, status: str) -> str:
    up = ov.get("up", 0)
    down = ov.get("down", 0)
    flat = ov.get("flat", 0)
    limit_up = ov.get("limit_up", 0)
    limit_down = ov.get("limit_down", 0)
    total = up + down + flat

    up_str = _c(GREEN, f"{up} 家")
    down_str = _c(RED, f"{down} 家")
    lu_str = _c(GREEN, f"涨停 {limit_up} 家")
    ld_str = _c(RED, f"跌停 {limit_down} 家")

    lines = [
        f"  市场状态: {CYAN}{status}{RESET}",
        f"  上涨 {up_str}  ({lu_str})  | 下跌 {down_str}  ({ld_str})  | 平盘 {flat} 家",
        f"  总计: {total} 只股票",
    ]
    return "\n".join(lines)


def render_lhb(lhb_list: list[dict]) -> str:
    if not lhb_list:
        return "  (暂无数据)"
    lines = [
        f"  {DIM}{'代码'.ljust(10)} {'名称'.ljust(10)} {'涨跌幅'.rjust(8)}  {'成交额(万)'.rjust(12)}  {'上榜原因'}{RESET}",
        f"  {DIM}{'─' * 60}{RESET}",
    ]
    for item in lhb_list:
        code = item.get("code", "")[:8].ljust(10)
        name = item.get("name", "")[:8].ljust(10)
        pct = _color_pct(item.get("change_pct", 0)).rjust(12)
        amt = f"{item.get('amount', 0):.2f}".rjust(12)
        reason = (item.get("reason", "") or "")[:20]
        lines.append(f"  {code} {name}  {pct}  {amt}  {reason}")
    return "\n".join(lines)


def render_stock_quote(q: dict, detail: bool = False) -> str:
    if not q:
        return "  (查询失败)"
    name = q.get("name", q.get("code", ""))
    pct = q.get("change_pct", 0)
    sign = "+" if pct > 0 else ""

    if pct > 0:
        price_color = GREEN
    elif pct < 0:
        price_color = RED
    else:
        price_color = ""

    price_val = q.get("price", 0)
    chg_val = q.get("change", 0)
    open_val = q.get("open", 0)
    high_val = q.get("high", 0)
    low_val = q.get("low", 0)
    pre_close_val = q.get("pre_close", 0)
    vol_val = q.get("volume", 0)
    amt_val = q.get("amount", 0)
    tr_val = q.get("turnover_rate", "N/A")
    pe_val = q.get("pe", "N/A")
    amp_val = q.get("amplitude", "N/A")

    lines = [
        f"\n  {BOLD}{name}{RESET}  {q.get('code', '')}",
        f"  现价: {_c(price_color, f'{price_val:.2f}')}  "
        f"涨幅: {_c(price_color, sign + str(pct) + '%')}  "
        f"涨跌: {_c(price_color, sign + f'{chg_val:.2f}')}",
    ]
    if detail:
        lines.append(
            f"  开盘: {_c(price_color, f'{open_val:.2f}')}  "
            f"最高: {_c(price_color, f'{high_val:.2f}')}  "
            f"最低: {_c(price_color, f'{low_val:.2f}')}  "
            f"昨收: {pre_close_val:.2f}"
        )
        lines.append(
            f"  成交量: {_fmt_vol(vol_val)}  "
            f"成交额: {_fmt_vol(amt_val)}  "
            f"换手率: {tr_val}%"
        )
        lines.append(f"  市盈率: {pe_val}  振幅: {amp_val}%")
    return "\n".join(lines)


def render_report(report: dict) -> str:
    w = term_width()
    parts = [
        "",
        f"{BOLD}{CYAN}{'═' * w}{RESET}",
        f"{BOLD}{CYAN}  📊 A股全景分析报告{RESET}",
        f"  {DIM}{report.get('timestamp', '')}{RESET}",
        f"{BOLD}{CYAN}{'═' * w}{RESET}",
        section("市场概况"),
        render_market_overview(report.get("overview", {}), report.get("market_status", "")),
        section("主要指数"),
        render_index_quotes(report.get("indices", [])),
        section("行业板块涨幅排行 (Top 10)"),
        render_sectors(report.get("sectors", [])),
        section("龙虎榜 (Top 10)"),
    ]
    lhb_list = report.get("lhb", [])
    if lhb_list:
        parts.append(render_sectors([
            {"name": item.get("name", ""), "change_pct": item.get("change_pct", 0),
             "change": item.get("amount", 0)} for item in lhb_list[:10]
        ]))
    else:
        parts.append("  (暂无龙虎榜数据)")

    parts.append(section("市场热点"))
    parts.append(render_sectors(report.get("hot", [])))
    parts.append(footer_line())
    return "\n".join(parts)


# ─── Sparkline (迷你K线) ───────────────────────────────────

SPARK_CHARS = "▁▂▃▄▅▆▇█"


def render_sparkline(values: list[float], width: int = 30) -> str:
    """用 unicode 字符绘制迷你折线图"""
    if not values:
        return ""
    if len(values) > width:
        step = len(values) / width
        sampled = [values[int(i * step)] for i in range(width)]
    else:
        sampled = values
    mn, mx = min(sampled), max(sampled)
    rng = mx - mn if mx != mn else 1
    chars = "".join(SPARK_CHARS[min(int((v - mn) / rng * 7), 7)] for v in sampled)
    return chars


def render_kline_bars(klines: list[dict], width: int = 30) -> str:
    """用字符绘制 K 线柱状图（收盘价）"""
    if not klines:
        return ""
    closes = [k["close"] for k in klines]
    spark = render_sparkline(closes, width)
    first = closes[0]
    last = closes[-1]
    direction = GREEN if last >= first else RED
    change = last - first
    pct = (change / first * 100) if first else 0
    return (
        f"  走势 ({len(klines)}日): {_c(direction, spark)}\n"
        f"  区间: {_c(direction, f'{first:.2f} → {last:.2f}  ({change:+.2f}, {pct:+.2f}%)')}"
    )
