# Summarization Engineer

## Role
NLP Engine Integration

## Assigned Ticket
TICKET-04: Summarization Engine

## Responsibilities
- Integrate NLP models from base repository
- Implement 4 summarization modes
- Optimize model performance and loading
- Handle character counting and validation
- Write unit tests for each mode

## MCP Tools
- `filesystem_mcp` (Read, Write, Edit)

## Deliverables

### 1. Four Summarization Modes

#### Extractive (TextRank)
- Algorithm: TextRank (graph-based ranking)
- Extract key sentences from original text
- Fast processing (<1 second)
- No model loading required
- Libraries: nltk, networkx

#### Abstractive (T5/BART)
- Model: T5-small or BART-base
- Generate new paraphrased summary
- Slower processing (2-5 seconds)
- Requires model download (~250MB)
- Libraries: transformers, torch

#### Hybrid
- Combination of extractive + abstractive
- First extract key sentences (TextRank)
- Then paraphrase with T5/BART
- Best quality, slower processing

#### Keyword Extraction
- Extract important keywords and phrases
- Use TF-IDF + Named Entity Recognition (NER)
- Fast processing
- Libraries: sklearn, spaCy

### 2. Model Management
- Load models on startup (cache in memory)
- Model quantization for faster inference
- Graceful fallback if model loading fails
- ONNX conversion (optional optimization)

### 3. Input Validation
- Character counting
- Maximum input length enforcement
- Minimum input length check
- Sanitize input (remove HTML, special chars)

## File Structure

```
src/summarizer/
├── models.py          # SummarizationRequest, Result
├── engines/
│   ├── __init__.py
│   ├── extractive.py  # TextRank implementation
│   ├── abstractive.py # T5/BART implementation
│   ├── hybrid.py      # Combination
│   └── keywords.py    # Keyword extraction
├── utils/
│   ├── preprocessing.py  # Text cleaning
│   ├── model_loader.py   # Model caching
│   └── validators.py     # Input validation
├── admin.py
├── apps.py           # Model loading on app ready
└── tests/
    ├── test_extractive.py
    ├── test_abstractive.py
    ├── test_hybrid.py
    └── test_keywords.py
```

## Technical Requirements

### Extractive Engine (TextRank)
```python
import nltk
import networkx as nx
from nltk.tokenize import sent_tokenize
from sklearn.metrics.pairwise import cosine_similarity

class ExtractiveSummarizer:
    def __init__(self):
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)

    def summarize(self, text: str, num_sentences: int = 5) -> str:
        """Extract key sentences using TextRank."""
        sentences = sent_tokenize(text)

        # Build sentence vectors
        sentence_vectors = self._vectorize_sentences(sentences)

        # Create similarity matrix
        similarity_matrix = cosine_similarity(sentence_vectors)

        # Run PageRank
        nx_graph = nx.from_numpy_array(similarity_matrix)
        scores = nx.pagerank(nx_graph)

        # Select top sentences
        ranked_sentences = sorted(
            ((scores[i], s) for i, s in enumerate(sentences)),
            reverse=True
        )

        # Return top N sentences in original order
        top_sentences = [s for _, s in ranked_sentences[:num_sentences]]
        return ' '.join(top_sentences)
```

### Abstractive Engine (T5)
```python
from transformers import T5Tokenizer, T5ForConditionalGeneration
import torch

class AbstractiveSummarizer:
    def __init__(self, model_name: str = "t5-small"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = T5Tokenizer.from_pretrained(model_name)
        self.model = T5ForConditionalGeneration.from_pretrained(model_name)
        self.model.to(self.device)
        self.model.eval()

    def summarize(self, text: str, max_length: int = 150) -> str:
        """Generate abstractive summary using T5."""
        input_text = f"summarize: {text}"
        inputs = self.tokenizer(
            input_text,
            return_tensors="pt",
            max_length=512,
            truncation=True
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model.generate(
                inputs.input_ids,
                max_length=max_length,
                min_length=50,
                length_penalty=2.0,
                num_beams=4,
                early_stopping=True
            )

        summary = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return summary
```

### Keyword Extraction
```python
from sklearn.feature_extraction.text import TfidfVectorizer
import spacy

class KeywordExtractor:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")

    def extract_keywords(self, text: str, top_n: int = 10) -> list:
        """Extract keywords using TF-IDF and NER."""
        # TF-IDF keywords
        vectorizer = TfidfVectorizer(max_features=top_n, stop_words='english')
        tfidf_matrix = vectorizer.fit_transform([text])
        keywords = vectorizer.get_feature_names_out()

        # Named entities
        doc = self.nlp(text)
        entities = [ent.text for ent in doc.ents]

        # Combine and deduplicate
        all_keywords = list(set(list(keywords) + entities))
        return all_keywords[:top_n]
```

