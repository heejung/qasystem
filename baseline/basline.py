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
    return "\n".join(answers) #add to take care of NIL
    
def output(outfile, ans):
    open(outfile, 'w').write(ans)

def run(indir, outfile, n, qmax):
    posfiles = posdocs(indir)
    ans = ""
    for qn in xrange(0,qmax):
        ans = ans + top_NNPs(n, qn, indir, posfiles, qn+201) + "\n\n"
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
        if nnp=="":
            continue
        ans = str(real_qn) + " " + docid + " " + nnp
        if candidates.has_key(ans):
            candidates[ans] += 1
        else:
            candidates[ans] = 1
    return candidates

run("/Users/jollifun/NLP/pro4/posdocs2/", "/Users/jollifun/NLP/pro4/myanswers.txt", 5, 18)
