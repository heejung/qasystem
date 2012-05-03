import re, heapq
from nltk import stem, corpus, sent_tokenize, word_tokenize
import utils
from preprocess import get_gzip_data

"""
Class CollocationAlgo 
    Uses named entities, POS tags, and basic collocation method
    in order to retrieve the answer candidates to the
    given question. Ranks the answer candidates by computing
    their confidence scores. The confidence scores are computed
    by counting the number of words that match the words in the given
    question, within the defined window frame
    before and after the answer candidate in the corpus where the
    answer candidate is found.
"""
class CollocationAlgo:
    def __init__(self):
        """
        windowSize: the window size for collocation consideration
        answerSize: number of words allowed for an answer
        stopWords: a dictionary of stopwords
        stemmer: nltk Lancaster Stemmer. Example stemming:
             original string:
             Stemming is funnier than a bummer says the sushi loving computer scientist, Bob's wife.
             stemmed string:
             stem is funny than a bum say the sush lov comput sci , bob ' s wif .
        """
        self.windowSize = 10
        self.answerSize = 10
        self.stopWords = utils.list2dict(corpus.stopwords.words('english'))
        self.stemmer = stem.LancasterStemmer()
  
    def run_colloc(self, question, dfile, n):
        """
        params
        ----
            question: string of question
            dfile: the original answer data file in gzip format
            n: the numer of top answer candidates to return

        returns the list of tuples (float of confidence score,
                                    string of docid + answer)
        """
        qdict = utils.list2dict(self.preprocess(question))
        top_n_cands = self.get_colloc_words(dfile, n, qdict)
        top_n_anses = self.shrink_answer_size(top_n_cands, qdict, self.answerSize)
        return top_n_anses

    def run_ne(self, question, ne_type, nefile, n):
        """
        param
        ----
            question: the question string
            ne_type: the named_entity tag we are looking for
            nefile: the data file that has been tagged with named entities.
            n: number of top answer candidates to return
        
            returns a list of tuples in the following format:
                (confidence score, string of docid + answer)
        """
        print "start ne"
        ents = self.get_colloc_words_ne(ne_type, nefile, self.windowSize)
        print "start ne scoring"
        return self.score_ents(ents, question, n)

    def run_pos(self, question, pos, posfile, n):
        """
        Uses POS tag information to find the answer to a given question
        """
        print "start pos"
        ents = self.get_colloc_words_pos(pos, posfile, self.windowSize)
        print "score pos"
        return self.score_ents(ents, question, n)


    def get_colloc_words_pos(self, pos_type, posfile, nwords):
        postag = "<" + pos_type + ">"
        return self.get_colloc_words_tag(postag, posfile, nwords, 3)

    def get_colloc_words(self, datafile, numcands, qdict):
        """
        params
        ----
            datafile: the original datafile
            numcands: number of answer candidates to return

        returns a list of tuples (string of "docid answer",
                                  float of confidence score)
        """
        doc = get_gzip_data(datafile)
        p_text = re.compile('(<DOCNO>((.|\n|\r)*?)</DOCNO>|<TEXT>((.|\r|\n)*?)</TEXT>)') 
        m_strip_tags = re.compile(r'<.*?>')
        docids_texts = p_text.findall(doc)
        candidates = []
        docn = None
        for tup in docids_texts:
            if "<DOCNO>" in tup[0]:
                 docn = tup[1].strip() + " "
            else:
                text = m_strip_tags.sub('', tup[3])
                if len(text) == 0:
                    continue
                sents = sent_tokenize(text)
                for sent in sents:
                    wtoks = self.preprocess(sent)
                    score = self.score_from_words(wtoks, qdict)
                    if len(candidates) < numcands:
                        heapq.heappush(candidates, (score, docn + sent))
                    else:
                        heapq.heappushpop(candidates, (score, docn + sent))
        return candidates

    def shrink_answer_size(self, candidates, qdict, anssize):
        shrinkeds = []
        for (sc, docn_cand) in candidates:
            docn, cand=docn_cand.split(' ',1)
            wtoks = self.strip_stop_words(cand)
            processedtoks = self.preprocess(cand)
            size = len(wtoks)
            shrinked = []
            for idx in xrange(0,size):
                if not qdict.has_key(processedtoks[idx]):
                    shrinked.append(wtoks[idx])
            size = len(shrinked)
            if size > anssize:
                subshrinked = shrinked[(size-anssize):]
                shrinked = subshrinked
            ans = docn + " " + " ".join(shrinked)
            shrinkeds.append((sc, ans))
        shrinkeds.reverse()
        return shrinkeds

    def get_colloc_words_ne(self, ne_type, nefile, n):
        """
        returns a list of n words containing the named entity type
        ne_type from nefile which is already tagged with named entities
        and processed to have a tuple of a word and an NE tag per line
        in the document file.
        """
        netag = "<" + ne_type + ">"
        return self.get_colloc_words_tag(netag, nefile, n, 0)

    def get_colloc_words_tag(self, tag, dfile, n, add):
        doc = open(dfile, 'r').read()
        toks = doc.strip().split()
        wtoks = toks[::2]
        ttoks = toks[1::2]
        size = len(wtoks)
        entities = {}
        docidx = 0
        for i in xrange(0,size):
            if ttoks[i] == "<DOCNO>":
                docid = wtoks[i]
                docidx = i
            elif ttoks[i] == tag:
                ent = " ".join(wtoks[i].split('_'))
                if add > 0:
                   iadd = i+add
                   if iadd >= size:
                       iadd = size
                   if "<DOCNO>" in ttoks[i+1:iadd]:
                       iadd = ttoks.index("<DOCNO>")
                   ent = ent + " " + " ".join(wtoks[i+1:iadd])
                iprev = i - n
                if iprev < 0:
                    iprev = 0
                if iprev <= docidx:
                    iprev = docidx + 1
                ipost = i + n
                if ipost >= size:
                    ipost = size
                if "<DOCNO>" in ttoks[i+1:ipost]:
                    ipost = ttoks.index("<DOCNO>")
                prev = " ".join(wtoks[iprev:i])
                post = " ".join(wtoks[i+1:ipost])
                entities[ent] = (docid, prev + " " + post)

        return entities

    def score_ents(self, ents, question, n):
        """
        Computes the confidence scores for each entity answer candidate to the given question.

        params
        ----
            ents: dict of key: entity answer string
                          value: tuple (string docid,
                                        string of words before & after the answer string)
            question: string of question to be answered
            n: number of answer candidates to be returned

        returns list of tuple (string of target entity token -- the answer candidate,
                               float of confidence score)
        """
        candidates = []
        qtoks = self.preprocess(question)
        qdict = utils.list2dict(qtoks)
        for (ent, (docid, colloc_words)) in ents.items():
            if not (ent in question):
                wtoks = self.preprocess(colloc_words)
                score = self.score_from_words(wtoks, qdict)
                size = len(candidates)
                ans = (score, docid + " " + ent)
                if size >= n:
                    heapq.heappushpop(candidates, ans)
                else:
                    heapq.heappush(candidates, ans)
        candidates.reverse()
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
            
    def score_from_words(self, wtoks, qdict):
        """
        Computes the confidence score from word tokens.
        """
        score = 0.
        for w in wtoks:
            if qdict.has_key(w):
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
        tokens = word_tokenize(string)
        stripped = []
        for t in tokens:
            if t=="" or not re.match("^[A-Za-z0-9-_]*$", t):
                continue
            t_lowered = t.lower()
            if not self.stopWords.has_key(t_lowered):
                stripped.append(t)
        return stripped

#nea = CollocationAlgo()
#cands = nea.run_ne("Where is Belize located?", "LOCATION", "train/ne_final/top_docs.202.ne", 5)
#print cands

#cands = nea.run_colloc("Where is Belize located?", "/Users/jollifun/Downloads/train/top_docs.202.gz", 5)
#print cands

#cands = nea.run_pos("When did the vesuvius last erupt?", "CD", "train/pos_final/top_docs.230.pos", 10)
#print cands
