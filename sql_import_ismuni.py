from sql_import import *
import xmltodict

# This class will parse IS MUNI odpovednik format *.qdefx
# and create SQL query to IMPORT data into Table
class sql_import_ismuni(sql_import):

    delimiters = [',', ';']

    def __init__(self, table, fileIn, fileOut):
        self.content = None
        self.questions_list = []

        self.table = table
        self.fileIn = fileIn

        if self.loadFile(fileIn) is not False:
            if self.parseContent():
                self.saveSql(table, fileOut)
            else:
                print("Can't parse \"{0}\". Structure might be wrong".format(fileIn))
        else:
            print("Can't open \"{0}\" file.".format(fileIn))

    def loadFile(self, filename):
        self.questions_list.clear()
        try:
            fd = open(filename, encoding='utf8')
            self.content = fd.read()
        finally:
            fd.close()

        if self.content is None:
            print('no content available!')
            return False
        return True

    def saveFile(self, filename, content, ext):
        try:
            fo = "{0}.{1}".format(filename, ext)
            with open(fo, 'w+', encoding='utf-8') as fd:
                fd.write(content)
            print("From: {0} -> {1} query file saved \'{2}\'".format(self.fileIn, ext, fo))
        except:
            print("Can't save '{0}' file \'{1}\'".format(ext,fo))

    
    #-----------------------------------------------------------
    # Method parses content of the *.qdefx xml file and splits 
    # structure into following dictionary:
    #
    #     dict = {
    #         'key_content' : value
    #         'answers' : [
    #             'r1' : value,
    #             'r(x)' : value,
    #         ]
    #         'right_answer' : value
    #     }
    #-----------------------------------------------------------
    def parseContent(self):
        delimiters = [':', ' ', 'ok']

        doc = xmltodict.parse(self.content)
        qdefx_root = doc['qdefx']
        qdefx_questions = doc['qdefx']['set']['questions']

        # parse sets
        content_list = []
        for question in qdefx_questions['question']:
            if question is not None:
                settings = question['settings']
                if settings is not None:
                    setting = settings['setting']
                    if setting is not None:
                        content = setting['content']
                        if content is not None:
                            content_list.append(content)

        
        if content_list is not None:
            # parseout html cdata format
            for cdata in content_list:
                question = {
                    'key_content' : None,
                    'answers' : [],
                    'right_answer' : None
                }

                data = cdata.split("\n")
                question['key_content'] = data[0] # store question

                # store answers only
                # remap format from ':r(x)' value -> key[r(x)]:'value' dictionary
                answers = { }
                for x in range(1, len(data) - 1):
                    d = " :r{0} ".format(int(x))
                    s = data[x].replace(d, '')
                    answers['r{0}'.format(int(x))] = s
                question['answers'] = answers # append answers to question list

                # remove ':', ' ' and 'ok' form right answer format like ':r5 ok' -> 'r5'
                # ugly but it works :D
                for d in delimiters:
                    data[-1] = data[-1].replace(d, '')
                question['right_answer'] = data[-1] # store right question

                self.questions_list.append(question) # append complete question to question list
            return True

        return False

    def printout(self):
        data = self.questions_list
        for row in data:
            print (row)
            
    def saveSql(self, table, filename):

        table = None # unused
        
        questions, answers, corrects = self.saveSplitTableSql(filename)

        self.saveSplitTableRelationSql(questions, answers, corrects, 0, 0)

        pass

    #-----------------------------------------------------------
    # Method will split dictionary data into three lists [questions, answers, right_answers]
    # and create *.sql query files as dataset ready for SQL 'INSERT INTO'
    #-----------------------------------------------------------
    def saveSplitTableSql(self, filename):
        delimiter = [',', ';']

        table = None
        questions = []
        answers = []
        right_answer = []

        # split data to corresponding lists
        for row in self.questions_list:
            data = []
            for item in row.values():
                data.append(item)

            questions.append(data[0])
            answers.append(data[1])
            right_answer.append(data[2])

        # obtain right answer indexes from non-duplicit arrays
        #------------------------------------------------------
        # The problem - we need to back convert 'r(x)' to index 
        # to obtain string of correct answer for eg. 'r1: ok' => '1970'
        # we should get same number of questions againts 'right_answer' dictionary.
        # This array will be used to match indexes in 'clean answers dictionary' 
        # (without any duplicities) for relation model between Questions and Answers
        right_answer_idx = []
        for right in right_answer:
            idx = int(right.replace('r','')) # remove 'r' from str 'r1' and extract number
            right_answer_idx.append(idx)
        
        #print ("{0} {1}".format(len(right_answer_idx), len(answers)))
        
        it = 0
        _right_answer = []
        for answer in answers:
            val_idx = int(right_answer_idx[it] - 1) #because array index starts from 0
            a = list(answer.values())
            #print ("val_idx: {0}  a: {1}".format(val_idx, a[val_idx]))
            _right_answer.append(a[val_idx])    # append correct item value from dictionary to right_answer list
            it+=1
        right_answer.clear()
        right_answer = _right_answer

        # continue with proper SQL QUERY creation:
        #------------------------------------------------------
        # remove duplicites from answers
        _answers = []
        for answer in answers:
            for item in answer.values():
                _answers.append(item)
        answers.clear()
        answers = list(set(_answers))

        # construct test question list
        query = None
        table = 'cms.testquestions'
        query = 'INSERT INTO {0} (id_question, text_question) \n VALUES '.format(table)
        id = 1
        for question in questions:
            d = 0
            if question is next(reversed(questions)): 
                d = 1
            query += "({0},'{1}'){2}\n".format(id, question, delimiter[d])
            id += 1
        self.saveFile("{0}_{1}".format(table, self.fileIn), query ,'sql')

        # construct test answer list
        query = None
        table = 'cms.testanswers'
        query = 'INSERT INTO {0} (id_answer, text_answer) \n VALUES '.format(table)
        id = 1
        for answer in answers:
            d = 0
            if answer is next(reversed(answers)): 
                d = 1
            query += "({0}, '{1}'){2}\n".format(id, answer, delimiter[d])
            id += 1
        self.saveFile("{0}_{1}".format(table, self.fileIn), query ,'sql')

        # return dictionaries for relation purpouse
        return questions, answers, right_answer

    #-----------------------------------------------------------
    # Method construct correct answer relation between question 
    # and answer lists
    #   param 'offset_qa' : last idx of the 'testquestion' table
    #   param 'offset_an' : last id of the 'testanswers' table
    #-----------------------------------------------------------
    def saveSplitTableRelationSql(self, questions, answers, corrects, offset_qa, offset_an):
        
        # Set right offset
        # +1 is ID record offset because records starts from 1 and not 0
        offset_qa += 1
        offset_an += 1

        delimiters = [',', ';']

        table = None
        query = None

        table = "cms.testquestionanswer_relation"
        query = 'INSERT INTO {0} (id_question, id_answers, correctnes) \n VALUES '.format(table)

        # Problem - we have to found correct answer in the question
        # and associate ID number with answers list
        if (len(questions) == len(corrects)) and (len(questions) == len(self.questions_list)) :
            for row in self.questions_list:
                data = []

                # split data origina to corresponding lists 
                #   [0] - question, 
                #   [1] - answers dictionary
                #   [2] - right answer
                for item in row.values():
                    data.append(item)

                # find question id
                qId = 0
                for q in range(len(questions)):
                    if questions[q] == data[0]:
                        qId = q

                # convert answers dictionary list to list
                _answers = []
                for answer in data[1].values():
                    _answers.append(answer)

                # find corresponding answers id to question answer
                # and determinate correctnes
                for answer in _answers:
                    aId = 0
                    for a in range(len(answers)):
                        # we found answer in our answer list
                        if answers[a] == answer:
                            aId = a
                            correct = 0
                            # there is correct answer for question id
                            if corrects[qId] == answer:
                                correct = 1
                            query += "({0}, {1}, {2}),\n".format(qId+offset_qa, aId+offset_an, correct)

            self.saveFile("{0}_{1}".format(table, self.fileIn), query ,'sql')

        else:
            print("Data corrupted: Number of items in dictionaries differs! {0} != {1}". format(len(questions), len(corrects)))
            pass

    #-----------------------------------------------------------
    #
    # Method will join 'question_list' dictionary into one query table
    # (key_content)         (answers {})      (right_answer)
    # +-------------+----+----+----+----+----+--------------+
    # | key_content | r1 | r2 | r3 | r4 | r5 | right_answer |
    # +-------------+----+----+----+----+----+--------------+ 
    #
    #-----------------------------------------------------------
    def saveSingleTableSql(self, table, filename):

        delimiters = [',', ';']

        idx = 0
        exclude = []
        query = None
        query = 'INSERT INTO {0} ('.format(table)

        # extract dictionary keys even from nested dictionaries
        # eg {'answers', {'r1', 'r2', 'r3'}, 'goals'} -> 'answers', 'r1', 'r2', 'r3', 'goals'
        header = [*self.questions_list[idx]]
        for row in header:
            nested = self.questions_list[idx]['{0}'.format(row)]
            for key in nested:
                if len(key) > 1:
                    exclude.append('{0}'.format(row))
                    if key is not next(reversed(nested)):
                        query += "{0}{1} ".format(key,self.delimiters[0])
                    else:
                        query += key
            if row is not next(reversed(header)):    
                query += "{0}{1} ".format(row,self.delimiters[0])
            else:
                query += row

        # exclude extracted keys from nested dictionaries
        for e in exclude:
            query = query.replace(e,'')

        # build VALUES
        query += ') \n VALUES '
        for row in self.questions_list:
            query += '('
            for item in row.values():
                value = None
                # extract values from nested dictionaries!
                if isinstance(item, dict) is True:
                    for i in item.values():
                        query += "'{0}'{1} ".format(i,self.delimiters[0])
                    continue
                if item is not next(reversed(row.values())):
                    query += "'{0}'{1} ".format(item,self.delimiters[0])
                else:
                    query += item
            if row is not next(reversed(self.questions_list)):
                query += '){0}'.format(delimiters[0])
            else:
                query += '){0}'.format(delimiters[1])
        return self.saveFile("{0}_{1}".format(table, self.fileIn), query ,'sql')
