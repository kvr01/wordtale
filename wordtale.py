import itertools
import pyphen
from wt_find_path import get_paths_between
from wt_score import get_sol_score

pyphen_dic = pyphen.Pyphen(lang='en')
def syllabize(w):
	return pyphen_dic.inserted(w).split('-')
	
def wordtale(w, dmax=4):
	"""Find best etymological story(ies) for word w, according to the method described in the paper.
	
	Named arguments:
	dmax -- The search depth from w to its constituent syllables.
	
	Return value:
	a pair -- best score, a list containing best etymological story(ies)
	"""
	
	wis = syllabize(w)
	paths = [get_paths_between(w, wi, dmax) for wi in wis]
	sols =  itertools.product(paths, repeat=len(wis))
	sol_scores = [get_sol_score(sol, dmax) for sol in sols]
	max_score = max(sol_scores)
	best_sols = [sol for sol, score in zip(sol, score) if score == max_score]
	return max_score, best_sols
	
if __name__ == '__main__':
	p0 = [[('ali', '/r/HasA'), ('ketab', '/r/IsA'), ('obj', '/r/HasA')], 'subject']
	print(path_to_sentence(p0))
	#for r in sentence_parts_dict:
	#	print('ali %r ketab' % r, path_to_sentence([[('ali', r)], 'ketab']))

	if len(sys.argv) != 1:
		print('usage: wordtale.py word')
		sys.exit(1)
	
	wordtale(sys.argv[1])
