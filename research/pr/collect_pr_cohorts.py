# -*- coding: utf-8 -*-
"""Collect every PR created in the 30d before/after the ClawSweeper adoption cut.

Intervention date: 2026-04-28 (first dispatcher adoption, same as the
dashboard's issue cohort).
  before: 2026-03-29 .. 2026-04-27
  after : 2026-04-28 .. 2026-05-27

Search returns all states (merged / closed-unmerged / still open), which is
what a merge-rate denominator needs.
"""
import datetime as dt
import json
import os
import subprocess
import sys
import time

START = dt.date(2026, 3, 29)
END = dt.date(2026, 5, 27)
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   'pr-cohorts-20260329-20260527.json')

FIELDS = '''
  number
  createdAt
  mergedAt
  closedAt
  state
  isDraft
  author { login }
  authorAssociation
  mergedBy { login }
  headRepository { nameWithOwner }
  baseRepository { nameWithOwner }
'''

QUERY = ('query($q:String!,$after:String){ search(query:$q,type:ISSUE,first:100,after:$after){ '
         'issueCount pageInfo{hasNextPage endCursor} nodes{ ... on PullRequest { %s } } } }' % FIELDS)


def graphql(q, after=None):
    args = ['gh', 'api', 'graphql', '-f', 'query=' + QUERY, '-f', 'q=' + q]
    if after:
        args += ['-f', 'after=' + after]
    for attempt in range(5):
        r = subprocess.run(args, capture_output=True, text=True, encoding='utf-8')
        if r.returncode == 0:
            data = json.loads(r.stdout)
            if 'errors' not in data:
                return data['data']['search']
        time.sleep(2 * (attempt + 1))
    raise RuntimeError((r.stderr or r.stdout)[:800])


def collect_day(day):
    q = 'repo:openclaw/openclaw is:pr created:%s' % day.isoformat()
    out, cursor, count = [], None, None
    while True:
        s = graphql(q, cursor)
        count = s['issueCount']
        out.extend(s['nodes'])
        if not s['pageInfo']['hasNextPage']:
            break
        cursor = s['pageInfo']['endCursor']
        time.sleep(0.05)
    return count, out


def main():
    all_rows, expected = [], 0
    d = START
    while d <= END:
        count, rows = collect_day(d)
        expected += count
        all_rows.extend(rows)
        print('%s expected=%d got=%d total=%d' % (d, count, len(rows), len(all_rows)), flush=True)
        d += dt.timedelta(days=1)
        time.sleep(0.05)

    by_num = {}
    for r in all_rows:
        by_num[r['number']] = r
    rows = list(by_num.values())
    print('expected %d, collected %d, deduped %d' % (expected, len(all_rows), len(rows)))
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(rows, f, ensure_ascii=False)
    print('saved', OUT)

    if len(rows) < expected * 0.98:
        print('WARNING: collected less than 98% of issueCount', file=sys.stderr)
        sys.exit(2)


if __name__ == '__main__':
    main()
