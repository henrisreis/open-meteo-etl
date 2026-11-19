# Open Meteo ETL | API, Python, Docker, PostgreSQL

## 1. Visão geral e arquitetura

Este projeto consulta as condições meteorológicas atuais da API pública Open-Meteo para uma localização fixa em Brasília e grava cada execução em uma tabela PostgreSQL. O objetivo é manter snapshots simples de temperatura, umidade relativa e velocidade do vento para consulta posterior.

O escopo implementado é um ETL local e síncrono.

### Fluxo End-to-End

```text
Open-Meteo Forecast API
  -> extração HTTP (requests; coordenadas e fuso fixos)
  -> transformação em memória (pandas; nomes e data/hora)
  -> carga (psycopg2; CREATE TABLE IF NOT EXISTS + INSERT)
  -> PostgreSQL 16 (tabela dados_clima)
  -> consulta SQL por ferramentas cliente PostgreSQL
```

### Tecnologias

| Tecnologia | Uso |
| --- | --- |
| Python 3.10+ | Implementação e execução do pipeline. |
| requests | Requisição HTTP à API Open-Meteo. |
| pandas | Conversão dos dados extraídos em DataFrame e parsing da data/hora. |
| psycopg2 | Conexão e inserção no PostgreSQL. |
| python-dotenv | Leitura das configurações de conexão em `config/.env`. |
| PostgreSQL 16 | Persistência dos snapshots meteorológicos. |
| Docker Compose | Inicialização local do PostgreSQL com volume persistente. |
| uv | Gerenciamento do ambiente e dependências do projeto. |

## 2. Fontes de dados e contratos

### Fonte implementada

| Origem | Recurso | Parâmetros | Dados consumidos |
| --- | --- | --- | --- |
| Open-Meteo | `GET https://api.open-meteo.com/v1/forecast` | `latitude=-15.7939`, `longitude=-47.8828`, `timezone=America/Sao_Paulo`, `current=temperature_2m,relative_humidity_2m,wind_speed_10m` | Latitude e longitude retornadas pela API; horário e três variáveis meteorológicas. |

A API deve responder com sucesso e com as chaves esperadas. A extração chama `raise_for_status()` para respostas HTTP de erro e acessa diretamente as chaves do JSON.

Campos de origem usados:

| Campo da API | Tipo esperado | Unidade padrão da API | Uso no destino |
| --- | --- | --- | --- |
| `latitude` | Numérico | Graus decimais | `latitude` |
| `longitude` | Numérico | Graus decimais | `longitude` |
| `current.time` | Texto ISO 8601 | Data/hora local solicitada | `data_hora` |
| `current.temperature_2m` | Numérico | °C | `temperatura` |
| `current.relative_humidity_2m` | Numérico | % | `umidade` |
| `current.wind_speed_10m` | Numérico | km/h | `velocidade_vento` |

## 3. Pipeline e transformações (ETL)

1. **Extração:** faz uma requisição GET para o endpoint de previsão atual, usando as coordenadas e o fuso definidos no ponto de entrada. A resposta é convertida em JSON e os campos de localização e `current` são reunidos em um dicionário.
2. **Transformação:** cria um DataFrame, renomeia `time` para `data_hora`, `temperature_2m` para `temperatura`, `relative_humidity_2m` para `umidade` e `wind_speed_10m` para `velocidade_vento`. `data_hora` é convertida com `pandas.to_datetime`.
3. **Carga:** cria `dados_clima` se ela ainda não existir e insere os registros do DataFrame. A operação usa a transação do contexto de conexão do psycopg2.

### Regras e comportamento atuais

- Cada execução insere uma nova linha;
- O horário é armazenado em uma coluna `TIMESTAMP` sem fuso. A API recebe `America/Sao_Paulo`.

## 4. Modelo de dados e dicionário de dados

O modelo atual é uma tabela plana de snapshots. Para o escopo reduzido do projeto, ela representa uma observação meteorológica por linha.

### Tabela `dados_clima`

| Coluna | Tipo PostgreSQL | Nulidade | Descrição/regra |
| --- | --- | --- | --- |
| `data_hora` | `TIMESTAMP` | Sim | Horário retornado pela API após parsing. Sem timezone e sem normalização explícita. |
| `latitude` | `DECIMAL(10,8)` | Sim | Latitude retornada pela API, em graus decimais. |
| `longitude` | `DECIMAL(11,8)` | Sim | Longitude retornada pela API, em graus decimais. |
| `temperatura` | `DECIMAL(5,2)` | Sim | Temperatura a 2 m, na unidade padrão da API (°C). |
| `umidade` | `DECIMAL(5,2)` | Sim | Umidade relativa a 2 m, em percentual. |
| `velocidade_vento` | `DECIMAL(6,2)` | Sim | Velocidade do vento a 10 m, na unidade padrão da API (km/h). |

## 5. Operação, monitoramento e alertas

### Pré-requisitos

- Python 3.10 ou superior e `uv`.
- Docker com Docker Compose.

### Configuração local

O Compose inicia PostgreSQL 16 com banco `pgdb`, usuário `pguser` e senha `pgpassword`, publicado na porta `5432`. Esses valores são apenas para desenvolvimento local; não os reutilize em ambientes compartilhados ou produtivos.

Crie `config/.env` (o arquivo não deve ser versionado) com os parâmetros de conexão:

```dotenv
DB_HOST=localhost
DB_PORT=5432
DB_NAME=pgdb
DB_USER=pguser
DB_PASSWORD=pgpassword
```

Se as credenciais ou a porta do serviço Compose forem alteradas, atualize também esse arquivo. Quando o pipeline for executado fora do host local, `DB_HOST` deve apontar para um endereço alcançável pelo processo.

### Execução manual

Na raiz do repositório:

```bash
docker compose up -d postgres
uv sync
uv run python main.py
```

O comando Python carrega `config/.env`, executa extração, transformação e carga uma vez e encerra. Para executar novamente, rode `uv run python main.py` outra vez; cada execução adiciona uma linha. O volume Docker `postgres_data` mantém os dados entre reinicializações do container.

Para conferir os dados:

```bash
docker compose exec postgres psql -U pguser -d pgdb \
  -c "SELECT * FROM dados_clima ORDER BY data_hora DESC LIMIT 10;"
```
