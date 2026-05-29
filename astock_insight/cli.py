"""
astock-insight CLI 入口

用法:
  astock-insight all              # 全景报告
  astock-insight market           # 大盘指数
  astock-insight sectors          # 行业板块排行
  astock-insight hot              # 热门板块/热点
  astock-insight lhb              # 龙虎榜
  astock-insight quote <code>     # 个股行情 (如 sh600519)
  astock-insight watch <code>     # 盯盘模式 (持续刷新)
  astock-insight batch <codes>    # 批量行情 (逗号分隔)
  astock-insight status           # 市场状态
  astock-insight version          # 版本信息
"""

import sys
import time
from datetime import datetime

from . import __version__
from .fetcher import (
    fetch_index_quotes,
    fetch_hot_sectors,
    fetch_market_overview,
    fetch_lhb,
    fetch_stock_quote,
    fetch_batch_quote,
    get_market_status,
    fetch_sector_rank,
    fetch_market_news,
)
from .reporter import (
    header_block,
    section,
    print_index_quotes,
    print_sectors,
    print_market_overview,
    print_lhb,
    print_stock_quote,
    print_footer,
    print_report,
)


def cmd_all():
    """全景报告"""
    report = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "market_status": get_market_status(),
        "overview": fetch_market_overview(),
        "indices": fetch_index_quotes(),
        "sectors": fetch_sector_rank()[:10],
        "lhb": fetch_lhb("all")[:10],
        "hot": fetch_hot_sectors()[:10],
    }
    print_report(report)


def cmd_market():
    """大盘指数"""
    header_block("主要指数行情", f"更新时间: {datetime.now().strftime('%H:%M:%S')}  |  状态: {get_market_status()}")
    indices = fetch_index_quotes()
    print_index_quotes(indices)

    overview = fetch_market_overview()
    print()
    print_market_overview(overview, get_market_status())
    print_footer()


