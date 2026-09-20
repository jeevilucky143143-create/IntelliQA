import re
from typing import Dict, List, Optional, Tuple
from core.preprocessing import tokenize, STOPWORDS

class QuestionType:
    PERCENTAGE = "PERCENTAGE"
    MARKS = "MARKS"
    CGPA = "CGPA"
    GPA = "GPA"
    YEAR = "YEAR"
    DATE = "DATE"
    AGE = "AGE"
    PHONE = "PHONE"
    EMAIL = "EMAIL"
    SCORE = "SCORE"
    RANK = "RANK"
    DURATION = "DURATION"
    LOCATION = "LOCATION"
    NAME = "NAME"
    ORGANIZATION = "ORGANIZATION"
    COLLEGE = "COLLEGE"
    DEGREE = "DEGREE"
    QUALIFICATION = "QUALIFICATION"
    TECHNOLOGY = "TECHNOLOGY"
    SKILL = "SKILL"
    EXPERIENCE = "EXPERIENCE"
    CERTIFICATION = "CERTIFICATION"
    ACHIEVEMENT = "ACHIEVEMENT"
    WHO = "WHO"
    WHAT = "WHAT"
    WHEN = "WHEN"
    WHERE = "WHERE"
    WHY = "WHY"
    HOW = "HOW"
    WHICH = "WHICH"
    YES_NO = "YES_NO"
    DEFINITION = "DEFINITION"
    ATTRIBUTE = "ATTRIBUTE"
    GENERAL = "GENERAL"

# Semantic synonyms map connecting canonical attribute keys to list of equivalent terms
SYNONYMS_MAP = {
    'sslc': ['sslc', '10th', '10th standard', 'secondary school', '10th class', 'class 10', 'matriculation', 'ssvm'],
    'puc': ['puc', '12th', '12th standard', 'pre-university', 'pre university', '12th class', 'class 12', 'hsc', 'higher secondary', 'sgpta pu college'],
    'cgpa': ['cgpa', 'gpa', 'grade point', 'pointer', 'cumulative grade point average'],
    'percentage': ['percentage', 'percent', 'score', 'marks percentage', 'marks %', '%'],
    'email': ['email', 'e-mail', 'mail', 'email address', 'mail id', 'gmail'],
    'phone': ['phone', 'mobile', 'contact number', 'phone number', 'contact', 'telephone', 'mobile number'],
    'college': ['college', 'university', 'institution', 'school', 'institute', 'academy'],
    'degree': ['degree', 'qualification', 'bachelor', 'master', 'b.e.', 'b.tech', 'm.tech', 'major', 'education', 'course'],
    'graduation': ['graduate', 'graduation', 'passing year', 'pass out year', 'completed in', 'graduated', 'graduating year'],
    'skills': ['skill', 'skills', 'technical skills', 'programming languages', 'technologies', 'tools', 'frameworks', 'languages']
}

