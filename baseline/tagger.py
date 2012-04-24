import nltk
import re
import gzip
import dircache

PRONOUN = "NNP"

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
    btwn_text_p = re.compile('(<DOCNO>(.*?)</DOCNO>|<TEXT>((.|\n)*?)</TEXT>)')

    #doc_stripped = strip_html_p.sub('', doc)
    text_list = btwn_text_p.findall(doc)
    docs = {}
    docn = None
    for tup in text_list:
        if "<DOCNO>" in tup[0]:
            docn = tup[1].strip()
            docs[docn] = ""
            print tup[1]
        else:
            print docn
            docs[docn] = docs[docn] + tup[2]

    #texts_stripped = ' '.join("%s" % tup[0] for tup in text_list)

    tagged_output = ""
    for (docn,text) in docs.items():
        docs[docn] = strip_html_p.sub('', text)
        tokens = nltk.word_tokenize(docs[docn])
        tagged_output = "<DOCNO> " + docn + "\n"
        tagged_text = nltk.pos_tag(tokens)
        output = "\n".join("%s %s" % tup for tup in tagged_text)
        tagged_output = tagged_output + output + "\n\n"
        
    open(outfile, 'w').write(tagged_output)

    # output the file
    

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
