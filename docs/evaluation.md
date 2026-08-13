# Answer Quality & Benchmark Evaluation Methodology

## 1. Evaluation Objectives

The Evaluation component in IntelliQA quantitatively measures answer accuracy, precision, recall, and F1 score against a ground-truth dataset (`data/sample_questions.csv`).

---

## 2. Evaluation Metrics

### Exact Match (EM)
Checks if the predicted answer string matches the ground-truth answer (case-insensitive substring match).

$$\text{EM} = \begin{cases} 1 & \text{if predicted} = \text{expected} \\ 0 & \text{otherwise} \end{cases}$$

### Token-Level Precision & Recall
Calculated over tokenized non-stopword tokens:

$$\text{Precision} = \frac{|\text{Tokens}_{\text{pred}} \cap \text{Tokens}_{\text{exp}}|}{|\text{Tokens}_{\text{pred}}|}$$

$$\text{Recall} = \frac{|\text{Tokens}_{\text{pred}} \cap \text{Tokens}_{\text{exp}}|}{|\text{Tokens}_{\text{exp}}|}$$

$$\text{F1 Score} = 2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}$$

---

## 3. Sample Questions Benchmark Dataset

The benchmark set (`data/sample_questions.csv`) comprises 25+ questions categorized into:
- **IR Factoid Questions** (Document passage retrieval)
- **Knowledge Base Queries** (Entity-attribute lookup)
- **Dialogue / Follow-Up Questions** (Pronoun coreference)
- **Small Talk / Greetings**
- **Out-of-Domain Questions** (Graceful fallback testing)
