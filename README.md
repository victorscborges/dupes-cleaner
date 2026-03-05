# dupes-cleaner

![Release](https://img.shields.io/github/v/release/victorscborges/dupes-cleaner)
![License](https://img.shields.io/github/license/victorscborges/dupes-cleaner)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Last commit](https://img.shields.io/github/last-commit/victorscborges/dupes-cleaner)

Script em Python para varrer uma pasta raiz (com subpastas), encontrar arquivos duplicados por conteúdo, **manter sempre o mais antigo** e **apagar os demais automaticamente**, mostrando o progresso no console.

## O que ele faz
- Varre recursivamente todas as subpastas
- Otimiza por tamanho antes de hashear (mais rápido)
- Hash SHA-256 em blocos (não estoura memória)
- Mantém o arquivo mais antigo:
  - Windows: usa data de criação
  - Linux/macOS: usa data de modificação
- Apaga duplicados sem pedir confirmação
- Mostra logs no console do que está acontecendo

## Requisitos
- Python 3.10+

## Como usar
```bash
python dupes_cleaner.py