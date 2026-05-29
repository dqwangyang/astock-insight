"""
数据获取模块 — 从公开接口拉取A股市场数据
数据来源：腾讯/新浪/东方财富公开API，完全合规，仅用于信息展示
"""

import json
import time
import urllib.request
import urllib.parse
import ssl

# 禁用SSL证书验证（兼容部分环境）
ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE


def _fetch(url: str, timeout: int = 10, encoding: str | None = None) -> str:
    """通用HTTP GET请求"""
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Referer": "https://qt.gtimg.cn/",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout, context=ssl_ctx) as resp:
        raw = resp.read()
    if encoding:
        return raw.decode(encoding, errors="replace")
    # 尝试 UTF-8，如果失败则回退 GBK
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("gbk", errors="replace")


def _extract_json(raw: str) -> str:
    """从 callback 包裹格式 (如 jQuery({...})) 中提取纯JSON"""
    s = raw.strip()
    # 处理 jQuery({...}) 或 var xxx={...} 格式
    paren = s.find("(")
    brace = s.find("{")
    if paren >= 0 and (brace < 0 or paren < brace):
        # 找到第一个 '(' 和最后一个 ')'
        start = paren + 1
        end = s.rfind(")")
        if end > start:
            return s[start:end]
    if brace >= 0:
        return s[brace:s.rfind("}") + 1]
    return s


def _fetch_json(url: str, timeout: int = 10) -> dict:
    """JSON接口请求"""
    data = _fetch(url, timeout)
    cleaned = _extract_json(data)
    return json.loads(cleaned)


# ─── 指数实时行情 ─────────────────────────────────────────────

# 常用指数代码
INDEX_MAP = {
    "sh000001": ("上证指数", "000001"),
    "sz399001": ("深证成指", "399001"),
    "sz399006": ("创业板指", "399006"),
    "sh000688": ("科创50", "000688"),
    "sh000300": ("沪深300", "000300"),
    "sh000016": ("上证50", "000016"),
    "sh000905": ("中证500", "000905"),
}

def fetch_index_quotes() -> list[dict]:
    """获取主要指数实时行情（腾讯接口）"""
    codes = ",".join(k for k in INDEX_MAP)
    url = f"https://qt.gtimg.cn/q={codes}"
    raw = _fetch(url)
    results = []
    for line in raw.strip().split("\n"):
        line = line.strip()
        if not line or not line.startswith("v_"):
            continue
        # 解析腾讯返回格式
        try:
            parts = line.split("~")
            if len(parts) < 40:
                continue
            code_full = parts[0].split("=")[0].replace("v_", "")
            name = parts[1]
            price = float(parts[3]) if parts[3] else 0
            change = float(parts[31]) if parts[31] else 0     # 涨跌额
            change_pct = float(parts[32]) if parts[32] else 0  # 涨跌幅%
            open_p = float(parts[5]) if parts[5] else 0
            high = float(parts[33]) if parts[33] else 0
            low = float(parts[34]) if parts[34] else 0
            pre_close = float(parts[4]) if parts[4] else 0
            volume = float(parts[6]) if parts[6] else 0       # 手
            amount = float(parts[7]) if parts[7] else 0        # 万
            results.append({
                "code": code_full,
                "name": name,
                "price": price,
                "change": change,
                "change_pct": change_pct,
                "open": open_p,
                "high": high,
                "low": low,
                "pre_close": pre_close,
                "volume": volume,
                "amount": amount,
            })
        except (ValueError, IndexError):
            continue
    return results


# ─── 热门板块排行 ───────────────────────────────────────────

def _fetch_em_qlist(url: str) -> list[dict]:
    """通用：解析东方财富 clist/get 接口返回的 diff 列表"""
    try:
        data = _fetch_json(url)
        items = data.get("data", {}).get("diff", [])
        if not items:
            return []
        results = []
        for item in items:
            # 东方财富的涨跌幅是千分比（164 = 1.64%），需除以100
            raw_pct = item.get("f3")
            raw_chg = item.get("f4")
            change_pct = raw_pct / 100 if raw_pct is not None else None
            change = raw_chg / 100 if raw_chg is not None else None
            results.append({
                "code": item.get("f12", ""),
                "name": item.get("f14", ""),
                "price": item.get("f2"),
                "change_pct": change_pct,
                "change": change,
            })
        return results
    except Exception:
        return []


