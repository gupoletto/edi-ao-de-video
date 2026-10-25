# Upload automático dos 5 Shorts (Fun Stuff)

O script `upload_shorts.py` sobe os vídeos pela API oficial do YouTube, já com título, descrição, tags e categoria. Cada um fica **agendado** para virar público sozinho, um por dia, às **15h de Brasília** (18:00 UTC):

| Data | Vídeo |
|---|---|
| seg 26/10 | Physics Simulations |
| ter 27/10 | Lava |
| qua 28/10 | Math Patterns |
| qui 29/10 | Ice |
| sex 30/10 | Factory |

Para mudar datas, títulos ou descrições, edite o `videos.json` antes de rodar.

---

## Passo 1 — Criar a credencial da API (uma vez só, ~10 min)

1. Acesse https://console.cloud.google.com/ com a conta Google dona do canal Fun Stuff.
2. Crie um projeto (ex.: "Fun Stuff Uploader").
3. Em **APIs e serviços → Biblioteca**, procure **YouTube Data API v3** e clique em **Ativar**.
4. Em **APIs e serviços → Tela de consentimento OAuth** (ou "Google Auth Platform"):
   - Tipo de usuário: **Externo**.
   - Preencha nome do app e seu e-mail.
   - Em **Usuários de teste**, adicione o seu e-mail (o da conta do canal).
5. Em **APIs e serviços → Credenciais → Criar credenciais → ID do cliente OAuth**:
   - Tipo de aplicativo: **App para computador** (Desktop app).
   - Baixe o JSON, renomeie para **`client_secret.json`** e coloque nesta pasta.

## Passo 2 — Instalar (uma vez só)

Precisa de Python 3 instalado. No terminal, dentro desta pasta:

```
pip install google-api-python-client google-auth-oauthlib
```

## Passo 3 — Rodar

```
python upload_shorts.py --dry-run
python upload_shorts.py
```

- O `--dry-run` só confere se está tudo certo; não envia nada.
- Na primeira vez abre o navegador para você entrar na conta e escolher o canal **Fun Stuff**.
- Se aparecer "O Google não verificou este app": clique em **Avançado → Acessar (não seguro)**. O aviso aparece porque o app é seu e só você usa.
- O login fica salvo em `token.json`. Não compartilhe esse arquivo.
- Se a internet cair no meio, rode de novo: o que já subiu fica registrado em `uploaded.json` e é pulado.

## Sobre os arquivos de vídeo

- `physics_simulations.mp4` e `math_patterns.mp4` já estão nesta pasta.
- `lava.mp4`, `ice.mp4` e `factory.mp4` são baixados automaticamente pelo script, **mas os links expiram hoje por volta das 2h da manhã**. Se rodar depois disso, baixe os 3 antes e coloque nesta pasta com esses nomes.

## O que fazer à mão depois

- **Comentário fixado:** a API não fixa comentários. Os textos sugeridos estão no `kit_upload_5_shorts.md`.
- Confira no YouTube Studio: cada vídeo aparece como "Agendado" com a data acima.
