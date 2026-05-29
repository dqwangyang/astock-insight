"""
报告格式化模块 — 输出美观的终端表格和报告
"""

import shutil

# ANSI 颜色
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"
DIM = "\033[2m"


def term_width() -> int:
    return shutil.get_terminal_size((80, 24)).columns


def _color_pct(pct: float) -> str:
    """涨跌幅着色"""
    if pct > 0:
        return f"{GREEN}+{pct:.2f}%{RESET}"
    elif pct < 0:
        return f"{RED}{pct:.2f}%{RESET}"
    return f"{pct:.2f}%"


def _color_change(val: float) -> str:
    if val > 0:
        return f"{GREEN}+{val:.2f}{RESET}"
    elif val < 0:
        return f"{RED}{val:.2f}{RESET}"
    return f"{val:.2f}"


def _fmt_vol(v: float) -> str:
    """格式化成交量"""
    if v > 10000:
        return f"{v / 10000:.2f}亿"
    return f"{v:.0f}万"


def _fmt_amount(v: float) -> str:
    """格式化成交额"""
    if v > 10000:
        return f"{v / 10000:.2f}万亿"
    if v > 1:
        return f"{v:.2f}亿"
    return f"{v * 10000:.0f}万"


def header_block(title: str, subtitle: str = "") -> None:
    """打印标题块"""
    w = term_width()
    line = "═" * w
    print(f"\n{BOLD}{CYAN}  {title}{RESET}")
    if subtitle:
        print(f"  {DIM}{subtitle}{RESET}")
    print(f"  {DIM}{line}{RESET}")


def section(title: str) -> None:
    """打印小节标题"""
    print(f"\n{BOLD}▎ {title}{RESET}")
    print(f"  {DIM}{'─' * term_width()}{RESET}")


def print_index_quotes(indices: list[dict]) -> None:
    """打印指数行情"""
    if not indices:
        print("  (暂无数据)")
        return
    col_w = max(len(idx["name"]) for idx in indices) + 2
    for idx in indices:
        name = idx["name"].ljust(col_w)
        price = f"{idx['price']:.2f}".rjust(10)
        chg = _color_change(idx["change"]).rjust(12)
        pct = _color_pct(idx["change_pct"]).rjust(12)
        print(f"  {name} {price}  {chg}  {pct}")


def print_sectors(sectors: list[dict], title: str = "热门板块") -> None:
    """打印板块排行"""
    if not sectors:
        print("  (暂无数据)")
        return
    print(f"  {DIM}{'名称'.ljust(16)} {'涨幅'.rjust(8)}  {'涨跌额'.rjust(8)}{RESET}")
    print(f"  {DIM}{'─' * 38}{RESET}")
    for s in sectors:
        name = s["name"][:10].ljust(16) if s["name"] else "".ljust(16)
        pct = _color_pct(s.get("change_pct", 0)).rjust(12)
        chg = _color_change(s.get("change", 0)).rjust(12)
        print(f"  {name} {pct}  {chg}")


def print_market_overview(ov: dict, status: str) -> None:
    """打印市场概况"""
    total = ov.get("up", 0) + ov.get("down", 0) + ov.get("flat", 0)
    print(f"  市场状态: {CYAN}{status}{RESET}")
    print(f"  上涨 {GREEN}{ov.get('up', 0)} 家{RESET}"
          f"  (涨停 {GREEN}{ov.get('limit_up', 0)} 家{RESET})"
          f"  | 下跌 {RED}{ov.get('down', 0)} 家{RESET}"
          f"  (跌停 {RED}{ov.get('limit_down', 0)} 家{RESET})"
          f"  | 平盘 {ov.get('flat', 0)} 家")
    print(f"  总计: {total} 只股票")


def print_lhb(lhb_list: list[dict]) -> None:
    """打印龙虎榜"""
    if not lhb_list:
        print("  (暂无数据)")
        return
    print(f"  {DIM}{'代码'.ljust(10)} {'名称'.ljust(10)} {'涨跌幅'.rjust(8)}  {'成交额(万)'.rjust(12)}  {'上榜原因'}{RESET}")
    print(f"  {DIM}{'─' * 60}{RESET}")
    for item in lhb_list:
        code = item.get("code", "")[:8].ljust(10)
        name = item.get("name", "")[:8].ljust(10)
        pct = _color_pct(item.get("change_pct", 0)).rjust(12)
        amt = f"{item.get('amount', 0):.2f}".rjust(12)
        reason = (item.get("reason", "") or "")[:20]
        print(f"  {code} {name}  {pct}  {amt}  {reason}")


def print_stock_quote(q: dict, detail: bool = False) -> None:
    """打印个股行情"""
    if not q:
        print("  (查询失败)")
        return
    name = q.get("name", q.get("code", ""))
    pct = q.get("change_pct", 0)
    sign = "+" if pct > 0 else ""
    print(f"\n  {BOLD}{name}{RESET}  {q.get('code', '')}")
    print(f"  现价: {q.get('price', 0):.2f}  "
          f"涨幅: {sign}{pct:.2f}%  "
          f"涨跌: {sign}{q.get('change', 0):.2f}")
    if detail:
        print(f"  开盘: {q.get('open', 0):.2f}  "
              f"最高: {q.get('high', 0):.2f}  "
              f"最低: {q.get('low', 0):.2f}  "
              f"昨收: {q.get('pre_close', 0):.2f}")
        print(f"  成交量: {_fmt_vol(q.get('volume', 0))}  "
              f"成交额: {_fmt_amount(q.get('amount', 0))}  "
              f"换手率: {q.get('turnover_rate', 'N/A')}%")
        pe = q.get('pe', 'N/A')
        print(f"  市盈率: {pe}  振幅: {q.get('amplitude', 'N/A')}%")


def print_footer() -> None:
    """打印页脚"""
    w = term_width()
    print(f"\n  {DIM}{'─' * w}{RESET}")
    print(f"  {DIM}数据来源: 腾讯财经/东方财富公开API | "
          f"数据延迟约1-3分钟 | 不构成投资建议{RESET}")
    print(f"  {DIM}如果对你有用，欢迎扫码请我喝杯咖啡 ☕{RESET}")
    print()


def print_report(report: dict) -> None:
    """打印全景报告"""
    print()
    w = term_width()
    print(f"{BOLD}{CYAN}{'═' * w}{RESET}")
    title = "📊 A股全景分析报告"
    ts = report.get("timestamp", "")
    print(f"{BOLD}{CYAN}  {title}{RESET}")
    print(f"  {DIM}{ts}{RESET}")
    print(f"{BOLD}{CYAN}{'═' * w}{RESET}")

    # 市场状态
    section("市场概况")
    print_market_overview(report.get("overview", {}), report.get("market_status", ""))

    # 指数行情
    section("主要指数")
    print_index_quotes(report.get("indices", []))

    # 行业涨幅前10
    section("行业板块涨幅排行 (Top 10)")
    print_sectors(report.get("sectors", []))

    # 龙虎榜
    section("龙虎榜 (Top 10)")
    lhb_list = report.get("lhb", [])
    if lhb_list:
        print_sectors([{
            "name": item.get("name", ""),
            "change_pct": item.get("change_pct", 0),
            "change": item.get("amount", 0),
        } for item in lhb_list[:10]])
    else:
        print("  (暂无龙虎榜数据)")

    # 市场热点
    section("市场热点")
    hot_list = report.get("hot", [])
    print_sectors(hot_list)

    print_footer()
