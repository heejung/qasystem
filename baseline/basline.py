import re
import heapq
import dircache

def posdocs(indirpath):
    infiles = dircache.listdir(indirpath)
    posfiles = [infile for infile in infiles if ".pos" in infile]
    return posfiles

def top_NNPs(n, qn, indir, posfiles, real_qn):
    candidates = {}
    candidates = answer(real_qn, indir + posfiles[qn], candidates)

    answers = heapq.nlargest(n, candidates, key=candidates.get)

    output = ""
    str_qn = str(real_qn)
    for ans in answers:
        (freq, docids) = candidates[ans]
        output = output + str_qn + " " + docids.iterkeys().next() + " " + ans + "\n"
    return output #add to take care of NIL
    
def output(outfile, ans):
    open(outfile, 'w').write(ans)

def run(indir, outfile, n, qmax):
    posfiles = posdocs(indir)
    ans = ""
    for qn in xrange(0,qmax):
        ans = ans + top_NNPs(n, qn, indir, posfiles, qn+201) + "\n"
    output(outfile, ans)

def answer(real_qn, posfile, candidates):
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

run("/Users/jollifun/NLP/pro4/posdocs2/", "/Users/jollifun/NLP/pro4/myanswers.txt", 5, 74)
