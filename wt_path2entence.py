def camel_case_split(str, lower=False):
	"""Split a camel-case string to its constituents, and return their list.
	
	Example: HasA --> ['Has', 'A']
	"""
	words = [[str[0]]]
  
	for c in str[1:]:
		if words[-1][-1].islower() and c.isupper():
			words.append(list(c))
		else:
			words[-1].append(c)
	if lower:
		return [''.join(word).lower() for word in words]
	else:
		return [''.join(word) for word in words]

""" A dictionary used by function triple_to_sentence_part to translate a triple to an English clause.

???Each 'x' in the dictionary values represents a camel-case part of the corresponding relation in the dictionary key.
Code??? '%s' is the placeholder for subject of the triple and '%o' is for its object. 
"""
sentence_parts_dict = {
	'/r/FormOf': 'isaxx',
	'/r/SymbolOf': 'isaxx',
	'/r/DefinedAs': 'isxx',
	'/r/SimilarTo': 'isxx',
	'/r/IsA': 'xa',
	'/r/PartOf': 'isaxx',
	'/r/HasA': 'xa',
	'/r/HasProperty': "%s can be described as %o",
	'/r/MannerOf': "%s is a specific way to do %o",
	'/r/MadeOf': 'isxx',
	'/r/UsedFor': 'isxx',
	'/r/CapableOf': 'isxx',
	'/r/AtLocation': 'isxx',
	'/r/Causes': 'x',
	'/r/HasSubevent': "%s includes %o",
	'/r/HasFirstSubevent': "%s begins with %o",
	'/r/HasLastSubevent': "%s ends with %o",
	'/r/HasPrerequisite': "%s needs %o",
	'/r/MotivatedByGoal': "%s is done for %o",
	'/r/ObstructedBy': "%s is prevented by %o",
	'/r/Desires': 'x',
	'/r/CreatedBy': 'isxx',
	'/r/LocatedNear': 'isxx',
	'/r/ReceivesAction': "%o can be done on %s",
	'/r/CausesDesire': "%s makes someone want be %o",
	'/r/RelatedTo': 'isxx',
	'/r/DistinctFrom': 'isxx',
	'/r/HasContext': "%s is used in the context of %o",
}

	
def triple2clause(s, orig_r, o):
	"""Return a natural-language string representation of triple (s, orig_r, o)."""
	p = sentence_parts_dict[orig_r]
	r = orig_r.replace('/r/', '')
	decamle = camel_case_split(r, lower=True)
	aan = 'an' if o[0] in 'aeiuo' else 'a'
	if '%' in p:
		return (p % s).replace('%o', '%s') % o
	elif p == 'isaxx': return s + ' is ' + aan + ' ' + decamle[0] + ' ' + decamle[1] + ' ' + o
	elif p == 'isxx': return s + ' is ' + decamle[0] + ' ' + decamle[1] + ' ' + o
	elif p == 'xa': return s + ' ' + decamle[0] + ' ' + aan  + ' ' + o
	elif p == 'xx': return s + ' ' + decamle[0] + ' ' + decamle[1] + ' ' + o
	elif p == 'x': return s + ' ' + decamle[0] + ' ' + o
	else: return None


def path2sentence(p):
	"""Return a natural-language string representation of path p.
	
	Input:
	p -- a list in the form of [[(e0, r0), (e1, r1), ...], eN]. rs should be in sentence_parts_dict defined above.
	
	Example:
	[[('Jack', '/r/HasA'), ('book', '/w/IsA')], 'object'] --> 'Jack has a book, and book is an object.'"""
	es = [(s, r, o) for (s,r),(o, _) in zip(p[0], p[0][1:])]
	s, r = p[0][-1]
	es.append((s, r, p[1]))
	clauses = []
	for e in es:
		clause = triple2clause(*e)
		if clause is not None:
			clauses.append(clause)
	
	return ', and '.join(clauses) + '.'
