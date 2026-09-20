import re
import string

STOPWORDS = {
    'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', 'aren\'t', 'as', 'at',
    'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by', 'can', 'can\'t', 'cannot',
    'could', 'couldn\'t', 'did', 'didn\'t', 'do', 'does', 'doesn\'t', 'doing', 'don\'t', 'down', 'during', 'each',
    'few', 'for', 'from', 'further', 'had', 'hadn\'t', 'has', 'hasn\'t', 'have', 'haven\'t', 'having', 'he', 'he\'d',
    'he\'ll', 'he\'s', 'her', 'here', 'here\'s', 'hers', 'herself', 'him', 'himself', 'his', 'how', 'how\'s', 'i',
    'i\'d', 'i\'ll', 'i\'m', 'i\'ve', 'if', 'in', 'into', 'is', 'isn\'t', 'it', 'it\'s', 'its', 'itself', 'let\'s',
    'me', 'more', 'most', 'mustn\'t', 'my', 'myself', 'no', 'nor', 'not', 'of', 'off', 'on', 'once', 'only', 'or',
    'other', 'ought', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'same', 'shan\'t', 'she', 'she\'d', 'she\'ll',
    'she\'s', 'should', 'shouldn\'t', 'so', 'some', 'such', 'than', 'that', 'that\'s', 'the', 'their', 'theirs',
    'them', 'themselves', 'then', 'there', 'there\'s', 'these', 'they', 'they\'d', 'they\'ll', 'they\'re', 'they\'ve',
    'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was', 'wasn\'t', 'we', 'we\'d', 'we\'ll',
    'we\'re', 'we\'ve', 'were', 'weren\'t', 'what', 'what\'s', 'when', 'when\'s', 'where', 'where\'s', 'which',
    'while', 'who', 'who\'s', 'whom', 'why', 'why\'s', 'with', 'won\'t', 'would', 'wouldn\'t', 'you', 'you\'d',
    'you\'ll', 'you\'re', 'you\'ve', 'your', 'yours', 'yourself', 'yourselves'
}

def clean_text(text: str) -> str:
    """Clean text by standardizing whitespace, camel-case boundaries, and quotes while protecting email addresses."""
    if not text:
        return ""
    text = text.replace('\r', ' ').replace('\n', ' ')

    # 1. Protect email addresses from digit-word boundary splitting
    emails = []
    def save_email(m):
        emails.append(m.group(0))
        return f'__EMAIL_{len(emails)-1}__'

    text = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', save_email, text)

    # 2. Insert space between lower-case and UPPER-case (e.g. BangaloreCGPA -> Bangalore CGPA)
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    # Insert space between letter and digit (e.g. College2023 -> College 2023)
    text = re.sub(r'([a-zA-Z])(\d)', r'\1 \2', text)
    # Insert space between digit and non-ordinal letter (e.g. 2023Pre -> 2023 Pre)
    text = re.sub(r'(\d+)(?!(?:st|nd|rd|th)\b)([a-zA-Z])', r'\1 \2', text, flags=re.IGNORECASE)

    # 3. Restore email addresses intact
    for i, email in enumerate(emails):
        text = text.replace(f'__EMAIL_{i}__', email)

    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def tokenize(text: str, remove_stopwords: bool = False) -> list:
    """Tokenize text into lowercased alphanumeric words."""
    if not text:
        return []
    words = re.findall(r'\b[a-zA-Z0-9]+\b', text.lower())
    if remove_stopwords:
        words = [w for w in words if w not in STOPWORDS]
    return words

def split_into_sentences(text: str) -> list:
    """
    Segment unstructured text into meaningful, clean sentences.
    Handles common abbreviations and sentence endings (. ! ?).
    """
    if not text:
        return []
    
    cleaned = clean_text(text)
    # Split on punctuation followed by space or capital letter
    raw_sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z0-9"])', cleaned)
    
    sentences = []
    for s in raw_sentences:
        s = s.strip()
        if len(s) > 10:  # Ignore trivial sentence fragments
            sentences.append(s)
            
    if not sentences and cleaned:
        sentences = [cleaned]
        
    return sentences

def extract_keywords(text: str, top_n: int = 5) -> list:
    """Extract key non-stopword tokens from text."""
    tokens = tokenize(text, remove_stopwords=True)
    freq = {}
    for t in tokens:
        freq[t] = freq.get(t, 0) + 1
    sorted_keywords = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    return [k for k, _ in sorted_keywords[:top_n]]
