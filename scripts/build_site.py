"""Build the public, static review page. No external service or frontend build."""
import json
from pathlib import Path
from datetime import date
import pilot

ROOT = Path(__file__).resolve().parents[1]

def build():
    data = pilot.load_data()
    report_file = ROOT / 'output/source-check.json'
    report = json.loads(report_file.read_text()) if report_file.exists() else None
    today = date.today()
    places = []
    for p in data['places']:
        entry = dict(p)
        entry['displayable_at_build'] = pilot.eligible(p, today, report)
        entry['scores'] = pilot.scores(p)
        places.append(entry)
    payload = json.dumps({'built_on': today.isoformat(), 'places': places}, ensure_ascii=False).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    template = (ROOT / 'web/index.template.html').read_text()
    assert template.count('__DATA__') == 1
    (ROOT / 'docs/index.html').write_text(template.replace('__DATA__', payload))
    (ROOT / 'docs/.nojekyll').touch()
    print(f"Built docs/index.html: {len(places)} research records")

if __name__ == '__main__': build()
