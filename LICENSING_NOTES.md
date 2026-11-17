# Licenciamento e origem dos materiais

Por autorização expressa do autor na finalização do trabalho, o código original do projeto e sua documentação de software são disponibilizados sob MIT, conforme [LICENSE](LICENSE). O escopo é o código próprio em `scripts/` e `configs/`. Essa licença não relicencia modelos, datasets, dados experimentais, llama.cpp, lm-evaluation-harness, bibliotecas ou demais componentes de terceiros. Este documento distingue essas origens; não transfere direitos de terceiros.

## Código do projeto

`scripts/` contém os scripts locais do pipeline, a recuperação retrospectiva e o gerador de figuras. `configs/mmlu_pro_direct_utils.py` e o YAML definem o protocolo local. Esses arquivos foram encontrados no projeto, fora dos clones de terceiros, e constituem o código próprio abrangido pela autorização MIT do autor.

`scripts/verify_public_package.py` e os documentos de empacotamento foram criados nesta preparação. Os demais scripts são cópias dos existentes, com as adaptações explicitadas no relatório e nos diffs. Não foi copiado o código completo do llama.cpp nem do harness.

**Licença aplicada ao código próprio:** MIT. O texto segue a [licença publicada pela Open Source Initiative](https://opensource.org/license/mit), com identificação do autor e do ano e delimitação expressa de escopo. Os avisos de copyright/licença devem ser preservados. O código é fornecido sem garantia. A licença não se estende automaticamente aos materiais externos ou aos dados.

## Resultados próprios e derivados

`analysis/results.csv`, `analysis/validation.csv`, as medidas em `results/processed/`, o manifesto de quantização, os gráficos e os relatórios de conferência registram resultados produzidos pelo experimento. O autor poderá definir separadamente os termos dos resultados numéricos e da documentação; não se atribuiu CC0, CC BY ou MIT a eles automaticamente.

`analysis/mmlu_por_questao_recuperado.csv` contém 120.320 linhas: modelo, quantização, question_id, categoria, chave hash, letra do gabarito, resposta curta do modelo, letra extraída e correção. Não há colunas de enunciado, alternativas ou cadeia de raciocínio. As categorias, os identificadores e os gabaritos derivam do MMLU-Pro; as saídas são gerações dos modelos, limitadas a oito tokens pelo protocolo. Algumas saídas contêm palavras além da letra. Esses campos não devem ser apresentados como integralmente independentes dos dados/modelos de origem.

Os JSONs agregados do harness incluídos contêm métricas, configuração e o código do prompt local, sem registros completos das questões. Os JSONL de amostras dos pilotos contêm textos de questões/alternativas e foram excluídos. O corpus WikiText integral e o Arrow MMLU-Pro também foram excluídos. Os logs pequenos selecionados foram inspecionados e não contêm o corpus ou um conjunto integral de enunciados/alternativas; registram metadados, progresso e resultados, além da resposta ao prompt próprio de validação.

## Materiais externos

| Material | Evidência consultada | Tratamento no pacote |
| --- | --- | --- |
| MMLU-Pro | Cartão **local da revisão usada** declara `license: mit`; SHA-256 do cartão em `docs/dataset_revisions.json`. [Cartão oficial](https://huggingface.co/datasets/TIGER-Lab/MMLU-Pro) | Distribuem-se resultados e campos derivados mínimos, com atribuição a TIGER-Lab/Wang et al. O dataset integral não é incluído. A abertura web da revisão fixa falhou; a identificação histórica vem do cartão cacheado nessa revisão. |
| Código do repositório MMLU-Pro | [LICENSE oficial](https://github.com/TIGER-AI-Lab/MMLU-Pro/blob/main/LICENSE) declara Apache 2.0, na consulta de 17/11/2026 | É um escopo diferente da declaração MIT do cartão do dataset; não unificar as duas licenças nem assumir que uma substitui a outra. Código desse repositório não foi copiado. |
| WikiText | [Cartão na revisão usada](https://huggingface.co/datasets/Salesforce/wikitext/raw/b08601e04326c79dfdd32d625aee71d232d685c3/README.md): front matter indica CC BY-SA 3.0/GFDL; corpo indica CC BY-SA 4.0 | Discrepância registrada, sem resolver por suposição. Texto integral omitido; reprodução baixa a revisão original e conserva metadados/hash. Não aplicar MIT ao corpus. |
| Gemma 3 4B IT | [Cartão do checkpoint](https://huggingface.co/google/gemma-3-4b-it/blob/093f9f388b31de276ce2de164bdc2081324b9767/README.md), licença Gemma e acesso condicionado aos termos | Nenhum peso, GGUF, tokenizador ou arquivo do checkpoint redistribuído. Obtenção pelo usuário no repositório oficial. |
| Qwen3-4B | [Cartão do checkpoint](https://huggingface.co/Qwen/Qwen3-4B/raw/1cfa9a7208912126459214e8b04321603b3df60c/README.md) e LICENSE local: Apache 2.0 | Nenhum peso, GGUF ou arquivo do checkpoint redistribuído. Metadados dos recibos apenas identificam os arquivos. |
| llama.cpp | [LICENSE da revisão usada](https://raw.githubusercontent.com/ggml-org/llama.cpp/1c4729414deba3bcacef6a5614e2ca04d069be3a/LICENSE): MIT | Clone, builds e executáveis excluídos. O usuário obtém a revisão oficial com seus avisos originais. |
| lm-evaluation-harness e dependências | Pacotes externos identificados em requirements e environment | Não são redistribuídos. A instalação e o uso conservam as licenças próprias de cada dependência. |

Os links servem para consulta das condições dos titulares. A seleção conservadora do pacote evita redistribuir textos integrais enquanto documenta as origens. Antes de depositar bancos de respostas ou logs no Zenodo, revisar novamente conteúdo, atribuições e caminhos pessoais. Não foi feito depósito, configurado Git LFS ou inventado DOI.

## Atribuição do dataset derivado

MMLU-Pro: TIGER-Lab; Wang, Yubo et al. *MMLU-Pro: A More Robust and Challenging Multi-Task Language Understanding Benchmark*. NeurIPS, 2024. [Artigo](https://arxiv.org/abs/2406.01574). Dataset usado na revisão `b189ec765aa7ed75c8acfea42df31fdae71f97be`; o cartão dessa revisão declara MIT. A atribuição aos criadores do benchmark deve acompanhar as tabelas derivadas, sem sugerir que os criadores endossaram o experimento.

WikiText: Merity, Stephen; Xiong, Caiming; Bradbury, James; Socher, Richard. *Pointer Sentinel Mixture Models*, 2016. [Artigo](https://arxiv.org/abs/1609.07843). Revisão do corpus identificada no README; nenhum texto integral é distribuído.
