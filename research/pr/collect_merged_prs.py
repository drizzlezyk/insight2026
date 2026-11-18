# -*- coding: utf-8 -*-
import subprocess, json, datetime, time, sys, os

START = datetime.date(2026, 9, 13)
END = datetime.date(2026, 11, 13)

FIELDS = '''
  number
  author { login }
  authorAssociation
  mergedAt
  headRepository { nameWithOwner }
  baseRepository { nameWithOwner }
  mergedBy { login }
'''

def graphql(query):
    r = subprocess.run(['gh', 'api', 'graphql', '-f', f'query={query}'],
                       capture_output=True, text=True, encoding='utf-8')
    if r.returncode != 0:
        raise RuntimeError(r.stderr[:500] or r.stdout[:500])
    data = json.loads(r.stdout)
    if 'errors' in data:
        raise RuntimeError(str(data['errors'])[:500])
    return data['data']['search']

def collect_day(day):
    q = f'repo:openclaw/openclaw is:pr merged:{day.isoformat()}'
    out = []
    cursor = None
    while True:
        after = f', after: "{cursor}"' if cursor else ''
        query = ('query { search(query: %s, type: ISSUE, first: 100%s) { '
                 'issueCount pageInfo { hasNextPage endCursor } nodes { ... on PullRequest { %s } } } }'
                 % (json.dumps(q), after, FIELDS))
        s = graphql(query)
        out.extend(s['nodes'])
        if not s['pageInfo']['hasNextPage']:
            break
        cursor = s['pageInfo']['endCursor']
        time.sleep(0.05)
    return out

all_rows = []
d = START
while d <= END:
    rows = collect_day(d)
    all_rows.extend(rows)
    print(d.isoformat(), len(rows), 'total', len(all_rows), flush=True)
    d += datetime.timedelta(days=1)
    time.sleep(0.05)

path = os.path.join(os.path.dirname(__file__), 'merged-prs-20260913-20261113.json')
with open(path, 'w', encoding='utf-8') as f:
    json.dump(all_rows, f, ensure_ascii=False)
print('saved', path, len(all_rows))
