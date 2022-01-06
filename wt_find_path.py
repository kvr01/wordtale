from tqdm import tqdm
from os import path
from collections import defaultdict
import eng_to_ipa as ipa
import sqlite3


CNET_FILE_ORIG = "/path/to/conceptnet-en.csv"
CNET_FILE_PP = "/path/to/conceptnet-en.pp.csv" # preprocessed file (see function preprocess_conceptnet_file)

cnet_dict = None

def ipa_fetch_all_words():
	db_path = path.join(path.abspath(ipa.__path__[0]), 'resources/CMU_dict.db')
	conn = sqlite3.connect(db_path)
	cursor = conn.cursor() 
	cursor.execute("SELECT word FROM dictionary")
	d = list()
	for k, in cursor.fetchall():
		d.append(k)
	return list(set(d))
	
ipa_dict = {w:ipa.convert(w, stress_marks=None) for w in ipa_fetch_all_words()[1:100]}
ipa_dict_rev = defaultdict(list)
IPA_LETTERS = []
for w,wipa in ipa_dict.items():
	ipa_dict_rev[wipa].append(w)
	IPA_LETTERS.extend(wipa)
IPA_LETTERS = list(set(IPA_LETTERS))
ENG_LETTERS = 'abcdefghijklmnopqrstuvwxyz'

# From: http://norvig.com/spell-correct.html
def edits1(word, letters=ENG_LETTERS):
    "All edits that are one edit away from `word`."
    splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
    deletes    = [L + R[1:]               for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
    replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
    inserts    = [L + c + R               for L, R in splits for c in letters]
    return set(deletes + transposes + replaces + inserts)

def get_orthographic_mutants(w):
	return edits1(w)
	
def get_phoentic_mutants(w):
	if w in ipa_dict:
		wipa = ipa_dict[ipa]
	ret = []
	for anipa in edits1(wipa, letters=IPA_LETTERS):
		ret.extend(ipa_dict_rev[anipa])
	return ret

def get_paths_between(x, y, dmax):
	""" Find all paths, up to length dmax, between nodes x and y on English ConceptNet graph, paying attention to x, y, and intermediate nodes' "mutants" (see the paper).
	
	An interative BFS algorithm is implemenetd. In variables ret and stack, paths are stored as sequence of subject, relation, object, etc., e.g., [s1,r1,o1,s2,r2,o2,...]. Before returning, they are converted to the form 
	of [[(e1,r1),...,],eN] as required by scoring functions (see wordtale.py).
	"""
	ret = []
	stack = [([x],0)]
	while stack:
		curr_path, curr_d = stack.pop()
		if curr_path[-1] == y:
			ret.append(curr_path)
			continue
		if curr_d > dmax: continue
		
		last_e = curr_path[-1]
		for r,o_s in cnet_dict[last_e].items():
			for o in o_s:
				stack.append((curr_path+[r,o], curr_d+1))
		for o in get_orthographic_mutants(last_e):
			if o in cnet_dict:
				stack.append((curr_path+['/wt/spelling',o], curr_d+1))
		for o in get_phoentic_mutants(last_e):
			if o in cnet_dict:
				stack.append((curr_path+['/wt/pronunciation',o], curr_d+1))
	final_ret = []
	for p in ret:
		first = list(zip(p[::2], p[1::2]))
		final_ret.append([first, p[-1]])
	return final_ret
	

def load_cnet():
	ret = defaultdict(lambda: defaultdict(list))
	with open(CNET_FILE_PP, encoding='utf-8') as inf:
		for lii, li in tqdm(enumerate(inf)):
			#r,s,o,_ = li.strip().split('\t')
			r,s,o = li.strip().split('\t')
			ret[s][r].append(o)
	return ret

def make_pp_cnet_file():
	""" Select English language rows from original ConceptNet file.
		
	Sample line in the original file: /a/[/r/Antonym/,/c/en/агыруа/n/,/c/en/аҧсуа/]   /r/Antonym      /c/en/агыруа/n  /c/en/аҧсуа     {"dataset": "/d/wiktionary/en", "license": "cc:by-sa/4.0", "sources": [{"contributor": "/s/resource/wiktionary/en", "process": "/s/process/wikiparsec/1"}], "weight": 1.0}
	
	This 
	"""
	
	OW = lambda fn: open(fn, 'w', encoding='utf-8')
	with open(CNET_FILE_ORIG, encoding='utf-8') as inf, OW(CNET_FILE_PP) as of, OW('cnet-conversion-log.txt') as logf:
		for lii, li in tqdm(enumerate(inf)):
			li = li.strip()
			if lii%10000 == 0:
				logf.write("[progress] line=%d\n" % lii)
			parts = li.strip().split("\t", 4)
			if len(parts) != 5:
				logf.write("[warning] len(parts) != 5 @ line=%d\n" % lii)
				continue
			synok = all([parts[1].startswith('/r/'), parts[2].startswith('/c/'), parts[3].startswith('/c/')])
			if not synok:
				logf.write("[warning] synok not True @ line=%d\n" % lii)
				continue
			
			all_en = all([parts[2].startswith('/c/en/'), parts[3].startswith('/c/en/')])
			if not all_en: continue
			
			r = parts[1]
			s, o = [x.replace('/c/en/', '', 1).split('/', 1)[0] for x in parts[2:4]]
			
			#of.write('%s\t%s\t%s\t%s\n' % (r,s,o,parts[4]))
			of.write('%s\t%s\t%s\n' % (r,s,o))
		
if not path.exists(CNET_FILE_PP):
	make_pp_cnet_file()
	
cnet_dict = load_cnet()
