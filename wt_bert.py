from sentence_transformers import SentenceTransformer
from mlm.scorers import MLMScorer, MLMScorerPT, LMScorer
from mlm.models import get_pretrained
import mxnet as mx


sbert_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
def sbert_emb(s):
	return sbert_model.encode([s])[0]


ctxs = [mx.cpu()] # or, e.g., [mx.gpu(0), mx.gpu(1)]
bert_model, vocab, tokenizer = get_pretrained(ctxs, 'bert-base-en-cased')
scorer = MLMScorer(model, vocab, tokenizer, ctxs)


def bert_p(s):
	return scorer.score_sentences([s])[0]
	
