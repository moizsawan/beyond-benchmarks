# Survey Data: Beyond Benchmarks

## Overview

This directory contains anonymized survey data from the study "Beyond Benchmarks: How Users Evaluate AI Chat Assistants" (N=388, late 2025).

## Files

| File | Wave | Rows | Columns | Description |
|------|------|------|---------|-------------|
| `wave2_cleaned.csv` | 2 | 237 | 217 | Primary analytic sample (all quantitative analyses) |
| `wave1_cleaned.csv` | 1 | 151 | 165 | Supplementary sample (qualitative responses only) |

## Privacy & Cleaning

The following columns were **removed** to protect respondent privacy:

- IP addresses
- Timestamps (start, end, recorded date)
- Qualtrics response IDs
- Recipient names and emails
- GPS coordinates (latitude/longitude)
- Distribution channel and language metadata
- Free-text "Other" fields for occupation and model selection

All remaining data are structured survey responses (Likert scales, categorical selections, and open-ended responses about AI tools).

## CSV Structure

Row 1 contains the question text for each column. Row 2 onward is response data.

### Key Column Reference

**Demographics:**
- `QID2` — Occupation category
- `QID3` — Country of residence
- `QID4` — AI chat usage frequency

**Model Selection (check all that apply):**
- `QID5_1` through `QID5_7` — Model usage (1=ChatGPT, 2=Claude, 3=Gemini, 4=Llama, 5=Grok, 6=DeepSeek, 7=Mistral)
- `QID5_8` — "Other" model (wave 2 only)

**Per-Model Evaluation Blocks:**

Each model has a block prefixed by its ID number (e.g., `1_` = ChatGPT, `2_` = Claude). Within each block:

| Column Pattern | Content |
|---------------|---------|
| `{id}_` | Was this your first AI chat tool? (Yes/No) |
| `{id}_.1` | Usage tenure |
| `{id}_QID14_1` | Overall satisfaction (Likert text) |
| `{id}_QID22_1` to `{id}_QID22_9` | Adoption drivers (1-5 scale) |
| `{id}_QID25_1` to `{id}_QID25_6` | Use case performance (1-5 scale) |
| `{id}__1` to `{id}__4` | Subscription plan |
| `{id}_.2` | Price sensitivity response |
| `{id}_.3` | Switched from another model? (Yes/No) |
| `{id}_.4` | Which model did you switch from? |

**Adoption Drivers (QID22_1 to QID22_9):**
1. Value for money
2. Answer quality
3. Multimodal capability
4. UI/UX design
5. Response speed
6. Work-task suitability
7. Word-of-mouth recommendation
8. Promotional discount
9. Censorship/content policy alignment

**Use Cases (QID25_1 to QID25_6):**
1. Content creation
2. Communication assistance
3. Learning and research
4. Technical and analytical tasks
5. Productivity and automation
6. Business and professional use

**Open-Ended Responses:**
- `QID15` — What does your preferred model do especially well?
- `QID16` — Most frustrating limitation of AI chat models
- `QID17` — Most desired feature

**Survey Metadata:**
- `Progress` — Completion percentage
- `Duration (in seconds)` — Time to complete
- `Finished` — Whether the respondent completed the survey

## Model ID Mapping

| Prefix | Platform |
|--------|----------|
| `1_` | ChatGPT |
| `2_` | Claude |
| `3_` | Gemini |
| `4_` | Llama |
| `5_` | Grok |
| `6_` | DeepSeek |
| `7_` | Mistral |
| `8_` | Other |

## Satisfaction Likert Scale

The satisfaction column (`{id}_QID14_1`) uses text labels:

| Label | Numeric |
|-------|---------|
| Extremely dissatisfied | 1 |
| Somewhat dissatisfied | 2 |
| Neither satisfied nor dissatisfied | 3 |
| Somewhat satisfied | 4 |
| Extremely satisfied | 5 |

## Differences Between Waves

Wave 1 used a 5-model checklist (ChatGPT, Claude, Gemini, Llama, Grok) plus "Other." Wave 2 added DeepSeek and Mistral as explicit options. All quantitative per-model analyses in the paper use Wave 2 only. Qualitative responses (QID16, QID17) are combined across both waves.

## Citation

If you use this data, please cite:

```bibtex
@article{awan2026beyond,
  title={Beyond Benchmarks: How Users Evaluate AI Chat Assistants},
  author={Awan, Moiz Sadiq and Munaf, Muhammad Salman and Noor, Muhammad Haris},
  year={2026}
}
```
