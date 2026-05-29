"""
astock-insight CLI 入口

用法:
  astock-insight all                    # 全景报告
  astock-insight market                 # 大盘指数
  astock-insight sectors                # 行业板块排行
  astock-insight hot                    # 热门板块/热点
  astock-insight lhb                    # 龙虎榜
  astock-insight quote <code>           # 个股行情 (如 sh600519)
  astock-insight batch <codes>          # 批量行情 (逗号分隔)
  astock-insight status                 # 市场状态

所有命令支持 --watch / -w 开启持续刷新，例如:
  astock-insight market --watch         # 大盘持续盯盘
  astock-insight quote sh600519 -w      # 个股盯盘 (含K线走势图)
"""

import sys
import time
import io
from datetime import datetime

from . import __version__
from .fetcher import (
    fetch_index_quotes,
    fetch_hot_sectors,
    fetch_market_overview,
    fetch_lhb,
    fetch_stock_quote,
    fetch_kline,
    fetch_batch_quote,
    get_market_status,
    fetch_sector_rank,
    fetch_market_news,
)
from .reporter import (
    header_block,
    section,
    render_index_quotes,
    render_sectors,
    render_market_overview,
    render_lhb,
    render_stock_quote,
    render_report,
    render_kline_bars,
    render_recommendations,
    footer_line,
)


# ─── 无闪烁刷新循环 ──────────────────────────────────────────

def refresh_loop(render_func, interval=5):
    """
    无闪烁刷新循环。
    使用光标上移 + 覆盖写入，不会清屏/闪动。
    """
    lines_written = [0]

    def _render():
        # 捕获输出
        old = sys.stdout
        sys.stdout = buf = io.StringIO()
        try:
            render_func()
        finally:
            sys.stdout = old

        output = buf.getvalue()
        new_lines = output.count("\n")

        if lines_written[0] > 0:
            # 光标上移 + 清除剩余行 → 原位覆盖
            sys.stdout.write(f"\033[{lines_written[0]}A\033[J")

        sys.stdout.write(output)
        sys.stdout.flush()
        lines_written[0] = new_lines

    _render()
    try:
        while True:
            time.sleep(interval)
            _render()
    except KeyboardInterrupt:
        # 最后多空一行，保留输出
        print()


def with_watch(func, *args, **kwargs):
    """装饰：带 --watch 的版本"""
    watch = kwargs.pop("watch", False)
    interval = kwargs.pop("interval", 5)
    if watch:

        def _render():
            func(*args, **kwargs)

        refresh_loop(_render, interval)
    else:
        func(*args, **kwargs)


# ─── 命令实现 ────────────────────────────────────────────────

def cmd_all():
    """全景报告"""
    r = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "market_status": get_market_status(),
        "overview": fetch_market_overview(),
        "indices": fetch_index_quotes(),
        "sectors": fetch_sector_rank()[:10],
        "lhb": fetch_lhb("all")[:10],
        "hot": fetch_hot_sectors()[:10],
    }
    print(render_report(r))


def cmd_market():
    """大盘指数"""
    t = datetime.now().strftime("%H:%M:%S")
    s = get_market_status()
    print(header_block("主要指数行情", f"{t}  |  状态: {s}"))
    print(render_index_quotes(fetch_index_quotes()))
    print()
    print(render_market_overview(fetch_market_overview(), s))
    print(footer_line())


