# PaloAlto RCE Elastic SOC

Este repositório documenta a resposta a incidente (DFIR/Threat Hunting) do lab **PaloAltoRCE** (CyberDefenders), que simula exploração de uma falha de **execução remota de código (RCE)** em firewalls Palo Alto (PAN-OS) via GlobalProtect – comumente associada ao **CVE-2024-3400**. O caso explora como um atacante pode executar comandos com privilégios elevados no firewall, estabelecer persistência e pivotar para ativos internos.

> **Escopo:** Evidenciar o processo investigativo de um analista SOC/DFIR – da formulação de hipóteses, consultas no Kibana/Elasticsearch, coleta de evidências e construção da timeline, até conclusões e recomendações – com **artefatos reproduzíveis** (queries, IoCs e uma regra Sigma base).

---

## 1) Ferramentas & Ambiente

- **Elastic Stack / Kibana Dev Tools** (consultas REST/ES)  
- **Kibana (Discover)** com **KQL**  
- **CyberDefenders** (lab PaloAltoRCE)  
- **GitHub** (versionamento da documentação)

> **Padrão de índice:** ajuste `paloalto-*` nas consultas para refletir seu ambiente (ex.: `paloalto-*`, `logs-*`, `filebeat-*` etc.).  

---

## 2) Metodologia de Investigação

**Ciclo de hunting:** hipótese → busca → validação → refinamento → correlação → conclusão.

**MITRE ATT&CK (mapeamento resumido):**  
- *Initial Access/Execution:* exploração do portal GlobalProtect (T1203/T1059)  
- *Persistence:* `cron`/serviço/artefatos no appliance (T1053)  
- *C2/Lateral/Exfil:* HTTP/SMB/WinRM e artefatos via CLI (T1041/T1021)

**Passo a passo aplicado neste repo:**
1. **Descoberta do dado** (índices, datasets, campos úteis).  
2. **Hunting inicial** com strings conhecidas (e.g., `gpsvc`, `failed to unmarshal session`, `hipreport.esp`, `curl`/`wget`).  
3. **Confirmação do vetor** (acessos SSL-VPN/GlobalProtect; endpoint explorado).  
4. **Pivôs de investigação** (IPs de origem, `user_agent`, paths `/tmp/sslvpn/session_*`, `device_telemetry`).  
5. **Linha do tempo** (primeiro/último evento de exploração confirmada).  
6. **Extração de IoCs** → `ioc/iocs.csv`.  
7. **Conclusões e recomendações** (patching, credenciais, varredura de IoCs e monitoração contínua).

---

## 3) Consultas no Kibana Dev Tools (Elasticsearch)

Todas as consultas estão prontas em **`queries/devtools.http`** para colar no **Dev Tools**.

**Cobertura das consultas principais:**
- Descoberta de **índices**, **datasets** e **paths de log** (ex.: `gpsvc.log`).  
- Erros e artefatos públicos associados ao CVE (ex.:  
  `failed to unmarshal session(`,  
  `failed to load file /tmp/sslvpn/session_` – zero-byte,  
  endpoint `hipreport.esp`).  
- Execução externa a partir do firewall (**`wget` / `curl`**), marcadores como `worldtimeapi.org`, e termos como `patch`/`policy`.  
- Top **IPs de origem** e **primeiro/último timestamp** de exploração confirmada.

Para buscas rápidas no **Discover/KQL**, use **`queries/kql.md`**.

---

## 4) Linha de Raciocínio (Timeline Analítica)

| Etapa | Evidência (consulta) | O que observamos | Implicação |
|---|---|---|---|
| 1. Primeiras falhas de sessão | `failed to unmarshal session` | Mensagens no `gpsvc.log` com SESSID malformado | *Probing*/testes de exploração |
| 2. Criação `session_*` | `failed to load file /tmp/sslvpn/session_` | Criação de arquivos de sessão (zero-byte) | Abuso do mecanismo de sessão |
| 3. Endpoint explorado | `hipreport.esp` | Requests ao endpoint SSL-VPN | Vetor de injeção de comando |
| 4. Execução externa | `wget`/`curl` | Downloads/comandos iniciados do appliance | Execução remota/persistência |
| 5. Indicadores extras | `worldtimeapi.org`, `patch`, `policy` | Marcadores relatados publicamente | Corrobora exploração |
| 6. Enriquecimento | Top `source.ip`, `user_agent` | IP(s) atacante(s) e perfil | IoCs e bloqueios |
| 7. Janela do incidente | 1º e último evento | Linha do tempo consolidada | Escopo e contenção |

