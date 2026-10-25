# Tooling to turn local edits of book340.md into Docs `find`-based ops.
import re, json, difflib, sys, os
D = os.path.dirname(os.path.abspath(__file__))
RAW = open(D + '/book340.md').read().split('\n')

def unesc(s):
    s = s.replace('&#91;', '[').replace('&#93;', ']')
    s = s.replace('\\*', '\x00')
    s = s.replace('**', '')
    s = re.sub(r'(?<![\w*])\*([^*\n]+)\*(?![\w*])', r'\1', s)
    s = re.sub(r'\\([\\`_{}\[\]()#+\-.!|<>~$])', r'\1', s)
    return s.replace('\x00', '*')

def split_row(line):
    body = line.strip()
    if body.startswith('|'): body = body[1:]
    if body.endswith('|') and not body.endswith('\\|'): body = body[:-1]
    cells = re.split(r'(?<!\\)\|', body)
    return [c.strip() for c in cells]

def is_sep(line):
    return bool(re.match(r'^\|[\s:|\-]+\|$', line.strip()))

def strip_prefix(l):
    l = re.sub(r'^#{1,6} ', '', l)
    l = re.sub(r'^\s*(?:[-*] |\d+\. )', '', l)
    return l

# blocks: list of dict(key=(line,col|None), text)
def build_blocks(lines):
    out = []
    for i, l in enumerate(lines, 1):
        if not l.strip(): continue
        if l.startswith('|'):
            if is_sep(l): continue
            for c, cell in enumerate(split_row(l)):
                out.append({'key': (i, c), 'text': unesc(cell)})
        else:
            out.append({'key': (i, None), 'text': unesc(strip_prefix(l))})
    return out

class Doc:
    def __init__(self):
        self.blocks = build_blocks(RAW)
        self.idx = {b['key']: n for n, b in enumerate(self.blocks)}
    def text(self, key):
        return self.blocks[self.idx[key]]['text']
    def count_before(self, find, n_block, upto_in_block=None):
        """number of occurrences of `find` in blocks before n_block (+ in block before offset)"""
        c = 0
        for b in self.blocks[:n_block]:
            c += b['text'].count(find)
        if upto_in_block is not None:
            c += self.blocks[n_block]['text'][:upto_in_block].count(find) if False else 0
        return c
    def total(self, find):
        return sum(b['text'].count(find) for b in self.blocks)

    def ops_for(self, key, new):
        n = self.idx[key]
        old = self.blocks[n]['text']
        if old == new: return []
        tok = lambda t: re.findall(r'\s+|[^\s]+', t)
        ot, nt = tok(old), tok(new)
        sm = difflib.SequenceMatcher(None, ot, nt, autojunk=False)
        codes = [c for c in sm.get_opcodes() if c[0] != 'equal']
        hunks = []
        for c in codes:
            if hunks and c[1] - hunks[-1][2] <= 3:
                m = hunks[-1]; hunks[-1] = (m[0], m[1], c[2], m[3], c[4])
            else:
                hunks.append((c[0], c[1], c[2], c[3], c[4]))
        while True:
            plan = []; bad = None
            for idx, (tag, i1, i2, j1, j2) in enumerate(hunks):
                lo = hunks[idx-1][2] if idx > 0 else 0
                hi = hunks[idx+1][1] if idx + 1 < len(hunks) else len(ot)
                L = R = 0
                while True:
                    find = ''.join(ot[i1-L:i2+R])
                    if find.strip() and self.total_with(n, old, find) == 1: break
                    cl = i1 - L > lo; cr = i2 + R < hi
                    if cl and (L <= R or not cr): L += 1
                    elif cr: R += 1
                    else:
                        find = None; break
                if find is None:
                    bad = idx; break
                plan.append((i1-L, i2+R, j1, j2, L, R))
            if bad is None: break
            if len(hunks) == 1:
                # cannot be made unique: use nth on the widest range
                plan = [(max(0, hunks[0][1]-1), min(len(ot), hunks[0][2]+1), hunks[0][3], hunks[0][4], 1, 1)]
                break
            j = bad + 1 if bad + 1 < len(hunks) else bad - 1
            a_, b_ = min(bad, j), max(bad, j)
            m1, m2 = hunks[a_], hunks[b_]
            hunks[a_:b_+1] = [(m1[0], m1[1], m2[2], m1[3], m2[4])]
        ops = []
        cur_t = list(ot)
        for (A, B, j1, j2, L, R), (tag, i1, i2, _, _) in reversed(list(zip(plan, hunks))):
            cur = ''.join(cur_t)
            find = ''.join(cur_t[A:B])
            rep = ''.join(cur_t[A:i1]) + ''.join(nt[j1:j2]) + ''.join(cur_t[i2:B])
            pos = len(''.join(cur_t[:A]))
            if rep:
                op = {'op': 'replace', 'target': {'kind': 'find', 'text': find}, 'with': {'as': 'text', 'from': {'kind': 'inline', 'content': rep}}}
            else:
                op = {'op': 'delete', 'target': {'kind': 'find', 'text': find}}
            if self.total_with(n, cur, find) > 1:
                op['target']['nth'] = self.occ_index(n, cur, pos, find)
            ops.append(op)
            cur_t[A:B] = [rep] if rep else []
        self.blocks[n]['text'] = ''.join(cur_t)
        assert self.blocks[n]['text'] == new, (key, self.blocks[n]['text'][:100], new[:100])
        return ops
    def total_with(self, n, cur, find):
        c = 0
        for m, b in enumerate(self.blocks):
            t = cur if m == n else b['text']
            c += t.count(find)
        return c
    def _unique_pos(self, n, cur, find):
        return None
    def occ_index(self, n, cur, pos, find):
        c = 0
        for m, b in enumerate(self.blocks[:n]):
            c += b['text'].count(find)
        c += cur[:pos].count(find) + 1
        return c

