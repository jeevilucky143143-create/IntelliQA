import os
import pandas as pd
import numpy as np
from typing import Dict, List
from core.preprocessing import tokenize

def compute_exact_match(predicted: str, expected: str) -> bool:
    """Check if predicted answer matches expected answer (lowercased & stripped)."""
    p_clean = predicted.strip().lower()
    e_clean = expected.strip().lower()
    return p_clean == e_clean or e_clean in p_clean or p_clean in e_clean

def compute_precision_recall_f1(predicted: str, expected: str) -> Dict[str, float]:
    """Calculate token-level Precision, Recall, and F1 score."""
    p_tokens = tokenize(predicted, remove_stopwords=True)
    e_tokens = tokenize(expected, remove_stopwords=True)

    if not p_tokens or not e_tokens:
        return {'precision': 0.0, 'recall': 0.0, 'f1': 0.0}

    common_tokens = set(p_tokens).intersection(set(e_tokens))
    num_same = len(common_tokens)

    if num_same == 0:
        return {'precision': 0.0, 'recall': 0.0, 'f1': 0.0}

    precision = num_same / len(p_tokens)
    recall = num_same / len(e_tokens)
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        'precision': round(precision, 4),
        'recall': round(recall, 4),
        'f1': round(f1, 4)
    }

class Evaluator:
    """Evaluates system answer quality and computes accuracy metrics across sample questions benchmark."""

    def __init__(self, sample_csv_path: str, ask_function):
        self.sample_csv_path = sample_csv_path
        self.ask_function = ask_function

    def run_evaluation(self) -> Dict:
        """Runs evaluation over sample dataset and returns benchmark report."""
        if not os.path.exists(self.sample_csv_path):
            return {'error': 'Sample questions CSV file not found.'}

        df = pd.read_csv(self.sample_csv_path)
        
        total_questions = len(df)
        results = []
        
        em_count = 0
        precisions = []
        recalls = []
        f1_scores = []
        confidences = []
        
        mode_counts = {'IR': 0, 'KNOWLEDGE': 0, 'DIALOGUE': 0}
        mode_correct = {'IR': 0, 'KNOWLEDGE': 0, 'DIALOGUE': 0}

        for _, row in df.iterrows():
            q = str(row['question'])
            expected = str(row['expected_answer'])
            qa_type = str(row.get('qa_type', 'general')).lower()

            # Execute ask pipeline
            resp = self.ask_function(q)
            pred_answer = resp.get('answer', '')
            actual_mode = resp.get('mode', 'UNKNOWN')
            conf = resp.get('confidence', 0.0)
            
            em = compute_exact_match(pred_answer, expected)
            prf = compute_precision_recall_f1(pred_answer, expected)
            
            if em:
                em_count += 1

            precisions.append(prf['precision'])
            recalls.append(prf['recall'])
            f1_scores.append(prf['f1'])
            confidences.append(conf)

            # Track per-mode performance
            mode_key = actual_mode.upper()
            if mode_key in mode_counts:
                mode_counts[mode_key] += 1
                if em or prf['f1'] > 0.5:
                    mode_correct[mode_key] += 1

            results.append({
                'question': q,
                'expected': expected,
                'predicted': pred_answer,
                'mode': actual_mode,
                'qa_type': qa_type,
                'confidence': conf,
                'exact_match': em,
                'precision': prf['precision'],
                'recall': prf['recall'],
                'f1': prf['f1']
            })

        avg_em = round(em_count / total_questions, 4) if total_questions > 0 else 0.0
        avg_precision = round(float(np.mean(precisions)), 4) if precisions else 0.0
        avg_recall = round(float(np.mean(recalls)), 4) if recalls else 0.0
        avg_f1 = round(float(np.mean(f1_scores)), 4) if f1_scores else 0.0
        avg_confidence = round(float(np.mean(confidences)), 4) if confidences else 0.0

        ir_accuracy = round(mode_correct['IR'] / mode_counts['IR'], 4) if mode_counts['IR'] > 0 else 0.0
        kb_accuracy = round(mode_correct['KNOWLEDGE'] / mode_counts['KNOWLEDGE'], 4) if mode_counts['KNOWLEDGE'] > 0 else 0.0
        dialogue_accuracy = round(mode_correct['DIALOGUE'] / mode_counts['DIALOGUE'], 4) if mode_counts['DIALOGUE'] > 0 else 0.0

        return {
            'summary': {
                'total_questions': total_questions,
                'exact_match_count': em_count,
                'exact_match_ratio': avg_em,
                'precision': avg_precision,
                'recall': avg_recall,
                'f1_score': avg_f1,
                'average_confidence': avg_confidence,
                'ir_accuracy': ir_accuracy,
                'knowledge_accuracy': kb_accuracy,
                'dialogue_accuracy': dialogue_accuracy,
                'mode_distribution': mode_counts
            },
            'details': results
        }
