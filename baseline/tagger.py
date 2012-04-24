import nltk
import re
import gzip
import dircache

def get_gzip_data(filename):
    """Read daa from gzip file.

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
        
    open(outfile, 'w').write(tagged_output)
    
def tag_dir(indirpath, outdirpath):
    """
    POS tags all the gzip files in indirpath directory and
    returns them in the output files with the extension .pos in the
    outdirpath directory.

    param
    ----
        indirpath: directory path with all the inputfiles
        outdirpath: output directory path

    """
    infiles = dircache.listdir(indirpath)
    for infile in infiles:
        if ".gz" in infile:
            tagger(indirpath + infile, outdirpath + infile + ".pos")

tag_dir("/Users/jollifun/Downloads/train/docs/", "/Users/jollifun/NLP/pro4/posdocs2/")
