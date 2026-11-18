# -*- coding: utf-8 -*-
import json, re, os, collections

BASE = os.path.dirname(os.path.abspath(__file__))
rows = json.load(open(os.path.join(BASE, 'merged-prs-20260913-20261113.json'), encoding='utf-8'))
by_num = {r['number']: r for r in rows}
rows = list(by_num.values())

# official list from the OpenClaw people page (Foundation + Core Maintainers)
html = open(os.path.join(BASE, 'openclaw_people.html'), encoding='utf-8', errors='ignore').read()
def section_logins(start_marker, end_marker=None):
    i = html.find(start_marker)
    if i < 0: return set()
    j = html.find(end_marker, i) if end_marker else len(html)
    if j < 0: j = len(html)
    return set(re.findall(r'data-ga-id="github:([^"]+)"', html[i:j]))
official = section_logins('people_maintainers', '<div class="layer">') | section_logins('people_foundation', '<div class="layer">')
core5 = {'steipete','vincentkoc','RomneyDa','obviyus','shakkernerd'}

def is_bot(login):
    if not login: return False
    l = login.lower()
    return l.endswith('[bot]') or l.endswith('-bot') or l in {'clawsweeper','openclaw-barnacle','roboclaw','openclaw-mantis','openclaw-macos-publisher','dependabot'}

# merged-by set (human accounts that performed at least one merge in the window)
merged_by = {r['mergedBy']['login'] for r in rows
             if r.get('mergedBy') and not is_bot(r['mergedBy']['login'])}

# classify
def head_repo(r):
    h = r.get('headRepository') or {}
    return h.get('nameWithOwner')
def base_repo(r):
    b = r.get('baseRepository') or {}
    return b.get('nameWithOwner')

def classify(r):
    a = r['author']['login']
    if is_bot(a): return 'bot'
    same = head_repo(r) == base_repo(r) and base_repo(r) == 'openclaw/openclaw'
    by = a in merged_by
    off = a in official
    assoc = (r.get('authorAssociation') or '')
    strong = same or by or off
    broad = strong or assoc in {'OWNER','MEMBER','COLLABORATOR'}
    return {'strong': strong, 'broad': broad, 'same': same, 'by': by, 'off': off, 'assoc': assoc}

for r in rows:
    r['_c'] = classify(r)

human = [r for r in rows if r['_c'] != 'bot']
print('merged PRs:', len(rows), 'deduped; human:', len(human), 'bot:', len(rows)-len(human))
print('merged_by accounts:', len(merged_by), 'official list:', len(official))

def pct(n, d): return f'{100*n/d:.2f}%'
for label, key in [('strong (same-repo | merged-by | official)', 'strong'),
                   ('broad (+ author_association member/collab/owner)', 'broad')]:
    ins = [r for r in human if r['_c'][key]]
    ext = [r for r in human if not r['_c'][key]]
    print(f'\n{label}: insider {len(ins)} {pct(len(ins),len(human))}; external {len(ext)} {pct(len(ext),len(human))}')
    print('  unique insiders', len({r['author']['login'] for r in ins}), 'unique externals', len({r['author']['login'] for r in ext}))

# components
for key in ['same','by','off']:
    s=set(r['number'] for r in human if r['_c'][key])
    print(key, len(s), pct(len(s),len(human)))

# exclusive reasons among strong insiders
def reasons(r):
    return tuple(k for k in ('same','by','off') if r['_c'][k])
cnt=collections.Counter(reasons(r) for r in human if r['_c']['strong'])
print('\ninsider reason combos:')
for k,v in cnt.most_common(): print(' ', '+'.join(k) or 'none', v, pct(v,len(human)))

# assoc distribution for external (strong definition)
ext=[r for r in human if not r['_c']['strong']]
print('\nexternal assoc:', collections.Counter(r['_c']['assoc'] for r in ext).most_common())
print('external same-repo false; head missing:', sum(1 for r in ext if not head_repo(r)))
print('external top authors:', collections.Counter(r['author']['login'] for r in ext).most_common(12))
print('core5 authored:', sum(1 for r in human if r['author']['login'] in core5), pct(sum(1 for r in human if r['author']['login'] in core5), len(human)))
print('official authored:', sum(1 for r in human if r['author']['login'] in official), pct(sum(1 for r in human if r['author']['login'] in official), len(human)))
print('bots:', collections.Counter(r['author']['login'] for r in rows if r['_c']=='bot').most_common(10))

# top insider authors
ins=[r for r in human if r['_c']['strong']]
print('\ninsider top authors:', collections.Counter(r['author']['login'] for r in ins).most_common(15))
print('all top authors:', collections.Counter(r['author']['login'] for r in human).most_common(15))
