# Lições de Deploy

Problemas reais encontrados e como foram resolvidos.

---

## 2026-03-29 — Primeiro deploy na VPS (sentinela.klauberfischer.online)

### 1. Conflito de hostname `postgres` na rede proxy do Traefik

**Problema:** O container `servidor` estava conectado em duas redes (`rede_sentinela` + `proxy`). Na rede `proxy` já existiam `supabase_db` e `evolution_postgres`. O Docker DNS resolvia o hostname genérico `postgres` para um desses containers antes de chegar no `sentinela-postgres`, causando `InvalidPasswordError`.

**Solução:** Usar o nome exato do container (`sentinela-postgres`) no `DATABASE_URL` em vez do service name (`postgres`).

```
# Errado
DATABASE_URL=postgresql+asyncpg://sentinela:senha@postgres:5432/sentinela

# Correto
DATABASE_URL=postgresql+asyncpg://sentinela:senha@sentinela-postgres:5432/sentinela
```

**Regra:** Em VPS com múltiplos stacks compartilhando a rede `proxy`, sempre usar o nome do container como hostname — nunca o service name genérico.

---

### 2. `alembic.ini` com URL hardcoded

**Problema:** O `alembic.ini` tinha `sqlalchemy.url = postgresql+asyncpg://sentinela:sentinela@localhost:5432/sentinela`. O Alembic usava essa URL ignorando as variáveis de ambiente, causando falha de conexão nas migrations.

**Solução:** Deixar `sqlalchemy.url =` vazio no `.ini`. O `env.py` já sobrescreve via `obter_configuracao().database_url`.

---

### 3. Volume do postgres inicializado com senha errada

**Problema:** Nas primeiras tentativas o volume foi criado com senha incorreta (placeholder `SUA_SENHA_ATUAL`). O postgres não muda a senha de um volume já existente — ele ignora o `POSTGRES_PASSWORD` se o volume já tiver dados.

**Solução:** `docker compose down -v && docker volume rm <nome_do_volume>` para recriar do zero com a senha correta.

**Regra:** Sempre preencher o `.env.prod` corretamente **antes** do primeiro `up`. Qualquer mudança de senha exige recriar o volume.

---

### 4. Senha com caracteres especiais na URL

**Problema:** A senha `Klaubeer@2577` contém `@`, que é o separador de credenciais na URL. O parser interpretava `Klaubeer` como senha e `2577` como host, causando `Name or service not known`.

**Solução:** Ou escapar o caractere como `%40` (`Klaubeer%402577`), ou usar uma senha sem caracteres especiais (`@`, `:`, `/`, `?`, `#`).

**Regra:** Senhas em URLs de banco devem evitar `@ : / ? # [ ] @`. Se necessário, usar percent-encoding.

---

### 5. Healthcheck do postgres com `pg_isready` é insuficiente

**Problema:** O `pg_isready` retorna "healthy" assim que o processo aceita conexões TCP, mas antes de o usuário/banco serem criados. O container `servidor` subia imediatamente e falhava na autenticação.

**Solução:** Trocar o healthcheck para usar `psql` com autenticação real:

```yaml
healthcheck:
  test: ["CMD-SHELL", "PGPASSWORD=$$POSTGRES_PASSWORD psql -h 127.0.0.1 -U $$POSTGRES_USER -d $$POSTGRES_DB -c 'SELECT 1' -q 2>/dev/null | grep -q 1 || exit 1"]
  start_period: 15s
  retries: 10
```

---

### 6. `docker compose restart` não relê o `.env`

**Problema:** Após editar o `.env.prod`, `restart` não recria o container — ele apenas para e inicia novamente com as mesmas variáveis de ambiente já injetadas.

**Solução:** Para que mudanças no `.env` surtam efeito, sempre usar `down` + `up`:

```bash
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d
```

---

### 7. Traefik duplicado na VPS

**Situação:** Havia duas pastas (`infra/infra/traefik` e `infra-klauberfischer-online/infra/traefik`). Apenas o primeiro estava ativo.

**Como identificar qual está rodando:**
```bash
docker inspect traefik | grep "com.docker.compose.project.working_dir"
```