def cmd_sectors():
    """行业板块排行"""
    print(header_block("行业板块涨幅排行", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    print(render_sectors(fetch_sector_rank()))
    print(footer_line())


def cmd_hot():
    """热门板块"""
    print(header_block("市场热门板块", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    print(render_sectors(fetch_hot_sectors()))
    print(section("市场热点头条"))
    news = fetch_market_news(5)
    for i, n in enumerate(news, 1):
        name = n.get("name", "")
        pct = n.get("change_pct")
        if pct is not None:
            sign = "+" if pct > 0 else ""
            print(f"  {i}. {name}  ({sign}{pct:.2f}%)")
        else:
            print(f"  {i}. {name}")
    print(footer_line())


def cmd_lhb():
    """龙虎榜"""
    print(header_block("龙虎榜", datetime.now().strftime("%Y-%m-%d")))
    print(render_lhb(fetch_lhb("all")))
    print(section("机构榜"))
    print(render_lhb(fetch_lhb("jg")))
    print(section("游资榜"))
    print(render_lhb(fetch_lhb("yyb")))
    print(footer_line())


def cmd_quote(code: str):
    """个股行情（含K线走势图）"""
    t = datetime.now().strftime("%H:%M:%S")
    print(header_block("个股行情", f"{code}  |  {t}  |  状态: {get_market_status()}"))
    q = fetch_stock_quote(code)
    print(render_stock_quote(q, detail=True))

    # 附加 K 线走势图
    if q:
        print()
        klines = fetch_kline(code, limit=30)
        if klines:
            print(render_kline_bars(klines))
        else:
            print("  (K线数据获取中...)")
    print(footer_line())


def cmd_batch(codes_str: str):
    """批量行情"""
    codes = [c.strip() for c in codes_str.split(",") if c.strip()]
    if not codes:
        print("错误: 请至少提供一个股票代码")
        return
    t = datetime.now().strftime("%H:%M:%S")
    print(header_block("批量行情", f"{len(codes)} 只股票  |  {t}"))
    for code in codes:
        q = fetch_stock_quote(code)
        print(render_stock_quote(q, detail=True))
    print(footer_line())


def cmd_status():
    """市场状态"""
    status = get_market_status()
    indices = fetch_index_quotes()
    print(f"\n  市场状态: {status}")
    if indices:
        print()
        print(render_index_quotes(indices))


def cmd_recommend():
    """推荐关注 — 基于市场数据给出关注建议和理由"""
    t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(header_block("今日关注", f"{t}  |  状态: {get_market_status()}"))

    # 1. 大盘背景
    indices = fetch_index_quotes()
    overview = fetch_market_overview()
    market_context = f"大盘 {indices[0]['name']} {indices[0]['price']:.2f} ({indices[0]['change_pct']:+.2f}%)，"
    market_context += f"上涨 {overview.get('up',0)} 家 / 下跌 {overview.get('down',0)} 家"

    # 2. 热门板块
    hot = fetch_hot_sectors()[:5]
    sectors_data = []
    for s in hot:
        pct = s.get("change_pct", 0) or 0
        if pct >= 4:
            reason = "资金集中涌入，短线热度高"
        elif pct >= 2:
            reason = "板块联动效应明显，持续关注"
        elif pct >= 0:
            reason = "相对抗跌，防御性配置方向"
        else:
            reason = "短期承压，等待企稳信号"
        sectors_data.append({**s, "reason": reason})

    # 3. 龙虎榜亮点（机构买入）
    lhb_data = fetch_lhb("jg")[:3]
    lhb_picks = []
    for item in lhb_data:
        pct = item.get("change_pct", 0) or 0
        amt = item.get("amount", 0) or 0
        lhb_picks.append({
            "name": item.get("name", ""),
            "code": item.get("code", ""),
            "change_pct": pct,
            "reason": f"机构上榜，成交额 {amt:.0f}万"
        })

    print(render_recommendations({
        "market_context": market_context,
        "sectors": sectors_data,
        "lhb": lhb_picks,
    }))
    print(footer_line())


def _process_recommend(args):
    """处理推荐命令参数"""
    watch = "--watch" in args or "-w" in args
    args_clean = [a for a in args if a not in ("--watch", "-w")]
    return watch, args_clean


def cmd_version():
    """版本信息"""
    print(f"\n  astock-insight v{__version__}")
    print(f"  A股市场全景分析工具")
    print()


def usage():
    print(f"\n  astock-insight v{__version__} — A股市场全景分析工具\n")
    print("  用法:")
    print("    asi all              全景报告")
    print("    asi market           大盘指数")
    print("    asi sectors          行业板块排行")
    print("    asi hot              热门板块/热点")
    print("    asi lhb              龙虎榜")
    print("    asi pick             今日关注 (推荐+理由)")
    print("    asi q <代码>          个股行情 (含K线)")
    print("    asi b <代码们>        批量行情")
    print()
    print("  所有命令支持 -w 持续刷新:")
    print("    asi market -w        大盘盯盘")
    print("    asi q sh600519 -w    个股盯盘 (含K线)")
    print("    asi q sh600519,sz300750 -w  多股盯盘")
    print("    asi hot -w           板块盯盘")
    print("    asi pick -w          关注推荐刷新")
    print()


def main():
    if len(sys.argv) < 2:
        usage()
        return

    # 检测 --watch / -w 标志
    watch = "--watch" in sys.argv or "-w" in sys.argv
    # 过滤掉 watch 标志
    args = [a for a in sys.argv[1:] if a not in ("--watch", "-w")]

    if not args:
        usage()
        return

    cmd = args[0]

    if cmd in ("all", "-a", "--all"):
        if watch:
            refresh_loop(cmd_all, interval=10)
        else:
            cmd_all()
    elif cmd in ("market", "-m", "--market"):
        if watch:
            refresh_loop(cmd_market, interval=5)
        else:
            cmd_market()
    elif cmd in ("sectors", "sec", "s", "--sectors"):
        if watch:
            refresh_loop(cmd_sectors, interval=5)
        else:
            cmd_sectors()
    elif cmd in ("hot", "h", "--hot"):
        if watch:
            refresh_loop(cmd_hot, interval=5)
        else:
            cmd_hot()
    elif cmd in ("lhb", "--lhb", "longhu", "l"):
        if watch:
            refresh_loop(cmd_lhb, interval=10)
        else:
            cmd_lhb()
    elif cmd in ("recommend", "pick", "p", "推荐"):
        if watch:
            refresh_loop(cmd_recommend, interval=10)
        else:
            cmd_recommend()
    elif cmd in ("quote", "q"):
        if len(args) < 2:
            print("用法: astock-insight quote <股票代码1>,<股票代码2>,...")
            return
        codes_str = args[1]
        codes = [c.strip() for c in codes_str.split(",") if c.strip()]
        if watch:
            def _render_multi_quote():
                t = datetime.now().strftime("%H:%M:%S")
                codes_label = ",".join(codes)
                print(header_block("多股盯盘", f"{codes_label}  |  {t}  |  状态: {get_market_status()}  |  Ctrl+C 退出"))
                for code in codes:
                    q = fetch_stock_quote(code)
                    print(render_stock_quote(q, detail=True))
                    if q:
                        klines = fetch_kline(code, limit=30)
                        if klines:
                            print(render_kline_bars(klines))
                    print()
                print(footer_line())
            refresh_loop(_render_multi_quote, interval=5)
        elif len(codes) == 1:
            cmd_quote(codes[0])
        else:
            cmd_batch(codes_str)
    elif cmd in ("batch", "b"):
        if len(args) < 2:
            print("用法: astock-insight batch <代码1>,<代码2>,...")
            return
        if watch:
            codes_str = args[1]
            def _render_batch():
                cmd_batch(codes_str)
            refresh_loop(_render_batch, interval=5)
        else:
            cmd_batch(args[1])
    elif cmd in ("status", "st"):
        cmd_status()
    elif cmd in ("version", "-v", "--version"):
        cmd_version()
    else:
        print(f"未知命令: {cmd}")
        usage()


if __name__ == "__main__":
    main()
