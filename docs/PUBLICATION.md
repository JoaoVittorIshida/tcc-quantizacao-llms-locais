# Versão pública utilizada no TCC

- Repositório público: [tcc-quantizacao-llms-locais](https://github.com/JoaoVittorIshida/tcc-quantizacao-llms-locais).
- Branch principal: `main`.
- Tag preservada: `v1.0.0`.
- Release: [v1.0.0 — Artefatos experimentais utilizados no TCC](https://github.com/JoaoVittorIshida/tcc-quantizacao-llms-locais/releases/tag/v1.0.0).
- Data da versão: 17/11/2026.

A release identifica o commit completo dos artefatos utilizados no trabalho. A tag não deve ser movida para incorporar alterações posteriores. O SHA pode ser consultado no histórico do GitHub ou por `git rev-parse v1.0.0^{commit}` em um clone.

O commit inicial contém somente o pacote público selecionado: código, configurações, resultados preservados e documentação. Não contém modelos, executáveis, caches integrais, arquivos do Codex ou o DOCX/PDF do trabalho. Os arquivos grandes omitidos e as limitações de reconstrução estão documentados no README e em REPO_EXCLUDED.md.

A licença MIT foi aplicada por autorização do autor ao código próprio e à documentação de software, sem relicenciar modelos, datasets, dados experimentais, llama.cpp, lm-evaluation-harness ou bibliotecas. Não foi criado depósito Zenodo nem atribuído DOI.

Na finalização, nenhum script experimental ou configuração foi modificado. As quatro adaptações de empacotamento preexistentes continuam registradas nos diffs. Caminhos de instalação e arquitetura da GPU refletem o ambiente original; adaptações ambientais em uma reprodução são responsabilidade do pesquisador e não devem alterar o protocolo.

A verificação anterior à publicação está em `publication_validation.json`. Os checksums preservam as evidências byte a byte, e `.gitattributes` impede conversão automática de quebras de linha no checkout.