def fetch_hot_sectors() -> list[dict]:
    """获取热门板块排行（东方财富公开接口）"""
    url = (
        "https://push2.eastmoney.com/api/qt/clist/get"
        "?cb=jQuery&pn=1&pz=20&po=1&np=1"
        "&fields=f2,f3,f4,f12,f14"
        "&fid=f3&fs=m:90+t:2"
    )
    return _fetch_em_qlist(url)


# ─── 涨跌榜（行业板块区间涨幅）────────────────────────────────

def fetch_sector_rank() -> list[dict]:
    """申万一级行业区间涨幅排行"""
    url = (
        "https://push2.eastmoney.com/api/qt/clist/get"
        "?cb=jQuery&pn=1&pz=28&po=1&np=1"
        "&fields=f2,f3,f4,f12,f14"
        "&fid=f3&fs=m:90+t:1"
    )
    return _fetch_em_qlist(url)


# ─── 沪深全市场涨跌分布 ──────────────────────────────────────

def fetch_market_overview() -> dict:
    """获取沪深市场概况（涨跌家数估算）"""
    overview = {
        "up": 0, "down": 0, "flat": 0,
        "limit_up": 0, "limit_down": 0,
        "total": 0,
    }
    try:
        # 按股票代码排序（近似随机分布），取100只样本估算涨跌比
        url = (
            "https://push2.eastmoney.com/api/qt/clist/get"
            "?cb=jQuery&pn=1&pz=100&po=0&np=1"
            "&fields=f3&fid=f12"  # 按代码排序，近似随机
            "&fs=m:0+t:6,m:0+t:80"
            "&ut=bd1d9ddb04089700cf9c27f6f7426281"
        )
        data = _fetch_json(url)
        total = data.get("data", {}).get("total", 0)
        overview["total"] = total
        items = data.get("data", {}).get("diff", [])
        if not items:
            return overview

        sample_up = 0
        sample_down = 0
        sample_flat = 0
        for item in items:
            pct = item.get("f3")
            if pct is None:
                sample_flat += 1
            elif pct >= 990:
                sample_up += 1
            elif pct <= -990:
                sample_down += 1
            elif pct > 0:
                sample_up += 1
            elif pct < 0:
                sample_down += 1
            else:
                sample_flat += 1

        sample_total = sample_up + sample_down + sample_flat
        if sample_total > 0:
            ratio = total / sample_total
            overview["up"] = int(sample_up * ratio)
            overview["down"] = int(sample_down * ratio)
            overview["flat"] = int(sample_flat * ratio)
            limit_up_sample = sum(1 for i in items if i.get("f3", -1) >= 990)
            limit_down_sample = sum(1 for i in items if i.get("f3", 1) <= -990)
            overview["limit_up"] = int(limit_up_sample * ratio)
            overview["limit_down"] = int(limit_down_sample * ratio)

    except Exception:
        pass
    return overview


# ─── 龙虎榜（东方财富）───────────────────────────────────────

def fetch_lhb(tab: str = "all") -> list[dict]:
    """龙虎榜数据"""
    tab_map = {
        "all": "0",   # 全部
        "jg": "2",    # 机构
        "yyb": "4",   # 游资
    }
    tab_val = tab_map.get(tab, "0")
    url = (
        f"https://data.eastmoney.com/stock/data/lhb/"
        f"get_lhb_listdata.ashx?type={tab_val}&sty=all"
    )
    results = []
    try:
        data = _fetch_json(url)
        items = data.get("data", {}).get("data", [])
        for item in items[:15]:
            results.append({
                "code": item.get("SECURITY_CODE", ""),
                "name": item.get("SECURITY_NAME_ABBR", ""),
                "change_pct": item.get("CHANGE_PCT", 0),
                "amount": item.get("AMOUNT", 0),   # 万
                "reason": item.get("LHB_REASON", ""),
            })
    except Exception:
        pass
    return results


