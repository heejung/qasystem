from baseline import top_NNPs
from collocation import CollocationAlgo
import re

ner_questions_file = "train/ner/questions.txt"

def best_guess(n, nefile, posfile, gzfile, qn, question):
    """
    returns a formatted string representing the best five guesses
    for the question corresponding to the input POS file

    params
    ----
    n = number of guesses to be returned
    posfile = formatted POS file in which data will be found
    qn = question number that is being answered
    question = tuple of:  (string representing the question being asked, question type)

    Note: the question input is not supported at this time 
    """
    num_responses = 5
    colloc_algo = CollocationAlgo()
    # weights is the ordered record of how individual algorithms fare.
    # This value must have length that corresponds to number of algos used.
    baseline_weight = 1
    ner_weight = 1
    colloc_weight = 1
    pos_weight = 1
    weights = [baseline_weight, ner_weight, colloc_weight, pos_weight]
    algo_names = ["BASELINE", "NER", "COLLOC", "POS"]


    # logic for determining whether or not to use the named entity collocation,
    # and if so which named entity to pass to the algo
    ne = None
    if question[1] in ["who", "where", "when"]:
        f = open(ner_questions_file)
        tmp = f.readline()
        while tmp:
            if str(qn) in tmp:
                for i in range(0, 3):
                    tmp = f.readline()
                    tmp = tmp.strip()
                break
            tmp = f.readline()
        if question[1] == "who":
            ne = ["PERSON", "ORGANIZATION"]
        elif question[1] == "where":
            ne = ["LOCATION", "ORGANIZATION"]
        else:
            ne = ["DATE"]

    # logic to determine whether or not to use the POS algo, and if so what
    # POS to pass along
    pos = None
    if question[1] in ["how much", "population", "when"]:
        pos = "CD"

    # representation of the output of each used algorithm
    algos = []

    # when adding a new algorithm, add a step exactly as below,
    # in the same position as the corresponding weight in weights above
    algos += [(0, top_NNPs(n, posfile, qn))]
    if ne:
        for word in ne:
            algos += [(1, colloc_algo.run_ne(question[0], word, nefile, num_responses))]
    algos += [(2, colloc_algo.run_colloc(question[0], gzfile, num_responses))]
    if pos:
        for word in pos:
            algos += [(3, colloc_algo.run_pos(question[0], word, posfile, num_responses))]


    # reconfigures confidences based on weights for each algo
    for i in range(0, len(algos)):
        for j in range(0, len(algos[i][1])):
            algos[i][1][j] = (algos[i][1][j][0]*weights[algos[i][0]], str(qn)+" "+algo_names[algos[i][0]]+": " +algos[i][1][j][1])

    # adds all (confidence, string) pairs into one list, sorts based on confidence
    # with the highest confidence appearing first
    tups = []
    for algo in algos:
        for tup in algo[1]:
            tups += [tup]
    tups.sort(key=lambda tup: tup[0])
    tups.reverse()

    # populates returns with the up to the first 5 unique strings featured in tups,
    # returning nil if returns is empty
    returns = []
    # i = 0
    # while i < len(tups) and len(returns) < 5:
    #     if tups[i][1] not in returns:
    #         returns += [tups[i][1].strip()]
    #     i += 1
    for tup in tups:
        returns += [tup[1].strip()]
    if returns == []:
        return 'nil'
    else:
        return '\n'.join(returns)
                
    
# print best_guess(5, 'train/ner/top_docs.201', 'train/docs_proc/top_docs.201.gz.pos', 'train/docs/top_docs.201.gz', 201, ("what is my name?", "what"))
