import re, json, sys, pathlib

def strip_wrappers(txt: str) -> str:
    # remove code fences e linhas de comando
    txt = txt.replace("```", "")
    lines = []
    for line in txt.splitlines():
        s = line.strip()
        if s.startswith(("GET ", "POST ", "PUT ", "DELETE ", "### ", "# ")):
            continue
        lines.append(line)
    return "\n".join(lines).strip()

def extract_first_json_obj(txt: str) -> str:
    # encontra o primeiro objeto JSON balanceado { ... }
    start = txt.find("{")
    if start == -1:
        raise ValueError("Nenhum '{' encontrado para iniciar JSON.")
    i = start
    depth = 0
    in_str = False
    esc = False
    while i < len(txt):
        ch = txt[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
        else:
            if ch == '"':
                in_str = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return txt[start:i+1]
        i += 1
    raise ValueError("Objeto JSON não balanceado (faltou '}' ).")

def fix_triple_quotes(json_like: str) -> str:
    # converte """ ... """ em strings JSON válidas
    def repl(m):
        inner = m.group(1)
        return json.dumps(inner)  # aplica escapes apropriados
    return re.sub(r'"""(.*?)"""', repl, json_like, flags=re.S)

def load_json_lenient(path: str):
    raw = pathlib.Path(path).read_text(errors="ignore")
    raw = strip_wrappers(raw)
    # tenta direto
    try:
        return json.loads(raw)
    except Exception:
        pass
    # tenta extrair o primeiro objeto JSON balanceado
    try:
        obj = extract_first_json_obj(raw)
    except Exception as e:
        # salva debug e reergue
        pathlib.Path(path + ".debug.txt").write_text(raw)
        raise
    # corrige triple quotes
    obj_fixed = fix_triple_quotes(obj)
    # tenta parsear
    try:
        return json.loads(obj_fixed)
    except Exception as e:
        # salva debug para inspeção
        pathlib.Path(path + ".fixed.json").write_text(obj_fixed)
        raise

def iso_hour(ts):
    return ts[:13] if ts and len(ts) >= 13 else ts

def summarize_hits(doc):
    hits = (doc.get("hits") or {}).get("hits") or []
    total_obj = (doc.get("hits") or {}).get("total")
    total = total_obj.get("value") if isinstance(total_obj, dict) else total_obj

    first = hits[0].get("_source", {}).get("@timestamp") if hits else None
    last  = hits[-1].get("_source", {}).get("@timestamp") if hits else None

    # amostras
    samples = []
    for h in hits[:3]:
        src = h.get("_source", {})
        path = (((src.get("log") or {}).get("file") or {}).get("path"))
        msg  = src.get("message") or ((src.get("event") or {}).get("original"))
        samples.append({"ts": src.get("@timestamp"), "path": path, "msg": msg})

    # contagens auxiliares
    import collections, re as _re
    per_hour = collections.Counter()
    failed_load = 0
    session_counter = collections.Counter()

    for h in hits:
        src = h.get("_source", {})
        ts  = src.get("@timestamp")
        if ts: per_hour[iso_hour(ts)] += 1
        path = (((src.get("log") or {}).get("file") or {}).get("path")) or ""
        msg  = src.get("message") or ((src.get("event") or {}).get("original")) or ""
        blob = f"{path} {msg}"

        if "failed to load file /tmp/sslvpn/session_" in blob:
            failed_load += 1
        for m in _re.finditer(r'/tmp/sslvpn/session_[^\s"\'\)\]]+', blob):
            session_counter[m.group(0)] += 1

    summary = {
        "total": total,
        "first": first,
        "last": last,
        "failed_load_count": failed_load,
        "unique_session_files": len(session_counter),
        "top_session_files": [{"path": p, "count": c} for p,c in session_counter.most_common(20)],
        "per_hour": dict(sorted(per_hour.items())),
        "samples": samples
    }
    return summary, session_counter

def write_csv_session_iocs(counter, path_out):
    lines = ["artifact_path,count"]
    for p,c in counter.most_common():
        lines.append(f"{p},{c}")
    pathlib.Path(path_out).write_text("\n".join(lines))

def summarize_agg(path):
    d = load_json_lenient(path)
    agg = d.get("aggregations") or {}
    fs = (agg.get("first_seen") or {}).get("value_as_string") or (agg.get("first_seen") or {}).get("value")
    ls = (agg.get("last_seen")  or {}).get("value_as_string")  or (agg.get("last_seen")  or {}).get("value")
    hist = (agg.get("per_hour") or {}).get("buckets") or []
    buckets = [{"key_as_string": b.get("key_as_string"), "doc_count": b.get("doc_count")} for b in hist[:100]]
    return {"first_seen": fs, "last_seen": ls, "per_hour_buckets": buckets}

def main():
    if len(sys.argv) != 3:
        print("usage: python3 tools/analyze_phase03.py <session_list_json> <agg_first_last_json>", file=sys.stderr)
        sys.exit(1)

    session_path = sys.argv[1]
    agg_path = sys.argv[2]

    sess_doc = load_json_lenient(session_path)
    sess_summary, sess_counter = summarize_hits(sess_doc)

    # outputs da parte de session_*
    out_summary = pathlib.Path(session_path).with_suffix(".summary.json")
    out_summary.write_text(json.dumps(sess_summary, indent=2, ensure_ascii=False))
    write_csv_session_iocs(sess_counter, str(pathlib.Path(session_path).with_suffix(".iocs.csv")))

    # outputs das agregações
    agg_summary = summarize_agg(agg_path)
    pathlib.Path(agg_path).with_suffix(".summary.json").write_text(json.dumps(agg_summary, indent=2, ensure_ascii=False))

    print(f"[ok] wrote: {out_summary}")
    print(f"[ok] wrote: {pathlib.Path(session_path).with_suffix('.iocs.csv')}")
    print(f"[ok] wrote: {pathlib.Path(agg_path).with_suffix('.summary.json')}")

if __name__ == "__main__":
    main()