# ─── 市场资讯（沪深市场新闻）─────────────────────────────────

def fetch_market_news(limit: int = 10) -> list[dict]:
    """获取沪深市场最新动态"""
    results = []
    try:
        url = (
            "https://push2.eastmoney.com/api/qt/slist/get"
            "?spt=1&fltt=2&invt=2&cb=jQuery"
            "&fields=f12,f14,f2,f3,f4,f5,f6"
            f"&pn=1&pz={limit}&fid=f3&po=1"
            "&fs=m:90+t:3"
        )
        results = _fetch_em_qlist(url)
    except Exception:
        pass
    # Fallback: 热门板块
    if not results:
        try:
            url = (
                "https://push2.eastmoney.com/api/qt/clist/get"
                "?cb=jQuery&pn=1&pz=10&po=1&np=1"
                "&fields=f2,f3,f4,f12,f14&fid=f3&fs=m:90+t:2"
            )
            results = _fetch_em_qlist(url)[:limit]
        except Exception:
            pass
    return results


# ─── 单只股票实时行情 ────────────────────────────────────────

def fetch_stock_quote(code: str) -> dict | None:
    """获取单只股票实时行情（腾讯接口）"""
    url = f"https://qt.gtimg.cn/q={code}"
    raw = _fetch(url)
    try:
        for line in raw.strip().split("\n"):
            if not line.startswith("v_"):
                continue
            parts = line.split("~")
            if len(parts) < 40:
                continue
            return {
                "code": code,
                "name": parts[1],
                "price": float(parts[3]),
                "change": float(parts[31]),
                "change_pct": float(parts[32]),
                "open": float(parts[5]),
                "high": float(parts[33]),
                "low": float(parts[34]),
                "pre_close": float(parts[4]),
                "volume": float(parts[6]),
                "amount": float(parts[7]),
                "pe": parts[39],
                "amplitude": parts[43],
                "turnover_rate": parts[38],
                "total_mv": parts[44],  # 总市值
                "circulate_mv": parts[45],  # 流通市值
            }
    except (ValueError, IndexError):
        return None
    return None


# ─── 批量股票行情 ────────────────────────────────────────────

def fetch_batch_quote(codes: list[str]) -> list[dict]:
    """批量获取股票行情"""
    joined = ",".join(codes)
    url = f"https://qt.gtimg.cn/q={joined}"
    raw = _fetch(url)
    results = []
    for line in raw.strip().split("\n"):
        line = line.strip()
        if not line or not line.startswith("v_"):
            continue
        try:
            parts = line.split("~")
            if len(parts) < 40:
                continue
            results.append({
                "code": parts[0].split("=")[0].replace("v_", ""),
                "name": parts[1],
                "price": float(parts[3]),
                "change": float(parts[31]),
                "change_pct": float(parts[32]),
                "high": float(parts[33]),
                "low": float(parts[34]),
                "volume": float(parts[6]),
                "amount": float(parts[7]),
            })
        except (ValueError, IndexError):
            continue
    return results


# ─── N日均线选股（模拟/演示）─────────────────────────────────

def get_market_status() -> str:
    """判断市场是否在交易时段"""
    now = time.localtime()
    weekday = now.tm_wday
    hour = now.tm_hour
    minute = now.tm_min
    if weekday >= 5:
        return "休市（周末）"
    if (hour == 9 and minute >= 30) or (9 < hour < 11) or (hour == 11 and minute <= 30):
        return "交易中（上午）"
    if hour == 11 and minute > 30:
        return "午间休市"
    if (hour == 13) or (hour < 15) or (hour == 15 and minute == 0):
        return "交易中（下午）"
    if hour >= 15:
        return "已收盘"
    return "盘前"
