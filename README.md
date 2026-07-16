# ABC da Amazônia - dados

Este repositório concentra os arquivos YAML que alimentam a ABC da Amazônia Wiki. Cada episódio fica em `src/episodios/` e o material publicado é gerado a partir desses arquivos.

## O que tem aqui

- Episódios em YAML em `src/episodios/`.
- Lista de episódios mapeados em `src/mapeamento/episodios_mapeados.txt`.
- Scripts de build e validação em `src/scripts/`.
- Testes automatizados em `tests/`.

## Como contribuir

O passo a passo para criar ou editar episódios está em [docs/contribuicao.md](docs/contribuicao.md).

## Validação

Antes de abrir um Pull Request, rode os testes e o build do projeto para validar suas alterações e evitar PRs recusados.

```bash
pytest
python src/scripts/build.py
```

## Estrutura

Cada episódio é descrito em um arquivo YAML com metadados e transcrição. O schema e as regras de validação ficam em `src/schema.py`.
