#!/usr/bin/python
import sys,os,re,optparse,tarfile,uuid,shutil

def main():

    try:
        returnValue = int(sys.argv[1])
        print "Return value from MrBayes is " + str(returnValue)
    except:
        print "Error: could not find return value from run_mrbayes"
        return 2

    try:
        basename = str(sys.argv[2])
    except:
        print "Error: could not find basename from run_mrbayes"
        return 3

    if returnValue == 1: 
        print "Not all taxa present for " + basename + " - file ignored."
        return 0

    if returnValue != 0: 
        print "Error: run_mrbayes returned " + str(returnValue) + "."
        return returnValue

    if os.path.isfile("run_mrbayes.tar"):
        if tarfile.is_tarfile("run_mrbayes.tar"):
            try:
                myTarfile = tarfile.open("run_mrbayes.tar", 'a:')
            except:
                return 4
        else:
            print "Error: file run_mrbayes.tar, not recognized as a tar file."
            return 5
    else:
        try:
            myTarfile = tarfile.open("run_mrbayes.tar", 'w:')
        except:
            print "Error: could not open new mrbayes.tar file."
            return 6
            
    filename = basename + ".t"
    if os.path.isfile(filename):
        try:
            myTarfile.add(filename)
        except:
            print "Error: could not add file to tar file"
            return 8

        try:
            os.unlink(filename)
        except:
            print "Error: could not delete mrbayes output file."
            return 9

    myTarfile.close()
    return 0
    
sys.exit(main())


