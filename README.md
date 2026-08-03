# YouTube Scraper — Radar Ódio

Scraper incremental para coleta de vídeos e comentários do YouTube via API oficial (v3).  
Desenvolvido para pesquisa de discurso de ódio no mestrado **Radar Ódio**.

---

## Índice

1. [Pré-requisitos](#pré-requisitos)
2. [Configuração](#configuração)
3. [Definindo os alvos](#definindo-os-alvos)
4. [Como rodar](#como-rodar)
5. [Como funciona a coleta](#como-funciona-a-coleta)
6. [Estrutura dos dados coletados](#estrutura-dos-dados-coletados)
7. [Logs](#logs)
8. [Estrutura do código](#estrutura-do-código)

---

## Pré-requisitos

| Opção | Requisitos |
|---|---|
| **Docker** (recomendado) | [Docker Desktop](https://www.docker.com/products/docker-desktop/) |
| **Local** | Python 3.11+ |

Independente da opção, você precisa de uma **API Key do YouTube Data v3**.

### Obtendo a API Key

1. Acesse o [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um projeto (ou use um existente)
3. Ative a **YouTube Data API v3** em *APIs e Serviços → Biblioteca*
4. Em *APIs e Serviços → Credenciais*, clique em **Criar credenciais → Chave de API**
5. Copie a chave gerada

> **Quota:** cada projeto tem 10.000 unidades/dia gratuitas. Uma chamada de comentários consome ~1 unidade por 100 comentários. Para coletar mais, adicione múltiplas chaves (projetos diferentes) no `.env`.

---

## Configuração

Copie o arquivo de exemplo e preencha com suas chaves:

```bash
cp .env.example .env
```

Edite o `.env`:

```env
# Uma chave — use esta variável
YOUTUBE_API_KEY=AIzaSy...

# Múltiplas chaves separadas por vírgula (o scraper alterna automaticamente quando uma esgota)
YOUTUBE_API_KEYS=AIzaSy...,AIzaSy...,AIzaSy...

# Intervalo entre requisições (segundos) — evita rate limit
REQUEST_SLEEP_SECONDS=1

# Intervalo entre ciclos completos de coleta (segundos) — padrão: 30 min
LOOP_INTERVAL_SECONDS=1800
```

Crie também o `.env.example` para versionamento:

```env
YOUTUBE_API_KEY=
YOUTUBE_API_KEYS=
REQUEST_SLEEP_SECONDS=1
LOOP_INTERVAL_SECONDS=1800
```

---

## Definindo os alvos

Os alvos ficam na pasta `targets/`. Edite os arquivos antes de rodar.

### `targets/videos.txt`

Uma URL de vídeo por linha. Aceita qualquer formato do YouTube:

```
https://www.youtube.com/watch?v=2IFCBt4HTd8
https://www.youtube.com/shorts/B2VzL2EcPlY
https://youtu.be/nvxmqytHm_4
```

### `targets/channels.txt`

Um **Channel ID** por linha (não o @ nem o nome — o ID que começa com `UC`):

```
UC5rO0aTewMfpk2UKKPTLBYw
UCBSMDyh_5qG8grvVu-VIEuw
```

> **Como achar o Channel ID:** abra o canal no YouTube → clique em "Sobre" → "Compartilhar canal" → "Copiar ID do canal". Ou use a URL: `youtube.com/channel/UC...` — o ID é o trecho `UC...`.

Quando um canal é adicionado, o scraper coleta **todos os vídeos** publicados nele, não só os mais recentes.

---

## Como rodar

### Com Docker (recomendado)

```bash
# 1. Construir a imagem
docker compose build

# 2. Rodar em segundo plano
docker compose up -d

# 3. Acompanhar os logs em tempo real
docker compose logs -f

# 4. Parar
docker compose down
```

O container reinicia automaticamente se o processo cair (`restart: unless-stopped`).

### Sem Docker (local)

```bash
# 1. Criar e ativar o ambiente virtual
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Rodar
python main.py
```

### Migrar dados coletados anteriormente

Se você já tem dados no formato antigo (`data/videos.json` + `data/comments.json`):

```bash
python migrate.py
```

Isso reorganiza os dados na hierarquia atual sem deletar os arquivos originais.

---

## Como funciona a coleta

### Visão geral do fluxo

```
main.py
  └── YouTubeClientPool          — gerencia as API keys
        └── run_scraper_pipeline — loop infinito de coleta
              └── run_once
                    ├── collect_target_video_ids   — descobre todos os vídeos
                    │     ├── lê targets/videos.txt → extrai IDs das URLs
                    │     └── lê targets/channels.txt → busca todos os vídeos do canal
                    │
                    └── para cada video_id:
                          process_video_with_key_fallback
                            └── process_video
                                  ├── verifica se já foi coletado (state.json)
                                  ├── busca metadados do vídeo
                                  ├── busca todos os comentários + respostas
                                  └── salva em data/channels/{channel_id}/videos/{video_id}/
```

### Ciclo de vida de um vídeo

```
┌─────────────────────────────────────────────────────────────┐
│  1. JÁ PROCESSADO?                                          │
│     Sim → pula (estado salvo em data/state.json)           │
│     Não → continua                                          │
│                                                             │
│  2. BUSCA METADADOS (videos.list)                           │
│     título, descrição, views, likes, contagem comentários   │
│                                                             │
│  3. BUSCA COMENTÁRIOS (commentThreads.list)                 │
│     → até 100 threads por página, paginação automática      │
│     → para cada thread com mais de 5 respostas:             │
│        busca todas via comments.list (paginação separada)   │
│                                                             │
│  4. SALVA OS DADOS                                          │
│     data/channels/{channel_id}/videos/{video_id}/           │
│       ├── video.json                                        │
│       └── comments.json                                     │
│                                                             │
│  5. MARCA COMO PROCESSADO em state.json                     │
└─────────────────────────────────────────────────────────────┘
```

### Gerenciamento de quota e múltiplas API keys

A YouTube Data API tem limite de **10.000 unidades por dia por projeto**. O scraper gerencia isso automaticamente:

```
Quota esgotada na key atual
  └── Tem outra key disponível?
        Sim → alterna para a próxima e continua
        Não → aguarda até meia-noite (horário do Pacífico, quando a Google reseta)
               depois reinicia com todas as keys disponíveis
```

Para configurar múltiplas keys, separe por vírgula no `.env`:
```
YOUTUBE_API_KEYS=chave1,chave2,chave3
```

### Coleta incremental

O scraper roda em **loop contínuo**. A cada ciclo:
- Vídeos já coletados são **pulados** (verificado via `state.json`)
- Apenas vídeos novos são processados
- Ao terminar o ciclo, aguarda `LOOP_INTERVAL_SECONDS` e recomeça

Isso permite deixar o scraper rodando continuamente para capturar novos vídeos de canais monitorados.

---

## Estrutura dos dados coletados

```
data/
├── state.json                         # controle interno: quais vídeos já foram coletados
└── channels/
    └── {channel_id}/
        ├── channel.json               # metadados do canal
        └── videos/
            └── {video_id}/
                ├── video.json         # metadados do vídeo
                └── comments.json      # comentários e respostas
```

### `channel.json`

Para canais de `channels.txt` (coleta completa via API):

```json
{
  "channel_id": "UC5rO0aTewMfpk2UKKPTLBYw",
  "channel_title": "Canal Foco",
  "description": "...",
  "country": "BR",
  "published_at": "2023-01-15T12:00:00Z",
  "subscriber_count": "450000",
  "video_count": "312",
  "view_count": "85000000",
  "uploads_playlist_id": "UU5rO0aTewMfpk2UKKPTLBYw"
}
```

Para canais descobertos via `videos.txt` (somente o necessário):

```json
{
  "channel_id": "UC5rO0aTewMfpk2UKKPTLBYw",
  "channel_title": "Canal Foco"
}
```

### `video.json`

```json
{
  "video_id": "2IFCBt4HTd8",
  "video_url": "https://www.youtube.com/watch?v=2IFCBt4HTd8",
  "channel_id": "UC5rO0aTewMfpk2UKKPTLBYw",
  "channel_title": "Canal Foco",
  "video_title": "1 MACHISTA VS 30 FEMINISTAS | FT. GABRIEL BREIER",
  "video_description": "...",
  "published_at": "2026-02-01T21:00:07Z",
  "view_count": "3283213",
  "like_count": "116498",
  "comment_count": "40202"
}
```

### `comments.json`

Lista de comentários. Cada item pode ser um comentário principal (`is_reply: false`) ou uma resposta (`is_reply: true`):

```json
[
  {
    "comment_id": "UgwYYrpmKY_w04BwM6x4AaABAg",
    "video_id": "2IFCBt4HTd8",
    "parent_id": null,
    "is_reply": false,
    "author": "@canalfoco_",
    "text": "Qual deveria ser o próximo 1vs30?",
    "text_raw": "Qual deveria ser o próximo 1vs30?",
    "like_count": 831,
    "published_at": "2026-02-09T22:35:50Z",
    "updated_at": "2026-02-09T22:35:50Z"
  },
  {
    "comment_id": "UgwYYrpmKY_w04BwM6x4AaABAg.AT0yb0FLQ",
    "video_id": "2IFCBt4HTd8",
    "parent_id": "UgwYYrpmKY_w04BwM6x4AaABAg",
    "is_reply": true,
    "author": "@usuario123",
    "text": "1 drag vs 30 redpills",
    "text_raw": "1 drag vs 30 redpills",
    "like_count": 0,
    "published_at": "2026-02-09T22:38:11Z",
    "updated_at": "2026-02-09T22:38:11Z"
  }
]
```

| Campo | Descrição |
|---|---|
| `comment_id` | ID único do comentário na API do YouTube |
| `parent_id` | ID do comentário pai (nulo se for comentário principal) |
| `is_reply` | `true` se for resposta a outro comentário |
| `text` | Texto normalizado (HTML decodificado, espaços limpos) |
| `text_raw` | Texto exatamente como retornado pela API |

---

## Logs

Cada execução grava um arquivo de log diário em `logs/scraper_YYYY-MM-DD.log`:

```
2026-06-30 14:23:01 | INFO     | === YOUTUBE SCRAPER — Modo: contínuo/incremental ===
2026-06-30 14:23:01 | INFO     | --- Carregando alvos ---
2026-06-30 14:23:01 | INFO     | Links de vídeos: 49
2026-06-30 14:23:02 | INFO     | 2IFCBt4HTd8: 40202 comentários coletados
2026-06-30 14:23:03 | WARNING  | Limite da API atingido. Alternando para outra key.
2026-06-30 14:23:04 | ERROR    | Erro ao coletar comentários do vídeo c2mkjP9NAM8
2026-06-30 14:25:00 | INFO     | Resumo — processados: 47 | pulados: 0 | erros: 1 | comentários: 143286
```

O terminal exibe o mesmo conteúdo em formato Rich (colorido). O arquivo de log é texto puro, sem cores.

---

## Estrutura do código

```
youtube_scraper/
│
├── main.py                  # entry point
├── config.py                # lê .env e define paths globais
├── youtube_client.py        # YouTubeClientPool + detecção de erro de quota
├── storage.py               # leitura e escrita de arquivos JSON
├── migrate.py               # migra dados do formato legado para a hierarquia atual
│
├── targets/
│   ├── channels.txt         # channel IDs a monitorar
│   └── videos.txt           # URLs de vídeos individuais
│
├── utils/
│   ├── console.py           # output Rich (terminal) + logging (arquivo) unificados
│   ├── run_stats.py         # dataclass com contadores de uma execução
│   ├── text.py              # normalização de texto de comentários
│   └── url.py               # extração de video_id de URLs
│
├── services/                # chamadas à YouTube Data API v3
│   ├── channel_service.py   # metadados e lista de vídeos de um canal
│   ├── video_service.py     # metadados de um vídeo
│   └── comment_service.py   # comentários e respostas de um vídeo
│
├── repositories/            # persistência em disco
│   ├── paths.py             # funções auxiliares de path (channel_dir, video_dir)
│   ├── channel_repository.py
│   ├── video_repository.py
│   ├── comment_repository.py
│   └── state_repository.py  # controle de vídeos já processados (com cache em memória)
│
└── pipeline/                # orquestração da coleta
    ├── collector.py         # descobre todos os video_ids alvo
    ├── processor.py         # processa um vídeo individual + fallback de quota
    └── runner.py            # loop principal (run_once + run_scraper_pipeline)
```
