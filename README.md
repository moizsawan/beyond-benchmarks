# Beyond Benchmarks: How Users Evaluate AI Chat Assistants

A cross-platform survey study examining user satisfaction, adoption motivations, use case performance, and qualitative frustrations across seven major AI chat platforms: ChatGPT, Claude, Gemini, DeepSeek, Grok, Mistral, and Llama.

## Key Findings

- **Satisfaction convergence:** The top three platforms (Claude, ChatGPT, DeepSeek) receive statistically indistinguishable satisfaction ratings despite vast resource asymmetries
- **Pervasive multi-homing:** 82.4% of users use two or more platforms simultaneously
- **Platform specialization:** Each platform attracts users for distinct reasons (UI/UX for ChatGPT, answer quality for Claude, word-of-mouth for DeepSeek)
- **First-mover anchoring:** Users who adopted ChatGPT as their first AI tool rate satisfaction 1.34 points higher than those who arrived from a competitor (p < 0.001)
- **Hallucination-censorship tradeoff:** The two most common frustrations represent opposing engineering constraints

## Repository Structure

```
├── README.md
├── requirements.txt
├── LICENSE
├── .gitignore
├── data/
│   ├── README.md              # Column reference and codebook
│   ├── wave2_cleaned.csv      # Wave 2 (n=237), primary analytic sample
│   └── wave1_cleaned.csv      # Wave 1 (n=151), qualitative responses only
├── src/
│   ├── utils.py               # Data loading and shared utilities
│   ├── analysis.py            # All statistical analyses reported in the paper
│   └── figures.py             # All 15 figures
├── figures/                    # Generated figure PDFs
└── paper/
    ├── paper.tex              # LaTeX manuscript
    └── *.pdf                  # Figure files for compilation
```

## Setup

```bash
pip install -r requirements.txt
```

## Data

Anonymized survey data is included in `data/`. The following personally identifiable information has been removed: IP addresses, timestamps, response IDs, recipient names/emails, GPS coordinates, and free-text "Other" fields. See `data/README.md` for the full column reference and codebook.

## Reproducing the Analysis

### Run all statistical analyses

```bash
python src/analysis.py
```

This prints every statistic reported in the paper: satisfaction means, Kruskal-Wallis tests, post-hoc comparisons, adoption drivers, use case ratings, switching rates, subgroup analyses, Cronbach's alphas, and qualitative theme counts.

### Generate all figures

```bash
python src/figures.py
```

This produces `fig1.pdf` through `fig15.pdf` in the `figures/` directory.

### Compile the paper

```bash
cd paper/
pdflatex paper.tex && pdflatex paper.tex
```

## Survey Details

- **N = 388** total responses across two waves
- **Platforms:** ChatGPT, Claude, Gemini, DeepSeek, Grok, Mistral, Llama
- **Collection period:** October 14, 2025 to January 10, 2026
- **Distribution:** Reddit AI/ML communities and professional networks
- **Instrument:** Within-subjects design with identical evaluation blocks per platform

## Citation

```bibtex
@article{awan2025beyond,
  title={Beyond Benchmarks: How Users Evaluate AI Chat Assistants},
  author={Awan, Moiz Sadiq and Munaf, Muhammad Salman and Noor, Muhammad Haris},
  year={2025}
}
```

## License

MIT License. See [LICENSE](LICENSE) for details.
