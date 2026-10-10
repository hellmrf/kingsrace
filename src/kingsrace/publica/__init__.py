"""Páginas públicas do projeto, servidas pelo GitHub Pages (decisão D12).

Ordem: pipeline do DVC → notebook (análise) → público. Cada `<página>.py` aqui só lê
saídas do DVC (`data/processed/`, `resultados/`) e grava os dados da página em `site/dados/`;
`build.py` junta templates, estático e dados em `_site/`.
"""