def normalize_question(question: str) -> Tuple[str, Optional[str], Optional[str]]:
    """
    Normalizes the question prompt to identify:
    1. Question Type (e.g. PERCENTAGE, CGPA, YEAR, EMAIL, SKILL, DEGREE, etc.)
    2. Target Attribute key (e.g. 'sslc', 'puc', 'cgpa', 'email', 'skills', etc.)
    3. Canonical Label (e.g. 'SSLC Percentage', 'PUC Percentage', etc.)
    """
    q_lower = question.lower().strip()

    target_attribute = None
    canonical_label = None
    q_type = QuestionType.GENERAL

    # Identify target attribute key from synonyms map
    for attr, synonyms in SYNONYMS_MAP.items():
        for syn in synonyms:
            if re.search(r'\b' + re.escape(syn) + r'\b', q_lower):
                target_attribute = attr
                break
        if target_attribute:
            break

    # Determine Question Value Type based on intent / keywords
    if re.search(r'\b(percentage|percent|%|score|marks|marks percentage)\b', q_lower):
        q_type = QuestionType.PERCENTAGE
        if target_attribute == 'sslc':
            canonical_label = "SSLC Percentage"
        elif target_attribute == 'puc':
            canonical_label = "PUC Percentage"
        else:
            canonical_label = "Percentage / Score"

    elif re.search(r'\b(cgpa|gpa|grade point)\b', q_lower):
        q_type = QuestionType.CGPA
        target_attribute = target_attribute or 'cgpa'
        canonical_label = "CGPA"

    elif re.search(r'\b(email|mail|email address)\b', q_lower):
        q_type = QuestionType.EMAIL
        target_attribute = target_attribute or 'email'
        canonical_label = "Email Address"

    elif re.search(r'\b(phone|mobile|contact|contact number|phone number)\b', q_lower):
        q_type = QuestionType.PHONE
        target_attribute = target_attribute or 'phone'
        canonical_label = "Phone / Contact Number"

    elif re.search(r'\b(when|year|date|pass out|passing year|graduate|graduation)\b', q_lower):
        q_type = QuestionType.YEAR
        target_attribute = target_attribute or 'graduation'
        canonical_label = "Graduation / Completion Year"

    elif re.search(r'\b(degree|qualification|bachelor|master|b\.e|b\.tech|major)\b', q_lower):
        q_type = QuestionType.DEGREE
        target_attribute = target_attribute or 'degree'
        canonical_label = "Degree / Qualification"

    elif re.search(r'\b(skill|skills|programming languages|technologies|tools|frameworks)\b', q_lower):
        q_type = QuestionType.SKILL
        target_attribute = target_attribute or 'skills'
        canonical_label = "Technical Skills / Programming Languages"

    elif q_lower.startswith(('is ', 'are ', 'was ', 'were ', 'do ', 'does ', 'did ', 'can ', 'could ', 'has ', 'have ')):
        q_type = QuestionType.YES_NO

    elif re.search(r'\b(who|created by|authored by|developer of)\b', q_lower):
        q_type = QuestionType.WHO

    elif re.search(r'\b(where|location|place|country|city)\b', q_lower):
        q_type = QuestionType.WHERE

    elif re.search(r'\b(why|reason|purpose)\b', q_lower):
        q_type = QuestionType.WHY

    elif re.search(r'\b(how|method|procedure)\b', q_lower):
        q_type = QuestionType.HOW

    elif re.search(r'\bwhat is\b|\bwhat are\b|\bdefine\b|\bdefinition of\b', q_lower):
        q_type = QuestionType.DEFINITION

    elif re.search(r'\b(what|which)\b', q_lower):
        q_type = QuestionType.WHAT

    return q_type, target_attribute, canonical_label


def detect_question_type(question: str) -> str:
    """Detect functional question type from user prompt (backward compatible wrapper)."""
    q_type, _, _ = normalize_question(question)
    return q_type