def dump(ops, name, per=14):
    for k in range(0, len(ops), per):
        p = f'{D}/ops/{name}_{k//per+1:02d}.json'
        json.dump({'ops': ops[k:k+per]}, open(p, 'w'), ensure_ascii=False, separators=(',', ':'))
        print(p, os.path.getsize(p))

class Edits:
    def __init__(self):
        self.doc = Doc(); self.new = {}
        sf = D + '/nostate.json'
        if os.path.exists(sf):
            st = json.load(open(sf))
            for k, v in st.items():
                a, b = k.split(',')
                key = (int(a), None if b == 'None' else int(b))
                self.doc.blocks[self.doc.idx[key]]['text'] = v
    def save_state(self):
        st = {}
        for b in self.doc.blocks:
            st['%d,%s' % b['key']] = b['text']
        json.dump(st, open(D + '/state2.json', 'w'), ensure_ascii=False)
    def span(self, line, start, end, new, col=None):
        c = self.cur(line, col)
        assert c.count(start) == 1, (line, start, c.count(start))
        i = c.index(start)
        j = c.index(end, i) + len(end)
        self.new[(line, col)] = c[:i] + new + c[j:]
    def delete(self, line, old, col=None, count=1):
        self.sub(line, old, '', col, count)
    def cur(self, line, col=None):
        k = (line, col)
        return self.new.get(k, self.doc.text(k))
    def sub(self, line, old, new, col=None, count=1):
        c = self.cur(line, col)
        assert c.count(old) == count, (line, col, old, c.count(old), c[:100])
        self.new[(line, col)] = c.replace(old, new)
    def full(self, line, new, col=None):
        self.new[(line, col)] = new
    def gen(self):
        ops = []
        for key in sorted(self.new, key=lambda k: self.doc.idx[k]):
            ops += self.doc.ops_for(key, self.new[key])
        self.new = {}
        return ops
