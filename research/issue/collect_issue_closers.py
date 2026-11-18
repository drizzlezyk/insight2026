# -*- coding: utf-8 -*-
"""Collect closer identity for issues created 2026-09-11..2026-11-11.

The funnel on slide 1 uses this window (11,468 issues). GitHub search does not
support closed-by, so pull CLOSED_EVENT actors from the timeline.
"""
import datetime as dt
import json
import os
import subprocess
import sys
import time

START = dt.date(2026, 9, 11)
END = dt.date(2026, 11, 11)
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   'issue-closers-20260911-20261111.json')

QUERY = '''query($q:String!,$after:String){
  search(query:$q,type:ISSUE,first:100,after:$after){
    issueCount
    pageInfo{hasNextPage endCursor}
    nodes{ ... on Issue {
      number createdAt closedAt state stateReason
      author{login}
      labels(first:50){nodes{name}}
      timelineItems(itemTypes:[CLOSED_EVENT],first:5){
        nodes{ ... on ClosedEvent { createdAt actor{login} } }
      }
    } }
  }
  rateLimit{cost remaining}
}'''


def fetch(q, cursor=None):
    args = ['gh', 'api', 'graphql', '-f', 'query=' + QUERY, '-f', 'q=' + q]
    if cursor:
        args += ['-f', 'after=' + cursor]
    for attempt in range(5):
        r = subprocess.run(args, capture_output=True, text=True, encoding='utf-8')
        if r.returncode == 0:
            data = json.loads(r.stdout)
            if 'errors' not in data:
                return data
        time.sleep(2 * (attempt + 1))
    raise RuntimeError((r.stderr or r.stdout)[:800])


def main():
    rows, expected = [], 0
    d = START
    while d <= END:
        q = 'repo:openclaw/openclaw is:issue created:%s' % d.isoformat()
        cursor, day_rows, day_count = None, [], 0
        while True:
            data = fetch(q, cursor)
            s = data['data']['search']
            day_count = s['issueCount']
            day_rows.extend(s['nodes'])
            if not s['pageInfo']['hasNextPage']:
                break
            cursor = s['pageInfo']['endCursor']
            time.sleep(0.05)
        expected += day_count
        rows.extend(day_rows)
        print('%s expected=%d got=%d total=%d remaining=%s' %
              (d, day_count, len(day_rows), len(rows),
               data['data']['rateLimit']['remaining']), flush=True)
        d += dt.timedelta(days=1)
        time.sleep(0.05)

    by_num = {r['number']: r for r in rows}
    rows = list(by_num.values())
    print('collected', len(rows), 'expected', expected)
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(rows, f, ensure_ascii=False)
    print('saved', OUT)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
