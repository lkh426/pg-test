import argparse
import json
import os
import re
import time
from typing import Dict, List, Optional, Tuple

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
try:
    import undetected_chromedriver as uc  # type: ignore
    UC_AVAILABLE = True
except Exception:
    UC_AVAILABLE = False
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fetch_xlink_files import get_xlink_list



DEFAULT_FEISHU_WEBHOOK = (
    "https://open.feishu.cn/open-apis/bot/v2/hook/a84d7b74-3c2f-4548-bd6b-b7557d436bb2"
)


def extract_tweet_id(tweet_url: str) -> Optional[str]:
    """Extract tweet ID from an X/Twitter status URL.

    Supports URLs like:
    - https://x.com/<user>/status/<id>
    - https://twitter.com/<user>/status/<id>
    """
    pattern = r"https?://(?:x\.com|twitter\.com)/[^/]+/status/(\d+)"
    match = re.search(pattern, tweet_url)
    return match.group(1) if match else None

def compose_feishu_text(results: List[Dict[str, Optional[int]]]) -> str:
    lines: List[str] = []
    lines.append("【X 推文指标】")
    for item in results:
        like_count = item.get("like_count")
        reply_count = item.get("reply_count")
        retweet_count = item.get("retweet_count")
        view_count = item.get("view_count")
        url = item.get("url")
        if like_count is None and reply_count is None and retweet_count is None and view_count is None:
            lines.append(f"- {url}\n  无法获取指标")
        else:
            lines.append(
                f"- {url}\n  点赞: {like_count}  评论: {reply_count}  转发: {retweet_count}  播放: {view_count}"
            )
    return "\n".join(lines)

#飞书发送内容
def send_to_feishu(webhook: str, text: str) -> Tuple[bool, str]:
    payload = {"msg_type": "text", "content": {"text": text}}
    headers = {"Content-Type": "application/json; charset=utf-8"}
    try:
        resp = requests.post(webhook, headers=headers, data=json.dumps(payload), timeout=15)
        if resp.status_code == 200:
            return True, "OK"
        return False, f"HTTP {resp.status_code}: {resp.text}"
    except Exception as e:
        return False, str(e)


