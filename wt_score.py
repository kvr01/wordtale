import itertools
import numpy as np
from numpy import linalg as LA
from wt_path2sentence import path2sentence
from wt_bert import bert_emb, bert_p

GLOVE_FILE = "/path/to/glove.6B.zip" # download from https://github.com/stanfordnlp/GloVe
# From: https://keras.io/examples/nlp/pretrained_word_embeddings/
def load_glove():
	ret = dict()
	with open(GLOVE_FILE) as f:
		for line in f:
			word, coefs = line.split(maxsplit=1)
			coefs = np.fromstring(coefs, "f", sep=" ")
			ret[word] = coefs
	return ret


def cosine01(a, b):
	""" Calculate a cosine-like SIMILARITY between a and b, which ranges between 0 and 1."""
	cos_sim = np.dot(a, b)/(LA.norm(a)*LA.norm(b))
	return .5*(cos_sim+1)


"""Score of ConceptNet (/r/) and WordTale (/wt/) relations.

Each relation's score is a rough estimates of how much two entities related with the relation are conceptually related. See the paper for more details."""
rel_scores_dict = {
	'/r/FormOf': 1, '/r/Synonym': 1, '/r/Antonym': 1, '/r/DerivedFrom': 1, '/r/SymbolOf': 1,
	'/r/DefinedAs': 1, '/r/SimilarTo': 1, '/r/EtymologicallyRelatedTo': 1, '/r/EtymologicallyDerivedFrom': 1,
	'/wt/spelling': 1, '/wt/pronunciation': 1,
	'/r/IsA': 0.6, '/r/PartOf': 0.6, '/r/HasA': 0.6, '/r/HasProperty': 0.6, '/r/MannerOf': 0.6, #???????
	'/r/MadeOf': 0.6,
	'/r/UsedFor': 0.3, '/r/CapableOf': 0.3, '/r/AtLocation': 0.3, '/r/Causes': 0.3, '/r/HasSubevent': 0.3,
	'/r/HasFirstSubevent': 0.3, '/r/HasLastSubevent': 0.3, '/r/HasPrerequisite': 0.3, '/r/MotivatedByGoal': 0.3,
	'/r/ObstructedBy': 0.3, '/r/Desires': 0.3, '/r/CreatedBy': 0.3, '/r/LocatedNear': 0.3, '/r/ReceivesAction': 0.3,
	'/r/CausesDesire': 0.3, '/r/RelatedTo': 0, '/r/DistinctFrom': 0, '/r/HasContext': 0, '/r/ExternalURL': 0
}
glove_dict = load_glove()


def get_path_score(p, dmax):
	s1 = len(p)/dmax
	s2 = np.mean([rel_scores_dict[r] for e,r in p[0]])
	s3 = bert_p(path2sentence(p))
	
	es = [e for e,r in p[1]] + [p[-1]]
	for e1, e2 in zip(es, es[1:]):
		if e1 in glove_dict and e2 in glove_dict:
		s4_coses.appends(cosine01(glove_dict[e1], glove_dict[e2])
	s4 = np.mean(s4_coses)
	return .25*(s1+s2+s3+s4)
	

def get_sol_score(sol, dmax):
	def get_sol_score_mps(sol):
		return np.mean([get_path_score(p, dmax) for p in sol])
		
	def get_sol_score_coh(sol):
		combs = itertools.combinations(sol, 2)
		mutual_scores = []
		for p1,p2 in combs:
			b1, b2 = bert_emb(path2sentence(p1)), bert_emb(path2sentence(p2))
			mutual_scores.append(cosine01(b1, b2))
		return np.mean(mutual_scores)
		
	mps = get_sol_score_mps(sol)
	coh = get_sol_score_coh(sol)
	return .5*(mps+coh)

