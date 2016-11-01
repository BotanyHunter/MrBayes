#!/usr/bin/python
import sys,os,re,optparse,tarfile,uuid,math,glob
from arguments import *

def TF(inputTF):
    if( inputTF != None and inputTF!=False ): return "True"
    return "False"


'''
Builds the submit file for MrBayes runs
'''

def main():

    current_version = "#version 1.0.2"
    current_mrbayes_version = "3.2.4"

    #versions 1.0.1 - includes ability to pass an "taxa to include" file using (-i)
    #               - includes ability to pass flag only to include genes on all taxa (-C)
    #versions 1.0.2 - includes ability to pass an "samplefreq" parameter to mrBayes using (-f)
    
    instanceID = uuid.uuid4()
    
    parser = getParser()
    options, remainder = parser.parse_args()

    noErrors = 1
    print("\n")
    #__________________________
    #fetch the working directory    
    #__________________________
    try:
        working_dir = os.path.dirname(os.path.realpath(__file__))
    except:
        print("ERROR: problem determining working directory")
        noErrors = 0

    #__________________________
    #  Work on data directory
    #__________________________
    if len(remainder) == 0:
        print("ERROR:   Must provide data directory as first argument after setup_mrbayes.")
        noErrors = 0
    else:
        data_dir = remainder[0]
        if( data_dir == None ):
            print("ERROR:   no data directory provided.  First argument after set_up_mrbayes should be data directory")
            noErrors = 0
        else:
            if os.path.isdir(data_dir) != True :
                print("ERROR:   data directory (" + data_dir + ") does not exist.")
                noErrors = 0

    #____________________
    #  If includeFiles to be used, ensure file exists.
    #____________________
    if options.includeFiles is not None:
       if not os.path.isfile(options.includeFiles):
          print("ERROR: taxa to include file (" + options.includeFiles + ") not found.\n")
          noErrors = 0

    if noErrors == 1:
        myGenes = []
        myFiletypes = []
        filetype = '*.nex'
        count = 0
        for file in glob.glob(data_dir + "/" + filetype):
            myGenes.append(os.path.basename(file))
            myFiletypes.append(filetype)
            count += 1
        print "file count: " + str(count)
        if len(myGenes) == 0 :
            print "ERROR:   no nexus (*.nex) files found in data directory."
            noErrors = 0
        else:
            print "CHECKED: Found ", len(myGenes), "nexus files in directory:", working_dir+"/" + data_dir+"/."

    #__________________________
    #  Work on LOG/ERR/OUT directories
    #__________________________
    if( os.path.isdir("log") ):
        print "CHECKED: - log/ directory exists."
    else:
        os.makedirs("log")
        print "ACTION:   - log/ directory created."

    if( os.path.isdir("err") ):
        print "CHECKED: - err/ directory exists."
    else:
        os.makedirs("err")
        print "ACTION:   - err/ directory created."

    if( os.path.isdir("out") ):
        print "CHECKED: - out/ directory exists."
    else:
        os.makedirs("out")
        print "ACTION:   - out/ directory created."


    #If any errors prior to this point, stop
    if noErrors == 0 : sys.exit()

    #Build run_mrbayes.dag which lists the individual genes to run
    st  = "#instanceID="+str(instanceID)+"\n"
    st += "#This dag runs the individual genes through mrbayes\n\n"
    whichGene = 0
    for file in myGenes:
        whichGene += 1
        basename = os.path.splitext(file)[0]

        #special coding for calochortus to cut off "_adj.phylip" from base name
        #basename = basename[0:-11]
        st += 'JOB         run_mrbayes_' + str(whichGene) + ' run_mrbayes.submit\n'
        st += 'VARS        run_mrbayes_' + str(whichGene) + ' filename="' + file + '" basename="' + basename + '"\n'
        st += 'SCRIPT POST run_mrbayes_' + str(whichGene) + ' pos_mrbayes.py $RETURN ' + basename+ '\n\n'

    submit_file = open('run_mrbayes.dag', 'w')
    submit_file.write(st)
    submit_file.close()

    #_________________________
    #Build run_mrbayes.submit
    #- This job file submits each individual gene
    #_________________________
    st  = "#instanceID="+str(instanceID)+"\n"
    st += "#Submit file for mrbayes.\n\n"

    st += "universe = Vanilla\n\n"
    st += "executable = run_mrbayes.py\n\n"
    st += "DDIR  = " + working_dir + "/" + data_dir + "\n"
    st += "should_transfer_files   = YES\n"
    st += "when_to_transfer_output = ON_EXIT\n\n"
    st += "transfer_input_files = run_mrbayes.py, fileNexus.py, arguments.py, mb, $(DDIR)/$(filename)"
    if options.includeFiles is not None: st += ", " + options.includeFiles
    st += "\n\n"
    st += "log    = log/mb.$(basename).log\n"
    st += "error  = err/mb.$(basename).err\n"
    st += "output = out/mb.$(basename).out\n\n"
    st += "request_cpus   = 1\n"
    st += "request_disk   = 20 MB\n"
    st += "request_memory = 20 MB\n\n"
    #st += "+wantFlocking = true\n"
    #st += "+wantGlidein = true\n\n"

    st += 'arguments = '
    st += '$(filename) $(basename)' + buildArgList("iCgnrsuf", options) + '\n'
    st += "queue \n\n"

    submit_file = open('run_mrbayes.submit', 'w')
    submit_file.write(st)
    submit_file.close()

    print "\n\nProgram set_up finished successfully."
    print "run_mrbayes.dag has been created.\n\n"
    


main()



