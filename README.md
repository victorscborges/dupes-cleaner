# dupes-cleaner

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