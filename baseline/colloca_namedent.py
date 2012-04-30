import re
from nltk import stem, corpus

"""
Class NamedEntAlog
    Uses named entities to retrieve the answer candidates to the
    given question. Ranks the answer candidates by computing
    their confidence scores. The confidence scores are computed
    by counting the number of words that match the words in the given
    question, within the defined window frame
    before and after the answer candidate in the corpus where the
    answer candidate is found.
"""
class NamedEntAlgo:
    def __init__(self):
        """
        windowSize: the window size for collocation consideration
        stopWords: a dictionary of stopwords
        stemmer: nltk Lancaster Stemmer. Example stemming:
             original string:
             Stemming is funnier than a bummer says the sushi loving computer scientist, Bob's wife.
             stemmed string:
             stem is funny than a bum say the sush lov comput sci , bob ' s wif .
        """
        self.windowSize = 10
        self.stopWords = self.list2dict(corpus.stopwords.words('english'))
        self.stemmer = stem.LancasterStemmer()
   
    def list2dict(self, lst):
        """
        Converts a list to a dictionary
        """
        dct = {}
        for w in lst:
            dct[w] = 1
        return dct
    
    def run_ne(self, question, ne_type, nefile):
        """
        param
        ----
            question: the question string
            ne_type: the named_entity tag we are looking for
            nefile: the data file that has been tagged with named entities.
        
            returns a list of tuples in the following format:
                (answer string, confidence score)
        """
        ents = self.get_colloc_words(ne_type, nefile, self.windowSize)
        return self.score_ents(ents, question)

    def get_colloc_words(self, ne_type, datafile, n):
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
        """
        Computes the confidence scores for each entity answer candidate to the given question.

        params
        ----
            ents: list of tuple (string of self.windowSize number of words before the target entity token,
                                 string of target entity token -- the answer candidate,
                                 string of self.windowSize number of words after the target entity token)
            question: string of question to be answered

        returns list of tuple (string of target entity token -- the answer candidate,
                               float of confidence score)
        """
        candidates = []
        qtoks = self.preprocess(question)
        qdict = self.list2dict(qtoks)
        for (prev_words, ent, post_words) in ents:
            prev_toks = self.preprocess(prev_words)
            score = self.score_from_words(prev_toks, qdict)
            post_toks = self.preprocess(post_words)
            score += self.score_from_words(post_toks, qdict)
            candidates.append((ent, score))
        candidates.sort()
        return candidates

    def preprocess(self, string):
        """
        Preprocesses the string by stripping it of the stop words,
        stemming it, and lowercasing it.

        params
        ----
            string: string of words to be preprocessed.

        returns a list of token string preprocessed.
        """
        stripped_toks = self.strip_stop_words(string)
        processed_toks = [self.stemmer.stem(t) for t in stripped_toks]
        return processed_toks 
            
    def score_from_words(self, wtoks, qtoks):
        """
        Computes the confidence score from word tokens.
        """
        score = 0.
        for w in wtoks:
            if qtoks.has_key(w):
                score += 1.
        return score

    def strip_stop_words(self, string):
        """
        Strip the string of stopwords.
        
        params
        ----
            string: string of words

        returns a list of token strings excluding stop words.
        """
        tokens = string.strip().split()
        stripped = []
        for t in tokens:
            t_lowered = t.lower()
            if not self.stopWords.has_key(t_lowered):
                stripped.append(t)
        return stripped

#nea = NamedEntAlgo()
#cands = nea.get_colloc_words("PERSON", "/Users/jollifun/NLP/pro4/ex1.ner", 10)
#print nea.score_ents(cands, "Who invented the paper clip?")