def main():
    parser = argparse.ArgumentParser(description="Fetch X/Twitter tweet metrics and send to Feishu.")
    parser.add_argument(
        "urls",
        nargs="*",
        help="Tweet URLs to fetch. If empty, will use built-in defaults.",
    )
    parser.add_argument(
        "--webhook",
        default=DEFAULT_FEISHU_WEBHOOK,
        help="Feishu bot webhook URL",
    )
    parser.add_argument(
        "--mode",
        choices=["api", "selenium", "auto"],
        default="auto",
        help="Choose fetch mode: api (Twitter API), selenium (real page), auto (try API then fallback)",
    )
    parser.add_argument(
        "--chrome-debug",
        default="127.0.0.1:9222",
        help="Chrome remote debugging address host:port for selenium mode",
    )
    parser.add_argument(
        "--feishu-doc-id",
        help="Feishu doc/docx ID to read URLs from",
    )
    # 移除飞书相关参数，改为仅使用默认/命令行链接
    args = parser.parse_args()

    #通过远程地址获取链接
    default_urls = get_xlink_list('http://10.61.171.61/')
    urls = args.urls if args.urls else default_urls

    def parse_compact_number(text: str) -> int:
        if text is None:
            return 0
        s = text.strip().upper()
        units = {
            'K': 1_000,
            'M': 1_000_000,
            'B': 1_000_000_000,
            '万'.upper(): 10_000,
            '亿'.upper(): 100_000_000,
        }
        m = re.match(r"([0-9.,]+)\s*([A-Z万亿]?)", s)
        if not m:
            digits = re.sub(r"[^0-9]", "", s)
            return int(digits) if digits else 0
        num_part, unit = m.groups()
        num_part = num_part.replace(',', '')
        try:
            base = float(num_part)
        except ValueError:
            return 0
        mult = units.get(unit, 1)
        return int(base * mult)

    def connect_existing_chrome(debug_addr: str):
        try:
            minimal_options = webdriver.ChromeOptions()
            minimal_options.add_argument("--no-sandbox")
            minimal_options.add_argument("--disable-dev-shm-usage")
            minimal_options.page_load_strategy = 'eager'
            driver = webdriver.Chrome(options=minimal_options)
            print("[Selenium] 已用最小配置启动新的 Chrome 实例")
            return driver
        except Exception as e2:
            print(f"[Selenium] 最小配置仍启动失败: {e2}")
            raise

    def find_article_for_tweet(driver, tweet_id: Optional[str]):
        if not tweet_id:
            return None
        try:
            # 寻找包含该 tweet 链接的 article 容器
            articles = driver.find_elements(By.XPATH, f"//article[.//a[contains(@href,'/status/{tweet_id}')]]")
            if articles:
                return articles[0]
        except Exception:
            pass
        return None

    def fetch_metrics_via_selenium(url_list: List[str], debug_addr: str) -> List[Dict[str, Optional[int]]]:
        results: List[Dict[str, Optional[int]]] = []
        batch_size = 20

        for start in range(0, len(url_list), batch_size):
            batch = url_list[start:start + batch_size]
            driver = connect_existing_chrome(debug_addr)
            try:
                for u in batch:
                    print(f"[Selenium] 打开: {u}")
                    # 节流：随机退避，避免限流
                    driver.get(u)
                    try:
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, "//article"))
                        )
                    except Exception:
                        time.sleep(8)
                    # 将解析范围限定到该推文对应的 article 容器
                    tid = extract_tweet_id(u)
                    article = find_article_for_tweet(driver, tid)
                    if article:
                        try:
                            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", article)
                            time.sleep(1.0)
                        except Exception:
                            pass
                    scope = article if article else driver

                    like = reply = retweet = views = None
                    try:
                        like_el = scope.find_element(By.XPATH, ".//div[@aria-label and (contains(@aria-label,'喜欢') or contains(@aria-label,'Like'))]")
                        label = like_el.get_attribute('aria-label') or ""
                        m = re.search(r"([0-9][0-9,\.]*\s*(?:万|亿)?)\s*(?:次)?\s*(?:Like|喜欢)", label, flags=re.IGNORECASE)
                        if not m:
                            m = re.search(r"(?:Like|喜欢)\D*([0-9][0-9,\.]*\s*(?:万|亿)?)", label, flags=re.IGNORECASE)
                        if m:
                            like = parse_compact_number(m.group(1))
                        else:
                            like = None
                    except Exception:
                        pass
                    try:
                        reply_el = scope.find_element(By.XPATH, ".//div[@aria-label and (contains(@aria-label,'回复') or contains(@aria-label,'Reply'))]")
                        rlabel = reply_el.get_attribute('aria-label') or ""
                        m = re.search(r"([0-9][0-9,\.]*\s*(?:万|亿)?)\s*(?:次)?\s*(?:Reply|回复)", rlabel, flags=re.IGNORECASE)
                        if not m:
                            m = re.search(r"(?:Reply|回复)\D*([0-9][0-9,\.]*\s*(?:万|亿)?)", rlabel, flags=re.IGNORECASE)
                        if m:
                            reply = parse_compact_number(m.group(1))
                        else:
                            reply = None
                    except Exception:
                        pass
                    try:
                        rt_el = scope.find_element(
                            By.XPATH,
                            ".//*[@aria-label and (contains(@aria-label,'转推') or contains(@aria-label,'转发') or contains(@aria-label,'转帖') or contains(@aria-label,'转贴') or contains(@aria-label,'Repost') or contains(@aria-label,'Retweet'))]"
                        )
                        rtlabel = rt_el.get_attribute('aria-label') or ""
                        m = re.search(r"([0-9][0-9,\.]*\s*(?:万|亿)?)\s*(?:次)?\s*(?:Repost|Retweet|转推|转发|转帖|转贴)", rtlabel, flags=re.IGNORECASE)
                        if not m:
                            m = re.search(r"(?:Repost|Retweet|转推|转发|转帖|转贴)\D*([0-9][0-9,\.]*\s*(?:万|亿)?)", rtlabel, flags=re.IGNORECASE)
                        if m:
                            retweet = parse_compact_number(m.group(1))
                        else:
                            retweet = None
                    except Exception:
                        pass
                    try:
                        views_el = scope.find_element(By.XPATH, ".//div[@aria-label and (contains(@aria-label,'次观看') or contains(@aria-label,'Views'))]")
                        vilabel = views_el.get_attribute('aria-label') or ""

                        m = re.search(r"([0-9][0-9,\.]*\s*(?:万|亿)?)\s*(?:次)?\s*(?:Views|观看|播放|浏览|查看)", vilabel, flags=re.IGNORECASE)
                        if not m and article is not None:
                            atxt = article.text or ""
                            m = re.search(r"([0-9][0-9,\.]*\s*(?:K|M|B|万|亿)?)\D{0,20}(Views|次浏览|浏览量|浏览|次查看|查看|观看|次观看|播放|次播放)", atxt, flags=re.IGNORECASE|re.DOTALL)
                        if m:
                            views = parse_compact_number(m.group(1))
                        else:
                            views = None
                    except Exception:
                        pass
                    print(f"[Selenium] 解析完成: like={like}, reply={reply}, retweet={retweet}, views={views}")
                    results.append({
                        "tweet_id": extract_tweet_id(u),
                        "like_count": like if like is not None else 0,
                        "reply_count": reply if reply is not None else 0,
                        "retweet_count": retweet if retweet is not None else 0,
                        "view_count": views if views is not None else 0,
                        "url": u,
                    })
            finally:
                try:
                    driver.quit()
                except Exception:
                    pass

        return results
    try:
        print("[Selenium] 使用默认/传入链接...")
        results = fetch_metrics_via_selenium(urls, args.chrome_debug)
    except Exception as e:
        print(f"执行出错: {e}")
        results = []


    text = compose_feishu_text(results)
    print(text)
    # ok, msg = send_to_feishu(args.webhook, text)
    # if ok:
    #     print("已发送到飞书")
    # else:
    #     print(f"发送飞书失败: {msg}")


if __name__ == "__main__":
    main()


