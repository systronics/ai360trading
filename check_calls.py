"""
check_calls.py v1.0 (2026-11-06) - static guard against the bug class that hid in trading_bot.py for 3.5 months:
a call passes a keyword (or too many/few arguments) that the function does not accept, the TypeError is swallowed by a try/except, and the feature silently does nothing
(`_find_nifty200_col(..., subs=[...])` while the parameter is `substring_keywords` -> ATR read 0 for every stock since 2026-07-20).

For every .py file in the repo root it checks calls to (a) functions defined in the same file and (b) `module.func(...)` / `from module import func` of other repo files:
unknown keyword, too many positional arguments, missing required argument. Methods and dynamic calls are skipped (no false alarms from guessing).
Exit code 1 when anything is found. USAGE: python check_calls.py [--quiet]
"""
import ast
import glob
import os
import sys


def sig_of(fn):
    a = fn.args
    pos = [x.arg for x in a.posonlyargs + a.args]
    kwonly = [x.arg for x in a.kwonlyargs]
    n_def = len(a.defaults)
    required_pos = pos[:len(pos) - n_def] if n_def else pos[:]
    required_kw = [x.arg for x, d in zip(a.kwonlyargs, a.kw_defaults) if d is None]
    return {"pos": pos, "kwonly": kwonly, "req_pos": required_pos, "req_kw": required_kw,
            "varargs": a.vararg is not None, "varkw": a.kwarg is not None}


def check_call(call, name, s, where):
    probs = []
    if any(isinstance(x, ast.Starred) for x in call.args) or any(k.arg is None for k in call.keywords):
        return probs                                   # *args / **kwargs at the call site: cannot judge
    names = set(s["pos"]) | set(s["kwonly"])
    if len(call.args) > len(s["pos"]) and not s["varargs"]:
        probs.append(f"{where}: {name}() gets {len(call.args)} positional args but takes at most {len(s['pos'])}")
    given = set(s["pos"][:len(call.args)])
    for k in call.keywords:
        if k.arg not in names and not s["varkw"]:
            probs.append(f"{where}: {name}() has no parameter '{k.arg}' (has: {', '.join(sorted(names)) or 'none'})")
        given.add(k.arg)
    missing = [p for p in s["req_pos"] + s["req_kw"] if p not in given]
    if missing and not s["varkw"]:
        probs.append(f"{where}: {name}() is missing required argument(s): {', '.join(missing)}")
    return probs


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    files = sorted(f for f in glob.glob("*.py") if not f.startswith(("test_", "check_")))
    trees, funcs = {}, {}
    for f in files:
        try:
            t = ast.parse(open(f, encoding="utf-8").read(), f)
        except SyntaxError as e:
            print(f"SYNTAX {f}: {e}")
            return 1
        trees[f] = t
        d = {}
        for n in t.body:
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                d[n.name] = sig_of(n)
        funcs[os.path.splitext(f)[0]] = d
    problems, checked = [], 0
    for f, t in trees.items():
        mod = os.path.splitext(f)[0]
        local = dict(funcs[mod])
        # names defined twice or redefined as a variable are ambiguous: drop them
        counts = {}
        for n in ast.walk(t):
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                counts[n.name] = counts.get(n.name, 0) + 1
        for nm, c in counts.items():
            if c > 1:
                local.pop(nm, None)
        imported, modalias = {}, {}
        for n in t.body:
            if isinstance(n, ast.ImportFrom) and n.module in funcs and n.level == 0:
                for a in n.names:
                    if a.name in funcs[n.module]:
                        imported[a.asname or a.name] = (n.module, a.name)
            if isinstance(n, ast.Import):
                for a in n.names:
                    if a.name in funcs:
                        modalias[a.asname or a.name] = a.name
        for n in ast.walk(t):
            if not isinstance(n, ast.Call):
                continue
            fn = n.func
            if isinstance(fn, ast.Name):
                if fn.id in local:
                    checked += 1
                    problems += check_call(n, fn.id, local[fn.id], f"{f}:{n.lineno}")
                elif fn.id in imported:
                    m, nm = imported[fn.id]
                    checked += 1
                    problems += check_call(n, f"{m}.{nm}", funcs[m][nm], f"{f}:{n.lineno}")
            elif isinstance(fn, ast.Attribute) and isinstance(fn.value, ast.Name) and fn.value.id in modalias:
                m = modalias[fn.value.id]
                if fn.attr in funcs[m]:
                    checked += 1
                    problems += check_call(n, f"{m}.{fn.attr}", funcs[m][fn.attr], f"{f}:{n.lineno}")
    for p in problems:
        print("CALL-MISMATCH", p)
    if "--quiet" not in argv:
        print(f"[check_calls] {len(files)} files, {checked} calls checked, {len(problems)} mismatch(es)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
