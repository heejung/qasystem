from baseline import top_NNPs

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
    # weights is the ordered record of how individual algorithms fare.
    # This value must have length that corresponds to number of algos used.
    weights = [1, .5]

    # representation of the output of each used algorithm
    algos = []

    # when adding a new algorithm, add a step exactly as below,
    # in the same position as the corresponding weight in weights above
    algos += [top_NNPs(n, posfile, qn)]
    algos += [[(.5, "_"), (.9, "_"), (1.3, "_"), (1.7, "_"), (2.1,"this should appear\n")]]

    # reconfigures confidences based on weights for each algo
    for i in range(0, len(algos)):
        for j in range(0, len(algos[i])):
            algos[i][j] = (algos[i][j][0]*weights[i], algos[i][j][1])

    # adds all (confidence, string) pairs into one list, sorts based on confidence
    # with the highest confidence appearing first
    tups = []
    for algo in algos:
        for tup in algo:
            tups += [tup]
    tups.sort(key=lambda tup: tup[0])
    tups.reverse()

    # populates returns with the up to the first 5 unique strings featured in tups,
    # returning nil if returns is empty
    returns = []
    i = 0
    while i < len(tups) and len(returns) < 5:
        if tups[i][1] not in returns:
            returns += [tups[i][1].strip()]
        i += 1
    if returns == []:
        return 'nil'
    else:
        return '\n'.join(returns)
                
    
