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
    btwn_text_p = re.compile('<TEXT>((.|\n)*?)</TEXT>')

    #doc_stripped = strip_html_p.sub('', doc)
    text_list = btwn_text_p.findall(doc)
    texts_stripped = ' '.join("%s" % tup[0] for tup in text_list)
    doc_stripped = strip_html_p.sub('', texts_stripped)
    text = nltk.word_tokenize(doc_stripped)
    tagged_text = nltk.pos_tag(text)

    # output the file
    output = "\n".join("%s %s" % tup for tup in tagged_text)
    open(outfile, 'w').write(output)

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

#tag_dir("/Users/jollifun/Downloads/train/docs/", "/Users/jollifun/NLP/pro4/posdocs/")
