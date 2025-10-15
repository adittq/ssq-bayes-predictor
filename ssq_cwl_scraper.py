#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中国福彩网（cwl.gov.cn）双色球往期数据抓取脚本

来源示例：
  - 列表页： https://www.cwl.gov.cn/ygkj/wqkjgg/ssq/
  - 单期详情：如 https://www.cwl.gov.cn/c/2025/10/14/631584.shtml

功能：
  - 抓取列表页的“期号、开奖日期、开奖号码、销售额”等字段
  - 将开奖号码拆分为红球1-6、蓝球
  - 输出为与现有数据一致的CSV列格式

使用：
  python ssq_cwl_scraper.py --out ssq_cwl_data.csv

注意：
  - 该页面可能采用切换“近30/50/100期/全部”的前端逻辑；当前实现抓取默认列表页中已呈现的条目。
  - 如需扩展为“全部”或分页抓取，可根据页面实际结构追加参数或解析更多区域。
"""

import re
import sys
import time
import csv
import logging
import argparse
from typing import List, Dict, Optional

import requests
from bs4 import BeautifulSoup


LISTING_URL = "https://www.cwl.gov.cn/ygkj/wqkjgg/ssq/"
API_URL = "https://www.cwl.gov.cn/cwl_admin/front/cwlkj/search/kjxx/findDrawNotice"


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Connection': 'keep-alive',
}


def clean_date(date_text: str) -> str:
    """清理日期文本，保留 YYYY-MM-DD 格式。
    例如："2025-10-14(二)" -> "2025-10-14"
    """
    if not date_text:
        return ""
    date_text = date_text.strip()
    # 去掉括号后的星期标记
    date_text = re.sub(r"\(.*?\)", "", date_text)
    return date_text.strip()


def parse_numbers(numbers_text: str) -> Dict[str, str]:
    """将开奖号码拆分为红球1-6与蓝球。
    输入示例："1 10 11 16 26 24 3" -> 红6+蓝1
    """
    nums = re.findall(r"\d+", numbers_text or "")
    # 某些页面红球可能为两位数前导零，统一按数字文本处理
    result = {
        '红球1': nums[0] if len(nums) > 0 else '',
        '红球2': nums[1] if len(nums) > 1 else '',
        '红球3': nums[2] if len(nums) > 2 else '',
        '红球4': nums[3] if len(nums) > 3 else '',
        '红球5': nums[4] if len(nums) > 4 else '',
        '红球6': nums[5] if len(nums) > 5 else '',
        '蓝球':  nums[6] if len(nums) > 6 else '',
        '原始号码': numbers_text.strip() if numbers_text else ''
    }
    return result


def fetch_listing_html(url: str, session: Optional[requests.Session] = None) -> str:
    sess = session or requests.Session()
    sess.headers.update(HEADERS)
    logger.info(f"请求列表页: {url}")
    resp = sess.get(url, timeout=10)
    resp.raise_for_status()
    resp.encoding = 'utf-8'
    return resp.text


def fetch_api_page(session: requests.Session, page_no: int = 1, page_size: int = 30) -> List[Dict]:
    """调用官网JSON接口获取单页数据。"""
    params = {
        'name': 'ssq',
        'issueCount': '',
        'issueStart': '',
        'issueEnd': '',
        'dayStart': '',
        'dayEnd': '',
        'pageNo': page_no,
        'pageSize': page_size,
        'week': '',
        'systemType': 'PC',
    }
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Referer': LISTING_URL,
        'X-Requested-With': 'XMLHttpRequest',
        # 复用默认UA等
    }
    logger.info(f"请求JSON接口: pageNo={page_no}, pageSize={page_size}")
    resp = session.get(API_URL, params=params, headers=headers, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    result = data.get('result') or []
    logger.info(f"接口返回 {len(result)} 条")
    return result


def parse_api_result(items: List[Dict]) -> List[Dict[str, str]]:
    records: List[Dict[str, str]] = []
    for item in items:
        period = str(item.get('code', '')).strip()
        # 接口字段为 'date'，形如 "2025-10-14(二)"
        date = str(item.get('date', '')).strip()
        red = str(item.get('red', '')).strip()
        blue = str(item.get('blue', '')).strip()
        sale = str(item.get('sales', '')).strip()

        # red 以逗号分隔，如 "01,10,11,16,26,24"
        reds = [x.strip() for x in red.split(',') if x.strip()]
        nums = {
            '红球1': reds[0] if len(reds) > 0 else '',
            '红球2': reds[1] if len(reds) > 1 else '',
            '红球3': reds[2] if len(reds) > 2 else '',
            '红球4': reds[3] if len(reds) > 3 else '',
            '红球5': reds[4] if len(reds) > 4 else '',
            '红球6': reds[5] if len(reds) > 5 else '',
        }

        record = {
            '开奖日期': clean_date(date),
            '期号': period,
            '红球1': nums['红球1'],
            '红球2': nums['红球2'],
            '红球3': nums['红球3'],
            '红球4': nums['红球4'],
            '红球5': nums['红球5'],
            '红球6': nums['红球6'],
            '蓝球': blue,
            '销售额': sale,
            '原始号码': (','.join(reds) + (('+' + blue) if blue else '')).strip(),
        }
        records.append(record)
    return records


def parse_listing(html: str) -> List[Dict[str, str]]:
    """从列表页HTML解析数据行。
    页面包含表格：期号、开奖日期、开奖号码、销售额... 解析为标准列。
    """
    soup = BeautifulSoup(html, 'lxml')

    # 尝试定位包含“期号”等表头的表格
    tables = soup.find_all('table')
    results: List[Dict[str, str]] = []

    def row_to_record(tds: List) -> Optional[Dict[str, str]]:
        texts = [td.get_text(strip=True) for td in tds]
        # 兼容不同列数；至少需要：期号、开奖日期、开奖号码、销售额
        if len(texts) < 4:
            return None

        # 基本字段提取（根据常见顺序：期号、开奖日期、开奖号码、...、销售额）
        period = texts[0]
        date_raw = texts[1]
        numbers_text = texts[2]

        # 销售额通常在后续列，尝试匹配含“,”的金额文本或全数字
        sale = ''
        for t in texts[3:]:
            if re.match(r"^[\d,]+$", t):
                sale = t
                break

        date = clean_date(date_raw)
        nums = parse_numbers(numbers_text)

        record = {
            '开奖日期': date,
            '期号': period,
            '红球1': nums['红球1'],
            '红球2': nums['红球2'],
            '红球3': nums['红球3'],
            '红球4': nums['红球4'],
            '红球5': nums['红球5'],
            '红球6': nums['红球6'],
            '蓝球': nums['蓝球'],
            '销售额': sale,
            '原始号码': nums['原始号码'],
        }
        return record

    for table in tables:
        # 查找所有行，跳过表头
        rows = table.find_all('tr')
        for tr in rows:
            tds = tr.find_all('td')
            if not tds:
                continue
            rec = row_to_record(tds)
            if rec and rec['开奖日期'] and rec['期号']:
                results.append(rec)

    logger.info(f"解析出 {len(results)} 条记录")
    return results


def save_csv(records: List[Dict[str, str]], out_path: str) -> None:
    if not records:
        logger.warning("没有数据可写入CSV")
        return

    # 统一列顺序与现有数据文件一致
    fieldnames = [
        '开奖日期', '期号',
        '红球1', '红球2', '红球3', '红球4', '红球5', '红球6',
        '蓝球', '销售额', '原始号码'
    ]

    with open(out_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in records:
            writer.writerow(r)

    logger.info(f"已写入 {len(records)} 条到 {out_path}")


def main():
    parser = argparse.ArgumentParser(description='从中国福彩网抓取双色球往期数据')
    parser.add_argument('--url', default=LISTING_URL, help='列表页URL')
    parser.add_argument('--out', default='ssq_cwl_data.csv', help='输出CSV文件路径')
    parser.add_argument('--delay', type=float, default=0.0, help='请求间隔秒数（如需抓取多页时可用）')
    args = parser.parse_args()

    session = requests.Session()
    session.headers.update(HEADERS)

    try:
        # 先请求列表页以建立站点Cookie，再走JSON接口分页抓取
        _ = fetch_listing_html(args.url, session)

        all_items: List[Dict] = []
        page = 1
        page_size = 30
        while True:
            items = fetch_api_page(session, page_no=page, page_size=page_size)
            if not items:
                break
            all_items.extend(items)
            # 官方接口按时间倒序返回；翻页直至为空
            page += 1
            # 避免过快请求
            if args.delay:
                time.sleep(args.delay)

        records = parse_api_result(all_items)
        # 简单去重：按期号去重
        uniq = {}
        for r in records:
            uniq[r['期号']] = r
        final_records = list(uniq.values())
        # 按日期排序（如日期格式清晰）
        try:
            final_records.sort(key=lambda x: x['开奖日期'])
        except Exception:
            pass
        save_csv(final_records, args.out)
        logger.info('✅ 抓取完成')
    except KeyboardInterrupt:
        logger.info('用户中断')
    except Exception as e:
        logger.error(f'抓取失败: {e}')
        sys.exit(1)


if __name__ == '__main__':
    main()