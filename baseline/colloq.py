import re

"""
Class NamedEntAlog
    Using named entities to retrieve the candidate answers to the
    given question.
"""
class NamedEntAlgo:
    def __init__(self):
        self.windowSize = 10
        self.stopWords = {"is":1, "it":1, "the":1, "who":1, "what":1, "when":1, "where":1, "how":1, "was":1, "were":1, "you":1, "are":1}

    """
    param
    ----
        question: the question string
        ne_type: the named_entity tag we are looking for
        nefile: the data file that has been tagged with named entities.
    
        returns a list of tuples in the following format:
            (answer string, confidence score)
    """
    def run_ne(self, question, ne_type, nefile):
        ents = self.get_colloq_words(ne_type, nefile, self.windowSize)
        return self.score_ents(ents, question)

    def get_colloq_words(self, ne_type, datafile, n):
        """
        returns a list of n words containing the named entity type
        ne_type from datafile which is already tagged with named entities
        """

        doc = open(datafile, 'r').read()
        p_n_words = "((?:(?:^|\s)+\S+){0," + str(n) + "}\s*)"
        m_ne = re.compile(p_n_words + "<" + ne_type + ">(.*?)</" + ne_type + ">" + p_n_words)
        result = m_ne.findall(doc)
        
        m_strip_tags = re.compile(r'<.*?>')
        entities = []
        for (first_nwords, ent, last_nwords) in result:
            tup = (m_strip_tags.sub('',first_nwords).strip(), ent, m_strip_tags.sub('',last_nwords).strip())
            entities.append(tup)

        return entities

    def score_ents(self, ents, question):
        candidates = []
        qtoks = self.strip_stop_words(question)
        for (prev_words, ent, post_words) in ents:
            score = self.score_from_words(prev_words, qtoks)
            score += self.score_from_words(post_words, qtoks)
            candidates.append((ent, score))
        candidates.sort()
        return candidates
            
    def score_from_words(self, words, qtoks):
        wtoks = words.split()
        score = 0.
        for w in wtoks:
            w_low = w.lower().strip()
            if not self.stopWords.has_key(w_low):
                if qtoks.has_key(w_low):
                    score += 1.
        return score

    def strip_stop_words(self, string):
        tokens = string.strip().split()
        stripped = {}
        for t in tokens:
            t_lowered = t.lower()
            if not self.stopWords.has_key(t_lowered):
                stripped[t] = 1
        return stripped

#nea = NamedEntAlgo()
#cands = nea.get_colloq_words("PERSON", "/Users/jollifun/NLP/pro4/ex1.ner", 10)
#print nea.score_ents(cands, "Who invented the paper clip?")
