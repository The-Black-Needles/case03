# Phase 03 — Artefatos de sessão (comando + resultado + análise)

## 3.1 session artifacts (list)
**Comando (DevTools):**
~~~http
GET paloalto-linux-messages-*/_search
{
  "size": 50,
  "_source": ["@timestamp","log.file.path","message","event.original"],
  "query": {
    "query_string": {
      "query": "(message:*\"/tmp/sslvpn/session_\" OR event.original:*\"/tmp/sslvpn/session_\") OR (message:*\"failed to load file /tmp/sslvpn/session_\" OR event.original:*\"failed to load file /tmp/sslvpn/session_\")"
    }
  },
  "sort": [{ "@timestamp": "asc" }]
}
~~~

**Resultado (resumo real):**
~~~json
{
  "total": 10000,
  "first": "2024-04-26T17:57:30.751488514Z",
  "last": "2024-04-26T17:57:30.893315446Z",
  "failed_load_count": 0,
  "unique_session_files": 0,
  "top_session_files": [],
  "per_hour": { "2024-04-26T17": 50 },
  "samples": [
    {
      "ts": "2024-04-26T17:57:30.751488514Z",
      "path": "/mnt/palo_alto2/var/log/pan/check_plugin_compat.log",
      "msg": "2024-04-21 07:55:35,686 check_plugin_compat INFO Check dependencies during installation of dlp 5.0.1"
    },
    {
      "ts": "2024-04-26T17:57:30.758887761Z",
      "path": "/mnt/palo_alto2/var/log/pan/check_plugin_compat.log",
      "msg": "2024-04-21 07:55:36,342 check dependencies during installation of vm_series 5.0.1"
    },
    {
      "ts": "2024-04-26T17:57:30.758193291Z",
      "path": "/mnt/palo_alto2/var/log/pan/check_plugin_compat.log",
      "msg": "2024-04-21 07:55:36,048 check dependencies during installation of openconfig 2.0.0"
    }
  ]
}
~~~

**Análise:**
- O resumo **não** evidenciou `session_*` (contadores em zero, amostras não relacionadas).
- Possíveis causas:
  1) Não há artefatos `session_*` neste dataset; **ou**
  2) O parser/consulta não capturou por variações (ex.: diretório diferente/capitalização); **ou**
  3) O resumo foi gerado de janela/índice diferente.

**Próximo:** seguir com sinais confirmados: `hipreport.esp`, `device_telemetry` (`echo|base64|bash`), `wget|curl`, `worldtimeapi`, e consolidar timeline.
