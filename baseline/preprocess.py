import nltk
import re
import gzip
import dircache

gzip_path = "train/docs/"
pp_path = "train/docs_proc/"

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
        
    open(outfile, 'w').write(tagged_output)

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
    pp = dircache.listdir(pp_path)
    for pp_file in pp:
        if str(file_num) in pp_file:
            return (pp_path + pp_file)

    gzips = dircache.listdir(gzip_path)
    for gzip in gzips:
        if str(file_num) in gzip:
            preprocess(gzip_path + gzip, pp_path + outfile)
            return (pp_path + outfile)

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
    pp = dircache.listdir(pp_path)
    for pp_file in pp:
        if str(file_num) in pp_file:
            return (pp_file, file_num)

    preprocess(gzip_path + filename, outfile)
    return (outfile, file_num)