class AnswerExtractor:
    """Extracts concise factoid answers from retrieved passages using pattern heuristics, semantic synonyms, and score ranking."""

    def expand_query_with_synonyms(self, query: str) -> str:
        """Expands user query with semantic synonyms for improved TF-IDF retrieval."""
        q_lower = query.lower()
        _, target_attribute, _ = normalize_question(query)
        
        expanded_terms = []
        # Generic personal/resume terms expansion
        if re.search(r'\b(user|user\'s|my|i|me|candidate|applicant|resume|person|author)\b', q_lower):
            expanded_terms.extend(['resume', 'education', 'contact', 'experience'])
            
        if target_attribute and target_attribute in SYNONYMS_MAP:
            expanded_terms.extend(SYNONYMS_MAP[target_attribute])
            
        if expanded_terms:
            return f"{query} " + " ".join(set(expanded_terms))
        return query

    def _extract_percentages(self, text: str) -> List[Dict]:
        """Extract percentage patterns like 92.64%, 95.17%, 85 percent."""
        matches = []
        pattern = r'(\d+(?:\.\d+)?\s*(?:%|percent|percentage))'
        for m in re.finditer(pattern, text, re.IGNORECASE):
            matches.append({
                'value': m.group(1).strip(),
                'start': m.start(),
                'end': m.end()
            })
        return matches

    def _extract_cgpas(self, text: str) -> List[Dict]:
        """Extract CGPA/GPA patterns like 9.48/10.0, 9.48, CGPA: 9.48, 3.9/4.0."""
        matches = []
        pattern = r'(?:cgpa|gpa)?\s*:?\s*(\b[0-9]\.\d{1,2}\s*(?:\/\s*10(?:\.0)?)?|\b10(?:\.0)?\s*\/\s*10\b)'
        for m in re.finditer(pattern, text, re.IGNORECASE):
            val = m.group(1).strip()
            val = val.rstrip('.')
            matches.append({
                'value': val,
                'start': m.start(),
                'end': m.end()
            })
        return matches

    def _extract_years(self, text: str) -> List[Dict]:
        """Extract 4-digit year patterns like 2021, 2023, 2027."""
        matches = []
        # Check for year ranges like 2023-2027 first (prefer graduation end year)
        range_pattern = r'\b(19\d{2}|20\d{2})\s*[-–\s]+\s*(19\d{2}|20\d{2})\b'
        for m in re.finditer(range_pattern, text):
            matches.append({
                'value': m.group(2),
                'full_match': m.group(0),
                'start': m.start(),
                'end': m.end()
            })
        
        single_pattern = r'\b(19\d{2}|20\d{2})\b'
        for m in re.finditer(single_pattern, text):
            matches.append({
                'value': m.group(1),
                'start': m.start(),
                'end': m.end()
            })
        return matches

    def _extract_emails(self, text: str) -> List[Dict]:
        """Extract email address patterns."""
        matches = []
        pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        for m in re.finditer(pattern, text):
            matches.append({
                'value': m.group(0),
                'start': m.start(),
                'end': m.end()
            })
        return matches

    def _extract_phones(self, text: str) -> List[Dict]:
        """Extract phone number patterns."""
        matches = []
        pattern = r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        for m in re.finditer(pattern, text):
            matches.append({
                'value': m.group(0),
                'start': m.start(),
                'end': m.end()
            })
        return matches

    def _extract_degrees(self, text: str) -> List[Dict]:
        """Extract degree and educational qualification phrases."""
        matches = []
        patterns = [
            r'\b(bachelor\s+of\s+engineering\s*[–-]?\s*[a-zA-Z\s&]+|\bmaster\s+of\s+[a-zA-Z\s&]+|\bB\.E\.?\s*[a-zA-Z\s&]*|\bB\.Tech\b)',
            r'\b(pre-university[^\n|,.–-]*|\bPUC\b|\b12th[^\n|,.–-]*)',
            r'\b(SSLC[^\n|,.–-]*|\b10th[^\n|,.–-]*)'
        ]
        for pat in patterns:
            for m in re.finditer(pat, text, re.IGNORECASE):
                matches.append({
                    'value': m.group(0).strip(),
                    'start': m.start(),
                    'end': m.end()
                })
        return matches

    def _extract_skills(self, text: str) -> List[Dict]:
        """Extract technical skills and programming languages."""
        matches = []
        pattern = r'(?:programming languages|technical skills|skills|frameworks|tools)\s*:?\s*([^\n|.]+)'
        for m in re.finditer(pattern, text, re.IGNORECASE):
            matches.append({
                'value': m.group(1).strip(),
                'start': m.start(),
                'end': m.end()
            })
        return matches

    def _rank_candidates(self, candidates: List[Dict], text: str, target_attribute: Optional[str]) -> Optional[Dict]:
        """
        Ranks candidate values using attribute-value forward distance, co-occurrence, and character proximity.
        """
        if not candidates:
            return None

        synonyms = SYNONYMS_MAP.get(target_attribute, [target_attribute]) if target_attribute else []

        # Locate all occurrences of target attribute synonyms in text
        attribute_positions = []
        if synonyms:
            for syn in synonyms:
                for m in re.finditer(r'\b' + re.escape(syn) + r'\b', text, re.IGNORECASE):
                    attribute_positions.append(m.start())

        best_cand = None
        best_score = -1.0

        for cand in candidates:
            c_pos = cand['start']
            
            if attribute_positions:
                # Forward attribute distance: attribute label precedes candidate value
                forward_distances = [c_pos - a_pos for a_pos in attribute_positions if c_pos >= a_pos]
                if forward_distances:
                    min_dist = min(forward_distances)
                    same_context = 1.0 if min_dist < 80 else 0.5
                    proximity_score = max(0.0, 1.0 - (min_dist / 120.0))
                    cand_score = (proximity_score * 0.7) + (same_context * 0.3)
                else:
                    # Backward distance penalty (value precedes label)
                    min_dist = min(abs(c_pos - a_pos) for a_pos in attribute_positions)
                    cand_score = max(0.1, 0.4 - (min_dist / 100.0))
            else:
                min_dist = 9999
                cand_score = 0.5 - (c_pos / (len(text) + 1.0)) * 0.1

            cand['score'] = cand_score
            cand['min_dist'] = min_dist

            if cand_score > best_score:
                best_score = cand_score
                best_cand = cand

        return best_cand

    def _extract_single_passage(self, question: str, passage: Dict, q_type: str, target_attribute: Optional[str], canonical_label: Optional[str]) -> Dict:
        text = passage['text']
        retrieval_score = passage.get('score', 0.0)
        source = passage.get('source', 'document')

        candidates = []
        if q_type == QuestionType.PERCENTAGE:
            candidates = self._extract_percentages(text)
        elif q_type == QuestionType.CGPA:
            candidates = self._extract_cgpas(text)
        elif q_type == QuestionType.YEAR:
            candidates = self._extract_years(text)
        elif q_type == QuestionType.EMAIL:
            candidates = self._extract_emails(text)
        elif q_type == QuestionType.PHONE:
            candidates = self._extract_phones(text)
        elif q_type == QuestionType.DEGREE:
            candidates = self._extract_degrees(text)
        elif q_type == QuestionType.SKILL:
            candidates = self._extract_skills(text)

        best_cand = self._rank_candidates(candidates, text, target_attribute)

        extracted_val = None
        matched_attr_name = target_attribute.upper() if target_attribute else "Factoid"
        confidence = 0.50

        if best_cand and best_cand.get('score', 0) > 0.2:
            extracted_val = best_cand['value']
            min_dist = best_cand.get('min_dist', 9999)

            if min_dist < 60:
                confidence = 0.96
            elif min_dist < 120:
                confidence = 0.82
            else:
                confidence = 0.68

            if canonical_label:
                concise_answer = f"{canonical_label}: {extracted_val}"
            else:
                concise_answer = extracted_val

        else:
            q_tokens = set(tokenize(question, remove_stopwords=True))
            p_tokens = set(tokenize(text, remove_stopwords=True))
            overlap = len(q_tokens.intersection(p_tokens)) / max(len(q_tokens), 1) if q_tokens else 0.5

            if target_attribute and q_type in [QuestionType.PERCENTAGE, QuestionType.CGPA, QuestionType.EMAIL, QuestionType.PHONE]:
                return {
                    'answer': "I couldn't find a reliable answer in the indexed documents.",
                    'question_type': q_type,
                    'confidence': 0.20,
                    'source': source,
                    'passage': text,
                    'search_explanation': {
                        'query': question,
                        'retrieved_passages': [passage['text']],
                        'similarity_scores': [retrieval_score],
                        'selected_passage': text,
                        'extracted_answer': "Requested attribute value not present in retrieved passage."
                    }
                }

            concise_answer = text
            confidence = min(0.92, max(0.40, (retrieval_score * 0.6) + (overlap * 0.4)))

        return {
            'answer': concise_answer,
            'question_type': q_type,
            'confidence': round(confidence, 2),
            'source': source,
            'passage': text,
            'search_explanation': {
                'query': question,
                'retrieved_document': source,
                'relevant_passage': text,
                'matched_attribute': matched_attr_name,
                'extracted_value': extracted_val or concise_answer,
                'extraction_method': 'Attribute-Value Distance & Proximity Matching' if best_cand else 'Passage Relevance',
                'confidence_reasoning': f"Extracted '{extracted_val}' with forward attribute distance {best_cand.get('min_dist', 'N/A')} chars." if best_cand else "Standard TF-IDF passage retrieval.",
                'retrieved_passages': [passage['text']],
                'similarity_scores': [retrieval_score],
                'selected_passage': text,
                'extracted_answer': concise_answer
            }
        }

    def extract_answer(self, question: str, retrieved_passages: List[Dict]) -> Dict:
        """
        Processes top retrieved passages and extracts the most relevant concise factoid answer.
        """
        q_type, target_attribute, canonical_label = normalize_question(question)
        fallback_msg = "I couldn't find a reliable answer in the indexed documents."

        if not retrieved_passages:
            return {
                'answer': fallback_msg,
                'question_type': q_type,
                'confidence': 0.0,
                'source': "none",
                'passage': "",
                'search_explanation': {
                    'query': question,
                    'retrieved_passages': [],
                    'selected_passage': None,
                    'extracted_answer': "No passages retrieved."
                }
            }

        # Evaluate candidate extraction across all retrieved passages
        best_result = None
        best_conf = -1.0

        for p in retrieved_passages:
            res = self._extract_single_passage(question, p, q_type, target_attribute, canonical_label)
            if res['confidence'] > best_conf:
                best_conf = res['confidence']
                best_result = res

        if best_result and best_conf >= 0.50:
            # Add full retrieved passages list to search_explanation
            best_result['search_explanation']['retrieved_passages'] = [p['text'] for p in retrieved_passages]
            best_result['search_explanation']['similarity_scores'] = [p.get('score', 0) for p in retrieved_passages]
            return best_result

        # Out of domain / Low confidence fallback
        return {
            'answer': fallback_msg,
            'question_type': q_type,
            'confidence': 0.0 if not retrieved_passages else round(max(0.0, retrieved_passages[0].get('score', 0.0)), 2),
            'source': "none" if not retrieved_passages else retrieved_passages[0].get('source', 'document'),
            'passage': "" if not retrieved_passages else retrieved_passages[0]['text'],
            'search_explanation': {
                'query': question,
                'retrieved_passages': [p['text'] for p in retrieved_passages],
                'similarity_scores': [p.get('score', 0) for p in retrieved_passages],
                'selected_passage': retrieved_passages[0]['text'] if retrieved_passages else None,
                'extracted_answer': fallback_msg
            }
        }