### Model Loader (App Ready)
```python
# src/summarizer/apps.py
from django.apps import AppConfig

class SummarizerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'summarizer'

    def ready(self):
        """Load models on app startup."""
        from .engines.extractive import ExtractiveSummarizer
        from .engines.abstractive import AbstractiveSummarizer
        from .engines.keywords import KeywordExtractor

        # Cache models globally
        import summarizer.engines as engines
        engines.extractive_model = ExtractiveSummarizer()
        engines.abstractive_model = AbstractiveSummarizer()
        engines.keyword_model = KeywordExtractor()

        print("✅ Summarization models loaded successfully")
```

### Input Validator
```python
import re
from django.core.exceptions import ValidationError

def validate_input(text: str, min_chars: int = 100, max_chars: int = 50000):
    """Validate summarization input."""
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)

    # Count characters
    char_count = len(text.strip())

    if char_count < min_chars:
        raise ValidationError(
            f"Text too short. Minimum {min_chars} characters required."
        )

    if char_count > max_chars:
        raise ValidationError(
            f"Text too long. Maximum {max_chars} characters allowed."
        )

    return text, char_count
```

## Model Files Storage

Models will be downloaded to:
```
/app/models/
├── t5-small/
├── spacy/en_core_web_sm/
└── nltk_data/
```

In Docker, mount a volume to persist models:
```yaml
volumes:
  - model_cache:/app/models
```

## Testing Requirements

### Unit Tests
- Extractive summarization accuracy
- Abstractive summarization quality
- Hybrid mode combines both
- Keyword extraction relevance
- Input validation edge cases
- Model loading and caching

### Performance Tests
- Processing time <5 seconds for typical input
- Memory usage acceptable (<2GB)
- Concurrent request handling

### Test Data
Use sample texts of varying lengths:
- Short (500 chars)
- Medium (2000 chars)
- Long (10000 chars)

## Visual QA Handoff
**Not required for TICKET-04** (backend only)

Visual QA will validate when integrated into API (TICKET-05)

## Acceptance Criteria

- [ ] All 4 modes implemented and functional
- [ ] Extractive mode processes in <1 second
- [ ] Abstractive mode processes in <5 seconds
- [ ] Hybrid mode produces quality summaries
- [ ] Keyword extraction returns relevant terms
- [ ] Models cached and reused (not reloaded per request)
- [ ] Input validation prevents invalid inputs
- [ ] Character counting accurate
- [ ] All unit tests passing
- [ ] No model loading errors in logs

## Dependencies
```txt
transformers==4.36.2
torch==2.1.2
sentencepiece==0.1.99
nltk==3.8.1
scikit-learn==1.4.0
numpy==1.26.3
networkx==3.2.1
spacy==3.7.2
```

Additional downloads:
```bash
python -m spacy download en_core_web_sm
```

## Performance Optimization

### Model Quantization
```python
# Reduce model size by 4x with minimal accuracy loss
quantized_model = torch.quantization.quantize_dynamic(
    model, {torch.nn.Linear}, dtype=torch.qint8
)
```

### Caching Strategy
- Load models once on app startup
- Keep models in memory (not on disk)
- Use GPU if available (`cuda`)
- Batch processing for multiple requests

## Handoff To
- API Engineer (integrate into REST API)

## Communication Protocol

### On Completion
```
[SUMMARIZATION_ENGINEER] → [ORCHESTRATOR_AGENT]
ACTION: COMPLETE
TICKET: TICKET-04
STATUS: COMPLETE
ARTIFACTS:
  - src/summarizer/engines/extractive.py
  - src/summarizer/engines/abstractive.py
  - src/summarizer/engines/hybrid.py
  - src/summarizer/engines/keywords.py
  - src/summarizer/tests/
TESTS:
  - Passed: 32
  - Coverage: 85%
VISUAL_QA_REQUIRED: NO
PERFORMANCE:
  - Extractive: 0.8s avg
  - Abstractive: 3.2s avg
  - Hybrid: 4.1s avg
  - Keywords: 0.5s avg
READY_FOR_NEXT: [TICKET-05]
```

## Important Notes
- Download models during Docker build, not runtime
- Gracefully handle OOM errors (out of memory)
- Provide fallback to extractive if abstractive fails
- Log processing times for monitoring
- Consider ONNX runtime for production (faster inference)
