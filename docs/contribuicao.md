# ABC da Amazônia - dados

Este repositório reúne os arquivos YAML que alimentam o acervo da ABC da Amazônia Wiki. Cada episódio fica em um arquivo próprio dentro de `src/episodios/`, e o dataset final é gerado a partir desses arquivos.

## Como contribuir

Se você encontrou um episódio novo, uma transcrição melhor ou uma correção verificável, a contribuição normalmente segue este fluxo:

1. Faça um clone do repositório.
2. Crie ou edite um arquivo YAML de episódio.
3. Abra um Pull Request a partir de uma branch nova.
4. Aguarde a revisão. Depois da aprovação, o pipeline atualiza o conjunto de dados usado pela Wiki.

## Estrutura de um episódio

Cada episódio é descrito em YAML e deve seguir a estrutura abaixo:

```yaml
titulo: Pato no Tucupi
slug: pato-no-tucupi
ano: 2003
status: completo
versao: 1
ativo: true
videos:
    - tipo: youtube
        duracao: 59
        url: https://www.youtube.com/watch?v=LxhabQqYJEA
        transcricao: |
            ABC da Amazônia, Pato no Tucupi.
            Comer pato é coisa comum no Pará, e o pato no tucupi está sempre na mesa em dias de festa.
            ...
```

Campos obrigatórios:

- `titulo`: título do episódio.
- `slug`: identificador estável em kebab-case, com letras minúsculas, números e hífen.
- `ano`: ano de exibição.
- `status`: `completo`, `parcial`, `perdido` ou `incompleto`.
- `versao`: versão do arquivo, começando em `1`.
- `ativo`: `true` para episódios que devem entrar no build.
- `videos`: lista de fontes do episódio.

Cada item em `videos` deve conter:

- `tipo`: tipo da fonte, hoje documentado como `youtube`.
- `duracao`: duração em segundos.
- `url`: link do vídeo.
- `transcricao`: transcrição completa do vídeo, como exatamente narrada.

## Como adicionar um episódio

1. Escolha um `slug` estável para o episódio.
2. Crie um novo arquivo em `src/episodios/` seguindo o padrão `slug-versao.yaml`, por exemplo `pato-no-tucupi-1.yaml`.
3. Preencha os metadados e a transcrição completa.
4. Se houver mais de um vídeo da mesma obra, liste todos no campo `videos`.
5. Marque `ativo: true` quando o episódio já puder entrar no conjunto principal.

### Regras importantes

- Use `slug` em kebab-case e mantenha-o estável (preferencialmente o título oficial do episódio).
- Não altere a transcrição além do que for verificável.
- Prefira corrigir apenas informações comprovadas por fonte.
- Episódios com status `incompleto` ou `perdido` podem ter `videos: null`; nos demais casos, a lista de vídeos deve existir.
- O arquivo YAML precisa terminar com o mesmo slug e a versão, por exemplo `pato-no-tucupi-1.yaml`.

## Como editar um episódio existente

Edite apenas o arquivo correspondente em `src/episodios/`.

- Para corrigir metadados, ajuste o campo necessário sem alterar o restante sem motivo.
- Para corrigir transcrição, mantenha a narração fiel e faça mudanças somente quando houver base verificável.
- Se a alteração for significativa, considere aumentar a `versao` e atualizar o nome do arquivo para refletir a nova versão.
- Se o episódio deixar de ser publicado, altere `ativo` apenas quando isso fizer sentido para o build.

## Vídeos e fontes

O projeto coleta, por enquanto, apenas episódios com vídeos hospedados no YouTube.

- Liste quantas fontes de vídeo encontrar para o mesmo episódio.
- Cada vídeo deve ter sua própria transcrição.
- Links não devem conter credenciais.
- Caso você encontre um episódio em outra plataforma que não o youtube, adicione-o à lista de episódios mapeados em `src/mapeamento/episodios_mapeados.txt` se ele ainda não estiver lá e no comentário do Pull Request, informe onde a nova fonte foi encontrada para revisão manual.

## Boas práticas

- Utilize slugs estáveis e em kebab-case.
- Mantenha a transcrição exatamente como narrada.
- Corrija apenas informações verificáveis.
- Evite alterar episódios sem necessidade.
- Um Pull Request pequeno é mais fácil de revisar.

## Validar antes do PR

Depois de editar ou criar episódios, rode a validação do projeto:

```bash
pytest
python src/scripts/build.py
```

O teste verifica a estrutura e a segurança dos arquivos YAML, e o build gera os artefatos em `src/dist/`.

## Estrutura do repositório

- `src/episodios/`: arquivos YAML dos episódios.
- `src/mapeamento/episodios_mapeados.txt`: lista de episódios mapeados.
- `src/scripts/build.py`: gera os dados finais.
- `src/scripts/check_lista.py`: gera o relatório de episódios mapeados.
- `tests/`: testes de validação dos episódios.

## Sobre o status de completo

Um episódio marcado como `completo` não significa necessariamente que ele esteja 100% correto. Erros podem ser corrigidos a qualquer momento quando surgirem novas evidências.

## Pull Request

Se você já usa Git e GitHub, o processo costuma ser rápido:

1. Crie uma branch nova.
2. Faça a alteração no YAML.
3. Rode os testes.
4. Abra o Pull Request.

Depois da aprovação, o GitHub lê a contribuição automaticamente e o crédito aparece na página de colaboradores.
