import nltk
import re
import gzip
import dircache

gzip_path = "train/docs/"
pp_path = "train/docs_proc/"
ner_path = "train/ner/"

def preprocess(infile, outfile):
    """
    Runs all necessary preprocessing on a file so that it can be
    run through our QA system

    params
    ----
    infile: input filename path of a raw document
    outfile: output filename path of preprocessed infile
    """
    tagger(infile, outfile)

def get_gzip_data(filename):
    """Read data from gzip file.

    param
    ----
    filename: Input gzip file.
    """
    with gzip.open(filename, "rb") as f:
        data = f.read()
    return data

def tagger(infile, outfile):
    """
    takes an input file path infile of a raw document
    returns POS tagged version of the infile to the outfile path

    param
    ----
    infile: input filename path of a raw document
    outfile: output filename path of POS tagged infile in the format
    WORD_TOKEN POS_TAG
    """
    # input the file
    doc = get_gzip_data(infile)
    strip_html_p = re.compile(r'<.*?>')
    btwn_text_p = re.compile('(<DOCNO>((.|\n)*?)</DOCNO>|<TEXT>((.|\n)*?)</TEXT>)')

    text_list = btwn_text_p.findall(doc)
    docs = {}
    docn = None
    for tup in text_list:
        if "<DOCNO>" in tup[0]:
            docn = tup[1].strip()
            docs[docn] = ""
        else:
            docs[docn] = docs[docn] + tup[3]

    # output the file
    tagged_output = ""
    for (docn,text) in docs.items():
        docs[docn] = strip_html_p.sub('', text)
        tagged_output = tagged_output + "<DOCNO> " + docn + "\n"
        sentences = nltk.sent_tokenize(docs[docn])
        for sent in sentences:
            tokens = nltk.word_tokenize(sent)
            tagged_text = nltk.pos_tag(tokens)
            output = "\n".join("%s %s" % tup for tup in tagged_text)
            tagged_output = tagged_output + output + "\n"
        tagged_output = tagged_output + "\n"
    
    final_output = preprocess_postext(tagged_output)
    open(outfile, 'w').write(final_output)

def tag_file_by_num(file_num, outfile):
    """
    POS tags and otherwise processes the gzip file number specified and
    returns in the output file with the extension .pos in the
    outfile, or does nothing if the file is found to have already
    been tagged

    param
    ----
    file_num: number of document to be processed
    outfile: output file name

    """
    ner_file = ner_path + "top_docs." + str(file_num)
    pp = dircache.listdir(pp_path)
    for pp_file in pp:
        if str(file_num) in pp_file:
            return (pp_path + pp_file, gzip_path+"top_docs."+str(file_num)+".gz", ner_file)

    gzips = dircache.listdir(gzip_path)
    for gzip in gzips:
        if str(file_num) in gzip:
            preprocess(gzip_path + gzip, pp_path + outfile)
            return (pp_path + outfile, gzip_path + gzip, ner_file)

def tag_file_by_name(filename, outfile):
    """
    POS tags and otherwise processes the gzip file specified and
    returns in the output file with the extension .pos in the
    outfile, or does nothing if the file is found to have already
    been tagged

    param
    ----
    file_num: name of document to be processed
    outfile: output file name

    """
    regex = re.compile('[0-9]+')
    file_num = int(regex.search(filename).group(0))
    nerfile = ner_path + "top_docs." + str(file_num)
    pp = dircache.listdir(pp_path)
    for pp_file in pp:
        if str(file_num) in pp_file:
            return (gzip_path + filename, pp_path+pp_file, nerfile, file_num)

    preprocess(gzip_path + filename, outfile)
    return (gzip_path + filename, outfile, nerfile, file_num)

def preprocess_nefile(nefile, outfile):
    doc = open(nefile, 'r').read()
    m_text = re.compile('(<DOCNO>((?:.|\n|\r)+?)</DOCNO>|<TEXT>((?:.|\r|\n)+?)</TEXT>)')
    results = m_text.findall(doc)
    m_ent = re.compile('((?:[^>])*)<(.+?)>((?:.|\n|\r)+?)</.+?>((?:[^<])*)')
    output = ""
    for r in results:
        if "<DOCNO>" in r[0]:
            docid = r[1].strip()
            output = output + docid + " <DOCNO>\n"
        else:
            text = r[2]
            sents = nltk.sent_tokenize(text)
            for sent in sents:
                results_ent = m_ent.findall(sent)
                for (prev, ne, ent, post) in results_ent:
                    if not prev.strip() == "":
                        output = output + "\n".join("%s %s" % (w, "<NA>") for w in prev.strip().split()) + "\n"
                    if not ent.strip() == "":
                        output = output + "_".join(ent.strip().split()) + " <" +  ne + ">\n"
                    if not post.strip() == "":
                        output = output + "\n".join("%s %s" % (w, "<NA>") for w in post.strip().split()) + "\n"
    open(outfile, 'w').write(output)

def preprocess_nefiles(nedir, outdir):
    pp = dircache.listdir(nedir)
    regex = re.compile('[0-9]+')
    for nefile in pp:
        file_num = regex.search(nefile).group(0)
        preprocess_nefile(nedir + nefile, outdir + "top_docs." + file_num + ".ne")

def preprocess_posfile(pfile, ofile):
    doc = open(pfile, 'r').read()
    output = preprocess_postext(doc)
    open(ofile, 'w').write(output)

def preprocess_postext(doc):
    toks = doc.strip().split()
    wtoks = toks[::2]
    ptoks = toks[1::2]
    size = len(wtoks)
    output = ""
    pos = None
    ent = ""
    for i in xrange(0,size):
        if wtoks[i] == "<DOCNO>":
            docid = ptoks[i]
            output = output + docid + " <DOCNO>\n"
        elif ptoks[i] == pos:
            ent = ent + "_" + wtoks[i]
            continue
        else:
            if not ent == "":
                output = output + ent + " <" + pos + ">\n"
            ent = wtoks[i]
            pos = ptoks[i]
    output = output + ent + " <" + pos + ">\n"
    return output

def preprocess_posfiles(indir, outdir):
    pp = dircache.listdir(indir)
    regex = re.compile('[0-9]+')
    for f in pp:
        file_num = regex.search(f).group(0)
        preprocess_posfile(indir + f, outdir + "top_docs." + file_num + ".pos")