---

## 5) Respostas às 6 Questões do Caso

Use **`answers/case-answers.md`**. O molde pede, para **cada** pergunta:
- **Resposta curta**,  
- **Evidência (consulta + screenshot)**,  
- **Trecho de log** relevante,  
- **Raciocínio** (como a evidência responde à pergunta).

**Exemplos do que geralmente se pede:**
1. **Vetor/endpoint** de exploração (p.ex., `POST /ssl-vpn/hipreport.esp` com injeção no `SESSID`).  
2. **Primeiro timestamp** de exploração confirmada.  
3. **IP(s) de origem** maliciosos (top `source.ip` filtrando pelos eventos chave).  
4. **Comandos/ações** do atacante (busca por `curl`, `wget`, backticks, `${IFS}`, etc.).  
5. **Persistência/pós-exploração** (artefatos, chamadas externas, scripts).  
6. **Impacto/risco** e **ações imediatas** (isolamento, coleta, patching/hardening, revisão de credenciais).

---

## 6) IoCs & Detecções

- Preencha `ioc/iocs.csv` com **IPs**, **URLs**, **paths** e **strings** relevantes e os *first/last seen*.  
- Use `ioc/detections-sigma.yml` como **base** para criar alertas no SIEM (ajuste campos conforme seu pipeline/logsource).

---

## 7) Conclusões e Lições Aprendidas

- **Confirmação de exploração** coerente com CVE-2024-3400 (artefatos de sessão, endpoint do portal, execução externa).  
- **Risco**: execução como **root** no firewall, possível **persistência** e **movimentação lateral**.  
- **Mitigação imediata**: aplicar correções do PAN-OS; restringir exposição (portal/management); coletar **Tech Support File** antes de qualquer reset/formatação; varrer IoCs; rotacionar credenciais; revisar acessos/contas de serviço; implantar/ajustar detecções.

---

## 8) Como usar este repositório

1. **Rode** os blocos de `queries/devtools.http` no Dev Tools.  
2. **Anote** evidências + prints em `artifacts/screenshots/` (nomeie `YYYYMMDD_HHMM_descricao.png`).  
3. **Responda** às 6 questões em `answers/case-answers.md`.  
4. **Atualize** `ioc/iocs.csv` e a **Sigma** em `ioc/detections-sigma.yml`.  
5. **Commit & push**.

---

## 9) Referências (para estudo/embasamento)

- Volexity – *Zero-Day Exploitation of CVE-2024-3400* (Apr/12/2024)  
  https://www.volexity.com/blog/2024/04/12/zero-day-exploitation-of-unauthenticated-remote-code-execution-vulnerability-in-globalprotect-cve-2024-3400/

- Volexity – *Detecting Compromise of CVE-2024-3400 on Palo Alto Networks GlobalProtect Devices* (May/15/2024)  
  https://www.volexity.com/blog/2024/05/15/detecting-compromise-of-cve-2024-3400-on-palo-alto-networks-globalprotect-devices/

- watchTowr Labs – *Palo Alto: Putting the Protecc in GlobalProtect (CVE-2024-3400)* (Apr/16/2024)  
  https://labs.watchtowr.com/palo-alto-putting-the-protecc-in-globalprotect-cve-2024-3400/

- Palo Alto Networks – *Security Advisory CVE-2024-3400*  
  https://security.paloaltonetworks.com/CVE-2024-3400

- CISA – *Palo Alto Networks Releases Guidance for CVE-2024-3400*  
  https://www.cisa.gov/news-events/alerts/2024/04/12/palo-alto-networks-releases-guidance-vulnerability-pan-os-cve-2024-3400
