# Deploy na VPS (Daycoval + Docker)

## O que roda onde

| Componente | Onde |
|------------|------|
| **PostgreSQL + FastAPI** | `docker/docker-compose.yml` (`make up`) |
| **Nginx → Daycoval** | **Host da VPS** (`/etc/nginx/`), não dentro do Compose |

O proxy precisa estar no **host** para o tráfego sair pelo **IP público** liberado pela Daycoval. O Docker publica a API em outra porta (ex.: 8000). Este template usa **8080** no nginx quando a **80** já está ocupada.

O `deploy/nginx-daycoval-sandbox.conf` usa **`resolver` com `ipv6=off`** e `proxy_pass` com variável: assim o upstream é contactado só por **IPv4**. Sem isso, em algumas VPS o nginx pode escolher **IPv6** e falhar (500) enquanto `curl` direto à API funciona.

## Nginx no host

**Importante:** o arquivo em `/etc/nginx/sites-available/daycoval-sandbox` deve conter **apenas** sintaxe nginx (comentários `#` e bloco `server { ... }`). **Nunca** cole comandos `sudo`, `cp`, `git` dentro desse arquivo — isso gera `unknown directive "sudo"`.

Se apareceu esse erro, apague o conteúdo e copie de novo só o arquivo `deploy/nginx-daycoval-sandbox.conf` do repositório (ou cole manualmente o bloco `server` abaixo).

1. Garanta o arquivo no servidor (commit/push no Mac, depois `git pull` na VPS; ou `scp` do arquivo):

   ```bash
   cd ~/temp/hub-banking-platform
   git pull
   sudo cp deploy/nginx-daycoval-sandbox.conf /etc/nginx/sites-available/daycoval-sandbox
   ```

2. Ative o site:

   ```bash
   sudo ln -sf /etc/nginx/sites-available/daycoval-sandbox /etc/nginx/sites-enabled/daycoval-sandbox
   sudo nginx -t && sudo systemctl reload nginx
   ```

3. Se `deploy/` não existir na VPS após `git pull`, faça push do branch no seu Mac ou copie o `.conf` manualmente.

4. Firewall: `sudo ufw allow 8080/tcp` (porta do proxy Daycoval).

5. Na aplicação: `DAYCOVAL_BASE_URL=http://<IP_PUBLICO_DA_VPS>:8080` no `.env` — a porta deve ser a mesma do `listen` do nginx.

6. Peça à Daycoval a liberação desse IP (evitar bloqueio WAF / geo).

## Docker Compose

Ver comentário no topo de `docker/docker-compose.yml`. Subir stack:

```bash
make up
```
