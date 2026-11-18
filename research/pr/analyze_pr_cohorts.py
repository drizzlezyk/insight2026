# -*- coding: utf-8 -*-
"""30-day cumulative merge rate for PR cohorts before/after 2026-04-28.

Groups follow the prior report's taxonomy:
  core5 / official / insider / external / bot
Internal = core5 + official + insider.
"""
import json
import os
import re
import statistics as st
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone

BASE = os.path.dirname(os.path.abspath(__file__))
CUTOFF = datetime(2026, 4, 28, tzinfo=timezone.utc)
BEFORE_START = datetime(2026, 3, 29, tzinfo=timezone.utc)
AFTER_END = datetime(2026, 5, 28, tzinfo=timezone.utc)  # exclusive
CORE5 = {'steipete', 'vincentkoc', 'RomneyDa', 'obviyus', 'shakkernerd'}
DAYS = 30


def parse_ts(s):
    return datetime.fromisoformat(s.replace('Z', '+00:00')) if s else None


def is_bot(login):
    if not login:
        return False
    l = login.lower()
    return (l.endswith('[bot]') or l.endswith('-bot') or
            l in {'clawsweeper', 'openclaw-barnacle', 'roboclaw', 'openclaw-mantis',
                  'openclaw-macos-publisher', 'dependabot'})


def section_logins(html, start_marker, end_marker=None):
    i = html.find(start_marker)
    if i < 0:
        return set()
    j = html.find(end_marker, i) if end_marker else len(html)
    if j < 0:
        j = len(html)
    return set(re.findall(r'data-ga-id="github:([^"]+)"', html[i:j]))


def wilson(k, n, z=1.96):
    if not n:
        return (0.0, 0.0)
    p = k / n
    den = 1 + z * z / n
    mid = (p + z * z / (2 * n)) / den
    half = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / den
    return (mid - half, mid + half)


def two_prop_p(k1, n1, k2, n2):
    if not n1 or not n2:
        return 1.0
    p1, p2 = k1 / n1, k2 / n2
    p = (k1 + k2) / (n1 + n2)
    se = (p * (1 - p) * (1 / n1 + 1 / n2)) ** 0.5
    if se == 0:
        return 1.0
    z = abs(p1 - p2) / se
    # two-sided normal tail
    from statistics import NormalDist
    return 2 * (1 - NormalDist().cdf(z))


def main():
    rows = json.load(open(os.path.join(BASE, 'pr-cohorts-20260329-20260527.json'),
                          encoding='utf-8'))
    html = open(os.path.join(BASE, 'openclaw_people.html'),
                encoding='utf-8', errors='ignore').read()
    official = (section_logins(html, 'people_maintainers', '<div class="layer">') |
                section_logins(html, 'people_foundation', '<div class="layer">'))

    for r in rows:
        r['created'] = parse_ts(r['createdAt'])
        r['merged'] = parse_ts(r['mergedAt'])
        r['author_login'] = (r.get('author') or {}).get('login')

    # merger set across both cohorts: behavior-based write-access proxy
    merged_by = {r['mergedBy']['login'] for r in rows
                 if r.get('mergedBy') and r['mergedBy'].get('login')
                 and not is_bot(r['mergedBy']['login'])}

    def group(r):
        a = r['author_login']
        if is_bot(a):
            return 'bot'
        if a in CORE5:
            return 'core5'
        if a in official:
            return 'official'
        head = (r.get('headRepository') or {}).get('nameWithOwner')
        base = (r.get('baseRepository') or {}).get('nameWithOwner')
        same = head == base == 'openclaw/openclaw'
        assoc = r.get('authorAssociation') or ''
        if same or a in merged_by or assoc in {'OWNER', 'MEMBER', 'COLLABORATOR'}:
            return 'insider'
        return 'external'

    for r in rows:
        r['group'] = group(r)
        r['cohort'] = 'before' if r['created'] < CUTOFF else 'after'
        r['days'] = ((r['merged'] - r['created']).total_seconds() / 86400) if r['merged'] else None

    print('rows=%d  official=%d  merged_by=%d' % (len(rows), len(official), len(merged_by)))
    windows = {}
    for c, lo, hi in [('before', BEFORE_START, CUTOFF), ('after', CUTOFF, AFTER_END)]:
        sub = [r for r in rows if lo <= r['created'] < hi]
        windows[c] = sub
        print('%s %s..%s n=%d' % (c, lo.date(), (hi - timedelta(days=1)).date(), len(sub)))
    print('group totals:', Counter(r['group'] for r in rows).most_common())

    groups = ['all', 'external', 'internal', 'core5', 'official', 'insider', 'bot']

    def select(c, g):
        sub = windows[c]
        if g == 'all':
            return sub
        if g == 'internal':
            return [r for r in sub if r['group'] in ('core5', 'official', 'insider')]
        return [r for r in sub if r['group'] == g]

    print('\n=== 30-day cumulative merge rate ===')
    results = {}
    for g in groups:
        line = []
        for c in ('before', 'after'):
            sub = select(c, g)
            n = len(sub)
            k = sum(1 for r in sub if r['days'] is not None and r['days'] <= DAYS)
            lo, hi = wilson(k, n)
            results[(g, c)] = (n, k, k / n if n else 0.0, lo, hi)
            line.append('%s n=%d merged=%d rate=%.2f%% [%.2f,%.2f]' %
                        (c, n, k, 100 * k / n if n else 0, 100 * lo, 100 * hi))
        b = results[(g, 'before')]
        a = results[(g, 'after')]
        delta = 100 * (a[2] - b[2])
        rel = (a[2] / b[2] - 1) * 100 if b[2] else float('nan')
        p = two_prop_p(b[1], b[0], a[1], a[0])
        print('%-9s %s | %s | delta=%+.2fpp rel=%+.1f%% p=%.2g' %
              (g, line[0], line[1], delta, rel, p))

    print('\n=== cumulative curve (share merged within N days) ===')
    for g in ['external', 'internal', 'bot']:
        print('--', g)
        for c in ('before', 'after'):
            sub = select(c, g)
            n = len(sub)
            vals = []
            for d in (1, 3, 7, 14, 30):
                k = sum(1 for r in sub if r['days'] is not None and r['days'] <= d)
                vals.append('%dd=%.1f%%' % (d, 100 * k / n if n else 0))
            print('  %-6s n=%d  %s' % (c, n, '  '.join(vals)))

    print('\n=== final state (snapshot 2026-11) ===')
    for c in ('before', 'after'):
        for g in ['external', 'internal', 'bot']:
            sub = select(c, g)
            print(c, g, Counter(r['state'] for r in sub).most_common())
        print()

    print('=== median days among merged (<=30d) ===')
    for g in ['external', 'internal', 'bot']:
        for c in ('before', 'after'):
            ds = [r['days'] for r in select(c, g) if r['days'] is not None and r['days'] <= DAYS]
            if ds:
                print('%-9s %-6s n=%d median=%.2fd p25=%.2f p75=%.2f' %
                      (g, c, len(ds), st.median(ds),
                       st.quantiles(ds, n=4)[0], st.quantiles(ds, n=4)[2]))


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
