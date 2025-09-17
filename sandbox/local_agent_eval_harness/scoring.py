import math

def _norm(v):
    if isinstance(v, float):
        return round(v, 4)
    return v

def score(expected, got):
    """Return (score_float, details_dict). Compares dict/list scalars with tolerant floats."""
    def flatten(x, prefix=''):
        items = {}
        if isinstance(x, dict):
            for k, v in x.items():
                items.update(flatten(v, prefix + '/' + str(k)))
        elif isinstance(x, list):
            for i, v in enumerate(x):
                items.update(flatten(v, prefix + '/' + str(i)))
        else:
            items[prefix or '/'] = _norm(x)
        return items

    exp = flatten(expected)
    gotf = flatten(got)
    total = len(exp)
    correct = 0
    diffs = {}
    for k, v in exp.items():
        gv = gotf.get(k, None)
        ok = False
        if isinstance(v, float) and isinstance(gv, float):
            ok = abs(v - gv) <= 1e-2
        else:
            ok = (v == gv)
        if ok:
            correct += 1
        else:
            diffs[k] = dict(expected=v, got=gv)
    return (correct/total if total else 0.0, dict(total=total, correct=correct, diffs=diffs))