def cmd_sectors():
    """行业板块排行"""
    header_block("行业板块涨幅排行", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    sectors = fetch_sector_rank()
    print_sectors(sectors)
    print_footer()


def cmd_hot():
    """热门板块"""
    header_block("市场热门板块", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    hot = fetch_hot_sectors()
    print_sectors(hot)

    section("市场热点头条")
    news = fetch_market_news(5)
    for i, n in enumerate(news, 1):
        name = n.get("name", "")
        pct = n.get("change_pct")
        if pct is not None:
            sign = "+" if pct > 0 else ""
            print(f"  {i}. {name}  ({sign}{pct:.2f}%)")
        else:
            print(f"  {i}. {name}")
    print_footer()


def cmd_lhb():
    """龙虎榜"""
    header_block("龙虎榜", datetime.now().strftime("%Y-%m-%d"))
    lhb_data = fetch_lhb("all")
    print_lhb(lhb_data)

    section("机构榜")
    jg_data = fetch_lhb("jg")
    print_lhb(jg_data)

    section("游资榜")
    yyb_data = fetch_lhb("yyb")
    print_lhb(yyb_data)
    print_footer()


def cmd_quote(code: str):
    """个股行情"""
    header_block("个股行情", code)
    q = fetch_stock_quote(code)
    print_stock_quote(q, detail=True)
    print_footer()


def cmd_watch(code: str):
    """盯盘模式 — 持续刷新个股行情"""
    interval = 5  # 刷新间隔（秒）
    print(f"\n  🔴 盯盘模式: {code}  |  每 {interval} 秒自动刷新  |  按 Ctrl+C 退出\n")

    first = True
    try:
        while True:
            if not first:
                time.sleep(interval)
                # 清除屏幕（ANSI 转义）
                print("\033c", end="")
                print(f"  🔴 盯盘模式: {code}  |  每 {interval} 秒自动刷新  |  按 Ctrl+C 退出\n")
            first = False

            q = fetch_stock_quote(code)
            if not q:
                print(f"  ❌ 查询失败: {code}")
                continue

            name = q.get("name", code)
            price = q.get("price", 0)
            pct = q.get("change_pct", 0)
            chg = q.get("change", 0)
            sign = "+" if pct > 0 else ""

            ts = datetime.now().strftime("%H:%M:%S")
            print(f"  [{ts}]  {name}  ({code})")
            print(f"  {'─' * 40}")
            print(f"  现价: {price:.2f}")
            print(f"  涨幅: {sign}{pct:.2f}%   涨跌: {sign}{chg:.2f}")
            print(f"  最高: {q.get('high', 0):.2f}   最低: {q.get('low', 0):.2f}")
            print(f"  开盘: {q.get('open', 0):.2f}   昨收: {q.get('pre_close', 0):.2f}")
            print(f"  成交量: {_fmt_vol(q.get('volume', 0))}  换手率: {q.get('turnover_rate', 'N/A')}%")

    except KeyboardInterrupt:
        print("\n\n  👋 盯盘结束")


def _fmt_vol(v: float) -> str:
    if v > 10000:
        return f"{v / 10000:.2f}亿"
    return f"{v:.0f}万"


def cmd_batch(codes_str: str):
    """批量行情"""
    codes = [c.strip() for c in codes_str.split(",") if c.strip()]
    if not codes:
        print("错误: 请至少提供一个股票代码")
        return
    header_block("批量行情", f"{len(codes)} 只股票")
    for code in codes:
        q = fetch_stock_quote(code)
        print_stock_quote(q, detail=True)
    print_footer()


def cmd_status():
    """市场状态"""
    status = get_market_status()
    indices = fetch_index_quotes()
    print(f"\n  市场状态: {status}")
    if indices:
        print()
        print_index_quotes(indices)


def cmd_version():
    """版本信息"""
    print(f"\n  astock-insight v{__version__}")
    print(f"  A股市场全景分析工具")
    print()


def usage():
    print(f"\n  astock-insight v{__version__} — A股市场全景分析工具\n")
    print("  用法:")
    print(f"    astock-insight all             全景报告")
    print(f"    astock-insight market          大盘指数")
    print(f"    astock-insight sectors         行业板块排行")
    print(f"    astock-insight hot             热门板块/热点")
    print(f"    astock-insight lhb             龙虎榜")
    print(f"    astock-insight quote <代码>     个股行情")
    print(f"    astock-insight watch <代码>     盯盘模式 (每5秒刷新)")
    print(f"    astock-insight batch <代码们>   批量行情")
    print(f"    astock-insight status          市场状态")
    print(f"    astock-insight version        版本信息")
    print()


def main():
    if len(sys.argv) < 2:
        usage()
        return

    cmd = sys.argv[1]

    if cmd in ("all", "-a", "--all"):
        cmd_all()
    elif cmd in ("market", "-m", "--market"):
        cmd_market()
    elif cmd in ("sectors", "--sectors"):
        cmd_sectors()
    elif cmd in ("hot", "--hot"):
        cmd_hot()
    elif cmd in ("lhb", "--lhb", "longhu"):
        cmd_lhb()
    elif cmd in ("quote", "q"):
        if len(sys.argv) < 3:
            print("用法: astock-insight quote <股票代码>")
            return
        cmd_quote(sys.argv[2])
    elif cmd in ("watch", "w", "live"):
        if len(sys.argv) < 3:
            print("用法: astock-insight watch <股票代码>")
            return
        cmd_watch(sys.argv[2])
    elif cmd in ("batch", "b"):
        if len(sys.argv) < 3:
            print("用法: astock-insight batch <代码1>,<代码2>,...")
            return
        cmd_batch(sys.argv[2])
    elif cmd in ("status", "st"):
        cmd_status()
    elif cmd in ("version", "-v", "--version"):
        cmd_version()
    else:
        print(f"未知命令: {cmd}")
        usage()


if __name__ == "__main__":
    main()
