import re
import heapq

def best_guess(n, posfile, qn, question):
    """
    returns a formatted string representing the best five guesses
    for the question corresponding to the input POS file

    params
    ----
    n = number of guesses to be returned
    posfile = formatted POS file in which data will be found
    qn = question number that is being answered
    question = the string representing the question being asked.

    Note: the question input is not supported at this time 
    """
    return top_NNPs(n, posfile, qn)

def top_NNPs(n, posfile, qn):
    """
    returns the n most frequently occuring proper nouns found in
    the training corpus.

    params
    ----
    n = number of responses
    posfile = formatted POS file of training corpus
    qn = absolute question number being answered
    """
    candidates = {}
    candidates = answer(posfile, candidates)

    answers = heapq.nlargest(n, candidates, key=candidates.get)

    output = ""
    str_qn = str(qn)
    for ans in answers:
        (freq, docids) = candidates[ans]
        output = output + str_qn + " " + docids.iterkeys().next() + " " + ans + "\n"
    return output #add to take care of NIL

def answer(posfile, candidates):
    """
    generates a dictionary of proper nouns found in the
    corpus where dict{NNP} -> count of that NNP in corpus

    params
    ----
    posfile = formatted data file
    candidates = dictionary at time of input
    """
    text = open(posfile, 'r').read()
    p_nnp = re.compile('(<DOCNO>(.*?)\n|(.*?)(?=NNP))')
    nnps = p_nnp.findall(text)
    docid = ""
    for tup in nnps:
        if "<DOCNO>" in tup[0]:
            docid = tup[1].strip()
            continue
        nnp = tup[2].strip()
        if nnp=="" or not re.match("^[A-Za-z0-9-]*$", nnp):
            continue
        if candidates.has_key(nnp):
            (freq, docids) = candidates[nnp]
            docids[docid] = 1
            candidates[nnp] = (freq+1, docids)
        else:
            candidates[nnp] = (1, {docid:1})
    return candidates
