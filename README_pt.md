# Academic Image Optimizer

Uma ferramenta de linha de comando (`CLI`) leve e inteligente em Python, projetada especificamente para otimizar figuras, gráficos e diagramas para artigos acadêmicos.

Muitos periódicos e repositórios de pre-prints (como arXiv) impõem limites rigorosos de tamanho de arquivo nas submissões em PDF. Figuras de alta resolução geradas por `matplotlib`, `seaborn` ou exportadas de ferramentas de design geralmente possuem dimensões desnecessariamente grandes, fundos transparentes (que podem causar problemas de renderização no PDF) ou canais de cores não otimizados.

Este script resolve esses problemas através do redimensionamento inteligente de dimensões extremamente altas usando o filtro de reamostragem de alta qualidade `LANCZOS`, transformando canais de transparência alfa em fundos brancos sólidos (para evitar artefatos de fundo preto na conversão LaTeX/PDF) e aplicando uma redução de tamanho com ou sem perda de dados adequada para impressão e leitura na web.

## Funcionalidades
- **Filtro Inteligente:** Otimiza apenas as imagens que ultrapassam um certo limite de dimensão ou tamanho de arquivo, pulando os recursos já otimizados.
- **Padrão Acadêmico:** Remove canais alfa (transparência) e os substitui por um fundo branco sólido, prevenindo erros de cores invertidas ao compilar PDFs no LaTeX.
- **Reamostragem de Alta Qualidade:** Utiliza o algoritmo de redução `LANCZOS` para preservar linhas finas, textos e pontos de dados nos gráficos.
- **Processamento em Lote:** Processa diretórios inteiros de imagens `.png`, `.jpg` e `.jpeg` de forma segura.

## Requisitos

A única dependência externa é a biblioteca Python Imaging Library (`Pillow`).

```bash
pip install Pillow
```

## Como Usar

Você pode invocar o script diretamente da linha de comando, informando um diretório de entrada.

```bash
python optimize_images.py -i <caminho_do_diretorio_de_entrada>
```

### Opções

| Argumento | Atalho | Padrão | Descrição |
| :--- | :--- | :--- | :--- |
| `--input` | `-i` | **Obrigatório** | O diretório fonte contendo as suas imagens. |
| `--output` | `-o` | `<input_dir>` | O diretório de destino para as imagens otimizadas. Se omitido, o script sobrescreverá os arquivos originais. |
| `--max-dim` | | `1600` | A largura ou altura máxima permitida (em pixels). Se uma imagem ultrapassar isso, será redimensionada proporcionalmente. |
| `--max-size-kb` | | `200` | Tamanho mínimo do arquivo (em KB) para acionar a otimização. Imagens menores do que isso são puladas para economizar tempo de processamento. |

### Exemplos Práticos

**1. Otimização Básica (Sobrescrever Originais)**
Perfeito para fazer uma varredura rápida na sua pasta `figures/` do LaTeX antes da submissão.
```bash
python optimize_images.py -i ./figures
```

**2. Salvar em uma Pasta Separada**
Se você deseja preservar as imagens originais em resolução nativa e exportar as versões web/PDF para uma pasta `build/`.
```bash
python optimize_images.py -i ./raw_figures -o ./optimized_figures
```

**3. Redução de Tamanho Agressiva**
Para portais de submissão extremamente rigorosos, force uma dimensão máxima de 1000px e comprima tudo que ultrapassar 100 KB.
```bash
python optimize_images.py -i ./figures --max-dim 1000 --max-size-kb 100
```

## Como Funciona nos Bastidores
1. O script varre de forma recursiva todos os arquivos `.png`, `.jpg` e `.jpeg` na pasta de entrada.
2. Ele faz a leitura dos metadados. Se a `largura > max-dim`, `altura > max-dim` ou `tamanho > max-size-kb`, ele carrega o array da imagem na memória RAM.
3. A imagem tem sua escala reduzida utilizando a ferramenta `Image.Resampling.LANCZOS` do Pillow.
4. O algoritmo procura pelo modo `RGBA` ou transparente `P`. Se for encontrado, ele cria um novo canvas branco limpo `RGB` e cola a imagem utilizando o seu próprio canal alfa como máscara.
5. Finalmente, ele salva a matriz gerada com a otimização profunda habilitada (`optimize=True` para PNGs, `quality=85` para JPEGs).
