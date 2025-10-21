# Phase 01 — Descoberta do Ambiente

**Objetivo:** validar saúde básica do cluster e identificar índices relevantes do lab.

**Consultas executadas:**
- GET /_cluster/health?pretty
- GET /_cat/indices/paloalto-*,paloalto-linux-*,filebeat-*,logs-*?v&s=index&h=index,docs.count,store.size

**Achados:**
- `status: yellow` em single-node é esperado (réplicas não alocadas).
- Índices relevantes para o caso: `paloalto-linux-messages-*` (logs de sistema com gpsvc), `paloalto-sslvpn-access-*`, `paloalto-nginx-*`, `paloalto-syslog-*`.

**Próximos passos (Phase 02):**
- Confirmar presença de `gpsvc.log`.
- Procurar erros chave: `failed to unmarshal session` e artefatos `/tmp/sslvpn/session_*`.
