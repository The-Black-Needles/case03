import re, json, sys, pathlib

def summarize_hits_text(text):
    # total (se existir)
    m_total = re.search(r'"total"\s*:\s*\{\s*"value"\s*:\s*(\d+)', text)
    total = int(m_total.group(1)) if m_total else None

    # timestamps (primeiro/último por ordem no arquivo)
    ts = re.findall(r'"@timestamp"\s*:\s*"([^"]+)"', text)
    first = ts[0] if ts else None
    last  = ts[-1] if ts else None

    # capturar até 3 blocos de _source
    samples = []
    for m in re.finditer(r'"_source"\s*:\s*\{(.*?)\}\s*,\s*"sort"', text, flags=re.S):
        src = m.group(1)

        # ts
        mts = re.search(r'"@timestamp"\s*:\s*"([^"]+)"', src)
        ts_val = mts.group(1) if mts else None

        # log.file.path
        mpath = re.search(r'"log"\s*:\s*\{.*?"file"\s*:\s*\{.*?"path"\s*:\s*"([^"]+)"', src, flags=re.S)
        path_val = mpath.group(1) if mpath else None

        # message (tenta triple-quote primeiro, depois normal)
        mmsg3 = re.search(r'"message"\s*:\s*"""\s*(.*?)\s*"""', src, flags=re.S)
        if mmsg3:
            msg_val = mmsg3.group(1)
        else:
            mmsg = re.search(r'"message"\s*:\s*"([^"]*)"', src)
            if mmsg:
                msg_val = mmsg.group(1)
            else:
                morig3 = re.search(r'"event"\s*:\s*\{.*?"original"\s*:\s*"""\s*(.*?)\s*"""', src, flags=re.S)
                if morig3:
                    msg_val = morig3.group(1)
                else:
                    morig = re.search(r'"event"\s*:\s*\{.*?"original"\s*:\s*"([^"]*)"', src, flags=re.S)
                    msg_val = morig.group(1) if morig else None

        samples.append({"ts": ts_val, "path": path_val, "msg": msg_val})
        if len(samples) >= 3:
            break

    return {"total": total, "first": first, "last": last, "samples": samples}

def main():
    if len(sys.argv) != 3:
        print("usage: python3 summarize_raw_json.py <input.json> <output.summary.json>", file=sys.stderr)
        sys.exit(1)
    inp = sys.argv[1]
    out = sys.argv[2]
    text = pathlib.Path(inp).read_text(errors="ignore")
    summary = summarize_hits_text(text)
    pathlib.Path(out).write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"wrote summary: {out}")

if __name__ == "__main__":
    main()
