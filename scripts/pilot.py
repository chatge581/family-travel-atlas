"""Small, dependency-free Osaka pilot. Run from any directory."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from hashlib import sha256
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]

class PageText(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts = []; self.skip = 0
    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style', 'nav', 'footer'): self.skip += 1
    def handle_endtag(self, tag):
        if tag in ('script', 'style', 'nav', 'footer'): self.skip = max(0, self.skip - 1)
    def handle_data(self, data):
        if not self.skip and data.strip(): self.parts.append(data.strip())

def load_data():
    data = json.loads((ROOT / 'data/osaka-pilot.json').read_text())
    ids = [p['id'] for p in data['places']]
    assert len(ids) == len(set(ids)), 'Duplicate place IDs'
    for p in data['places']:
        assert p['sources'] and p['status'] in ('candidate', 'blocked')
        date.fromisoformat(p['checked_on'])
        assert p['family_admission_jpy'] is None or p['family_admission_jpy'] >= 0
        for e in p['events']:
            assert date.fromisoformat(e['start']) <= date.fromisoformat(e['end'])
    return data

def stars(n):
    return '未评分' if n is None else '★' * n + '☆' * (5-n)

def scores(p):
    c, w = p['family_admission_jpy'], p['station_walk_minutes']
    return [None if c is None else 5 if c == 0 else 4 if c <= 1000 else 3 if c <= 2500 else 2 if c <= 4000 else 1,
            None if w is None else 5 if w <= 5 else 4 if w <= 10 else 3 if w <= 20 else 2 if w <= 30 else 1,
            5 if p['weather'] == 'indoor' else None]

def eligible(p, today, report):
    if p['status'] == 'blocked': return False
    age = (today - date.fromisoformat(p['checked_on'])).days
    if age < 0 or age > 31: return False
    # A successful fetch never refreshes factual verification dates.
    if report:
        by_url = {r['url']: r for r in report['sources']}
        return all(u in by_url and by_url[u]['status'] in ('baseline', 'unchanged') for u in p['sources'])
    return True

def active_events(p, today):
    # Future events remain in the upcoming section; expired items leave it.
    return [e for e in p['events'] if today <= date.fromisoformat(e['end'])]

def render(data, today, report=None):
    out = ROOT / 'output'; out.mkdir(exist_ok=True)
    md = ['# 大阪及周边 · 亲子地点小样本', '', f'样稿日期：{today}。两位成人＋一名学龄前儿童；日本当地开放时间。', '',
          '星级按门票金额、车站步行分钟和室内条件计算，不是游客评分，无综合排名。图片尚未取得转载依据，本稿不使用网络照片。', '']
    cards = []; usable = 0
    for p in data['places']:
        if not eligible(p, today, report):
            md += [f"## {p['name']}｜暂不展示", '', '资料读取失败、发生变化或已超过31天复核期限；不沿用旧数据作当前推荐。', '']
            continue
        usable += 1
        score = scores(p)
        money = '未核实' if p['family_admission_jpy'] is None else f"{p['family_admission_jpy']:,}日元"
        transit = '见官方交通说明，不换算分钟' if p['station_walk_minutes'] is None else f"车站步行约{p['station_walk_minutes']}分钟"
        rows = [('家庭门票', money), ('门票经济性', stars(score[0])), ('车站步行便利度', stars(score[1]) + ' · ' + transit),
                ('天气适应性', stars(score[2]) + (' · 核心参观在室内' if score[2] else ' · 户外或遮蔽条件未完整核实')),
                ('开放时间', p['hours']), ('地址', p['address']), ('游览时长', p['duration'] or '暂无可靠参考时长')]
        map_url = 'https://www.google.com/maps/search/?' + urlencode({'api': 1, 'query': p['local_name'] + ' ' + p['area']})
        md += [f"## {p['name']}", '', p['local_name'] + ' · ' + p['area'], '', p['summary'], '', '| 项目 | 信息 |', '| --- | --- |']
        md += [f'| {k} | {v} |' for k, v in rows]
        md += ['', '**体验与限制**', ''] + ['- '+x for x in p['experiences'] + p['limits']]
        events = active_events(p, today)
        if events:
            md += ['', '**近期活动**', ''] + [f"- {e['title']}｜{e['start']}—{e['end']}：{e['details']} [公告]({e['source']})" for e in events]
        md += ['', f'[Google地图搜索]({map_url})', '', '资料核查：' + p['checked_on'] + '；出发前查看官方临时通知。', '']
        md += [f"[来源{i+1}]({u})" for i,u in enumerate(p['sources'])] + ['']
        eh = ''.join(f"<p><b>{escape(e['title'])}</b> · {e['start']}—{e['end']}<br>{escape(e['details'])}</p>" for e in events)
        cards.append(f"<article><div class='tag'>{escape(p['area'])}</div><h2>{escape(p['name'])}</h2><p class='local'>{escape(p['local_name'])}</p><p>{escape(p['summary'])}</p><table>" + ''.join(f'<tr><th>{escape(k)}</th><td>{escape(v)}</td></tr>' for k,v in rows) + '</table><ul>' + ''.join(f'<li>{escape(x)}</li>' for x in p['experiences']+p['limits']) + '</ul>' + (f'<h3>近期活动</h3>{eh}' if eh else '') + f"<a href='{escape(map_url, quote=True)}'>在Google地图中搜索</a><footer>资料核查：{p['checked_on']} · " + ' / '.join(f"<a href='{escape(u, quote=True)}'>来源{i+1}</a>" for i,u in enumerate(p['sources'])) + '</footer></article>')
    (out / 'osaka-pilot.md').write_text('\n'.join(md))
    css = 'body{font:16px/1.7 system-ui;background:#f4f3ef;color:#24322e;margin:auto;max-width:1000px;padding:24px}article{background:white;border:1px solid #ddd;border-radius:16px;padding:28px;margin:24px 0}h2{margin:6px 0}table{width:100%;border-collapse:collapse}th,td{text-align:left;border-bottom:1px solid #eee;padding:10px}th{width:30%}.tag,a{color:#396851}.local,footer{color:#66716b;font-size:13px}footer{margin-top:20px}@media(max-width:600px){body{padding:12px}article{padding:18px}th{width:35%}}'
    (out / 'osaka-pilot.html').write_text(f'<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>大阪亲子地点小样本</title><style>{css}</style><h1>大阪及周边 · 亲子地点小样本</h1><p>{today} · {usable}张候选卡 / 10个研究对象。未展示的对象见文字版。</p><p>门票按两大一名学龄前儿童计算，交通、餐饮与体验另计。星级为规则分类，不是游客评分。本稿未使用网络照片。</p>' + ''.join(cards) + '</html>')
    return usable

def fetch(url):
    try:
        with urlopen(Request(url, headers={'User-Agent': 'FamilyTravelAtlas-research/0.1'}), timeout=20) as r:
            raw = r.read(3_000_001)
            if len(raw) > 3_000_000: raise ValueError('response_too_large')
            text = raw.decode('utf-8', 'replace'); p = PageText(); p.feed(text)
            body = re.sub(r'\s+', ' ', ' '.join(p.parts)).strip()
            if len(body) < 100 or any(t in body.lower() for t in ('verify you are human', 'captcha', 'access denied')):
                raise ValueError('empty_or_challenge_page')
            return {'url':url, 'hash':sha256(body.encode()).hexdigest(), 'text':body}
    except Exception as e:
        return {'url':url, 'error':str(e)}

def check(data):
    cache = ROOT / '.travel-cache'; cache.mkdir(exist_ok=True)
    baseline_file = cache / 'baseline.json'
    baseline = json.loads(baseline_file.read_text()) if baseline_file.exists() else {}
    urls = sorted({u for p in data['places'] for u in p['sources']})
    records = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        for r in pool.map(fetch, urls):
            if 'error' in r: r['status'] = 'error'
            elif r['url'] not in baseline:
                r['status'] = 'baseline'; baseline[r['url']] = r['hash']
            else: r['status'] = 'unchanged' if baseline[r['url']] == r['hash'] else 'changed'
            # Keep source extracts local; reports contain no reproduced source pages.
            if 'text' in r:
                (cache / (sha256(r['url'].encode()).hexdigest()+'.txt')).write_text(r.pop('text'))
            records.append(r)
    baseline_file.write_text(json.dumps(baseline, indent=2))
    return {'checked_at': __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(), 'sources':records,
            'note':'Page changes are signals, not automatically verified new facts; changed or failed sources suppress their cards. A hash match does not prove all notices were discovered.'}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--as-of', default=date.today().isoformat()); ap.add_argument('--check', action='store_true'); args=ap.parse_args()
    data=load_data(); report=None
    if args.check:
        report=check(data); (ROOT/'output').mkdir(exist_ok=True)
        (ROOT/'output/source-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    usable=render(data,date.fromisoformat(args.as_of),report)
    print(json.dumps({'places':len(data['places']),'displayed':usable,'as_of':args.as_of,'source_statuses': {k:sum(r['status']==k for r in report['sources']) for k in ('baseline','unchanged','changed','error')} if report else 'not_checked_this_run'},ensure_ascii=False))
if __name__ == '__main__': main()
