import re
"""
  Categorize Questions into 6 different question types:
      what, who, where, when, how, misc(miscellaneous)
"""
class CategorizeQs:

    def __init__(self):
        self.categories = {"what":1, "who":2, "where":3, "when":4, "how":5, "misc":6,
                           "how much":7, "is/was":8, "are/were":9, "population":10,
                           "do/does/did":11, "name":12, "why":13}

    def categorize_q(self, question):
        words = re.compile("\W").split(question.lower())
        firstword = words[0]
        if self.categories.has_key(firstword):
            if firstword == "how" and (words[1] in ["much", "many"] or words[1][-2:] == "ly"):
                return "how much"
            if firstword == "what":
                if "population" in words:
                    return "population"
                if len(set(words[1:4]).intersection(set(["is", "was", "s"]))) > 0:
                    return "is/was"
                if len(set(words[1:4]).intersection(set(["are", "were", "re"]))) > 0:
                    return "are/were"
                if len(set(words[1:4]).intersection(set(["do", "does", "did", "d"]))) > 0:
                    return "do/does/did"
            return firstword
        for i in range(0, len(words)-1):
            if words[i] == "how":
                if words[i+1] in ["much", "many"] or words[i+1][-2:] == "ly":
                    return "how much"
                return "how"
        if "what" in words:
            if words[-2] == "what":
                if len(set(words).intersection(set(["is", "was", "s"]))) > 0:
                    return "is/was"
                if len(set(words).intersection(set(["are", "were", "re"]))) > 0:
                    return "are/were"
            return "what"
        return "misc"

    def read_qfile(self, qfile):
        doc = open(qfile, 'r').read()
        m_num_qs = re.compile('(<num> Number: (\d*)|<desc> Description:\s*\n(.*))')
        num_qs = m_num_qs.findall(doc)
        questions = {}
        for tup in num_qs:
            if "<num>" in tup[0]:
                qnum = tup[1].strip()
            else:
                question = tup[2].strip()
                questions[qnum] = question
        return questions

    """
        Extracts question numbers and questions from qfile, and 
        categorizes each question into 6 different question types. 

        params
        ----
            qfile : question file in the format:
                 <num> Number: "qnum"
                 ...
                 <desc> Descriptions:
                 "question"
                 ...

       returns a dictionary of
           key: question number string
           value: (question string, question type string)
    """
    def get_qtypes(self, qfile):
        questions = self.read_qfile(qfile)
        for (qnum,q) in questions.items():
            qtype = self.categorize_q(q)
            questions[qnum] = (q, qtype)
        return questions

    """
        Analyzes the questions in the qfile and
        generates statistics as to how much percentage of the questions
        belongs to which question type.
    """
    def stats(self, qfile):
        questions = self.read_qfile(qfile)
        qstats = {}
        tot = 0.
        for (qnum,q) in questions.items():
            tot += 1.
            qtype = self.categorize_q(q)
            if qstats.has_key(qtype):
                qstats[qtype] += 1.
            else:
                qstats[qtype] = 1.

        qstat_str = ""
        for (qt,freq) in qstats.items():
            qstats[qt] = freq / tot
            qstat_str = qstat_str + qt + " " + str(qstats[qt]) + "%\n"

        print qstat_str

if __name__ == "__main__":
    qatree = CategorizeQs()
    qatree.stats("questions.txt")

        
