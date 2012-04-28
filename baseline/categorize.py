import re
"""
  Categorize Questions into 6 different question types:
      what, who, where, when, how, misc(miscellaneous)
"""
class CategorizeQs:

    def __init__(self):
        self.categories = {"what":1, "who":2, "where":3, "when":4, "how":5, "misc":6}

    def categorize_q(self, question):
        words = re.compile("\W").split(question.lower())
        firstword = words[0]
        if self.categories.has_key(firstword):
            return firstword
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
    qatree.stats("/Users/jollifun/Downloads/train/questions.txt")

        
