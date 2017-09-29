# coding:utf-8
import Paper
import csv
import ILearner
from sklearn.model_selection import train_test_split
import datetime
import pickle
import codecs
import re

# 文件路径
paperPath = "F:\\ACAData\\task3\\papers.txt"
trainPath = "F:\\ACAData\\task3\\train.csv"
validationPath = "F:\\ACAData\\task3\\validation.csv"
output3Path = "F:\\ACAData\\task3\\output3.txt"

trainX = []
trainY = []
testX = []
ordinals = ['first',
 'second',
 'third',
 'fourth',
 'fifth',
 'sixth',
 'seventh',
 'eighth',
 'ninth',
 'tenth',
 'eleventh',
 'twelfth',
 'thirteenth',
 'fourteenth',
 'fifteenth',
 'sixteenth',
 'seventeenth',
 'eighteenth',
 'nineteenth',
 'twentieth',
 'thirtieth',
 'fortieth',
 'fiftieth',
 'sixtieth',
 'seventieth',
 'eightieth',
 'ninetieth',
 'hundredth',
 'thousandth']


def getVenue(venue, d=dict()):
    tmp = d.get(venue)
    if tmp:
        return tmp
    tmp = venue
    venue = venue.lower()
    #Remove Roman numerals, and artifacts like '12.'
    venue = re.sub(r'M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})', '', venue)
    venue = re.sub(r'\d+\.', '', venue)
    #Remove numbers
    venue = re.sub(r' \d+ ', '', venue)
    #Remove years
    venue = re.sub(r'\'\d{2}', '', venue)
    venue = re.sub(r'\d{4}', '', venue)
    #Remove ordinals
    venue = re.sub(r'\d+(st|nd|rd|th)', '', venue)
    venue = venue.split()
    venue = [x for x in venue if not any([o in x for o in ordinals])]
    venue = ' '.join(venue)
    #Remove stuff in brackets, and other boilerplate details
    f = venue.find('(')
    if f > 0:
        venue = venue[:f]
    f = venue.find(':')
    if f > 0:
        venue = venue[:f]
    f = venue.find(';')
    if f > 0:
        venue = venue[:f]
    f = venue.find('vol.')
    if f > 0:
        venue = venue[:f]
    f = venue.find('volume')
    if f > 0:
        venue = venue[:f]
    f = venue.find('part')
    if f > 0:
        venue = venue[:f]
    d[tmp] = venue
    return venue


def ParsePaperTxt():
    print("%s parse paper"%datetime.datetime.now())
    with codecs.open(paperPath, "r",encoding='utf-8') as f:
        for eachLine in f:
            if eachLine.startswith('#index'):
                i = int(eachLine[6:])
                p = Paper.Paper.getPaperById(i)
            elif eachLine.startswith("#@"):
                p.Author = eachLine[2:-1].split(',')
                for aut in p.Author:
                    Paper.Paper.addAutPaper(aut, p)
            elif eachLine.startswith("#*"):
                p.Title = eachLine[2:-1]
            elif eachLine.startswith("#t"):
                p.Time = int(eachLine[2:-1])
            elif eachLine.startswith("#c"):
                p.Journal = getVenue(eachLine[2:-1])
            elif eachLine.startswith("#%"):
                t = Paper.Paper.getPaperById(int(eachLine[2:-1]))
                p.References.append(t)
                t.Referenced.append(p)
            else:
                pass


def ReadTrain():
    print("%s read training set"%datetime.datetime.now())
    with codecs.open(trainPath, "r",encoding='utf-8') as csvf:
        reader = csv.reader(csvf)
        firstRow = True
        for row in reader:
            if firstRow:
                firstRow = False
                continue
            trainX.append(row[0])
            trainY.append(int(row[1]))


def ReadValidation():
    print("%s read validation set"%datetime.datetime.now())
    with codecs.open(validationPath, "r",encoding='utf-8') as csvf:
        reader = csv.reader(csvf)
        firstRow = True
        for row in reader:
            if firstRow:
                firstRow = False
                continue
            testX.append(row[0])


def SelectModel():
    print("%s select model"%datetime.datetime.now())
    X_train, X_test, y_train, y_test = train_test_split(
        trainX, trainY, test_size=0.3, random_state=0)
    c=0
    opt=0

    m = ILearner.SparsePA(0,26)
    m.train(X_train, y_train)
    mape = m.score(X_test, y_test)
    print("C: %r,  MAPE: %r, train: %r, test: %r\n" %
          (c, mape, len(X_train), len(y_test)))

    if mape > opt:
        opt = mape
        model = m
    return model


def GenResult(model):
    print("%s save model"%datetime.datetime.now())
    with codecs.open(output3Path, "w",encoding='utf-8') as out:
        out.write("<task3>\nauthorname\tcitation\n")
        Yp = model.predict(testX)
        for i in range(len(Yp)):
            out.write("%s\t%d\n" % (testX[i], Yp[i]))
        out.write("</task3>\n")


def analisis():
    tempPath = "F:\\ACAData\\task3\\"
    with codecs.open(tempPath+"temp.txt",'w',encoding='utf-8') as fout:
        fout.write("%r\n"%len(trainX))
        for i in range(len(trainX)):
            papers = Paper.Paper.getPaperByAut(trainX[i])
            A = [(papers[j].Index, len(papers[j].Referenced)) for j in range(len(papers))]
            for j in range(len(A)):
                fout.write("%d:%d;"%(A[j][0],A[j][1]))
            fout.write("%d\n"%trainY[i])


def main():
    ParsePaperTxt()
    Paper.Paper.MergePaper()
    ReadTrain()
    #analisis()
    ReadValidation()
    model = SelectModel()
    model.save('optModel.txt')
    GenResult(model)




if __name__ == "__main__":
    main()

