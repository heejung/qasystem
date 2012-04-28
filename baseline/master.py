import dircache
from decision import best_guess
from preprocess import tag_file_by_name, tag_file_by_num
from categorize import CategorizeQs

# qa = CategorizeQs()
# dic = qa.get_qtypes("questions.txt")
# dic["question number"] will now return ('question', 'question type')

def run_files_in_range(start, stop, outfile, n):
    """
    executes run_file on all question numbers in [start, stop]
    Note: to do one file, have start and stop be the same number.

    params
    ----
    start = the first question to be processed
    stop = the last question to be processed
    Note: this is inclusive - both start and stop, as well as all
    numbers in between, will be processed

    outfile = path to the file that results will be written to
    n = number of top guesses per question
    """
    ans = ""
    for i in range(start, stop+1):
        ans += run_file(i, n) + "\n\n"
    output(outfile, ans)

def run_file(file_num, n):
    """
    takes a single question number and performs question-answering on that
    question

    params
    ----
    file_num = number of question being answered
    outfile = filepath for the results of QA
    n = number of answers desired
    """
    posfile = tag_file_by_num(file_num, "top_docs."+str(file_num)+".pos")
    ans = best_guess(n, posfile, file_num, None)
    return ans

def run_dir(indirpath, outdirpath, answerfile, n):
    """
    takes a directory containing gzip files of informative articles
    and preprocesses them (if necessary) and performs QA on them

    params
    ----
    indirpath = directory containing gzip files
    outdirpath = directory that preprocessed files should be written to
    answerfile = file path that results of QA should be output to
    n = number of answers desired per question
    """
    infiles = dircache.listdir(indirpath)
    ans = ""
    for infile in infiles:
        if ".gz" in infile:
            outpath = outdirpath+infile+".pos"
            (posfile, qn) = tag_file_by_name(infile, outpath)
            ans += best_guess(n, posfile, qn, None) + "\n\n"
    output(answerfile, ans)

def output(outfile, ans):
    """
    writes output

    params
    ----
    outfile = path to write answers to
    ans = answer to be written
    """
    open(outfile, 'w').write(ans)

run_dir("train/docs/", "train/docs_proc/", "train/results/test.txt", 5)
