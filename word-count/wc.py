#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This is words counter
"""
import sys, getopt, re, operator
import reader
from reader import Spider, WordStats

def main(argv):
    """This is main function """
    input_file = ""
    output_file = ""

    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["ifile=","ofile="])
    except getopt.GetoptError:
        print "test.py -i <inputfile> -o <outputfile>"
        print argv
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            print "wc.py -i <inputfile> -o <outputfile>"
        elif opt in ("-i", "--ifile"):
            input_file = arg
        elif opt in ("-o", "--ofile"):
            output_file = arg
    print 'Input file is "', input_file
    print 'Output file is "', output_file

    raw_txt = reader.readFromFile(input_file)
    words = reader.extractWords(raw_txt)
    keywords = reader.meter(words)
    reader.writeToFile(output_file, keywords)


if __name__ == '__main__':
    #main(sys.argv[1:])
    #files = reader.batchRead()
    #print len(files)
    #print files[:10] 

    spider = Spider()
    print spider.getCatLen()
    spider.computeStats(['crude', 'livestock', 'earn', 'jobs' ])
    spider.getCategoryTop('crude')
    spider.getCategoryTop('earn')
    spider.getCategoryTop('livestock')
    spider.getCategoryTop('jobs')
    
    print spider.train()
