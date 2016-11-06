#!/usr/bin/python
import sys,os,re,optparse,subprocess
from arguments import *
from fileNexus import *
'''
Runs a series of mrbayes calculations
'''

def main():

    current_version        = "#version 1.0.1"
    #                        version 1.0.1 includes the ability to only include certain taxa (-i filename)
    #                        and to only include genes that were found for all taxa (-C 1)
    mrbayes_executable     = "mb"
    errorAtStep            = None

    parser = getParser()
    options, remainder = parser.parse_args()
    fr = fileReader()


    #__________________________
    #fetch the working directory    
    #__________________________
    try:
        working_dir = os.path.dirname(os.path.realpath(__file__))
    except:
        print "ERROR: problem determining working directory"
        return 2

    #  We need to accomplish the following steps
    #  1)  data work
    #      1a - remove taxa not on "includedTaxa" file
    #         - if -C == 1 and not all desired taxa included, return fail notice
    #         - change name of input file to "input.nex"
    #  2)  launch mb
    #  3)  change name of output file and clean up.

    #step 1: The first argument is the data file name.
    #        change it to input.nex - this is what mbCommand.nex uses.
    try:
        datafile = remainder[0]
        working_dir = os.path.dirname(os.path.realpath(__file__))
    except:
        print "ERROR: problem determining data file"
        return 3

    if not os.path.isfile(datafile):
        print "ERROR: data file " + datafile + " does not exist"
        return 4

    #If user supplies list of taxa, then carve these out of the input nexus files.
    if options.includeFiles is not None:
      try:
         includeTaxa = find_taxa_set(options.includeFiles)
      except:
         print "ERROR: problem reading includeFiles: " + options.includeFiles
         return 5
    else:
         includeTaxa = None

    #Read input nexus files for taxa and mb_block
    try:
        d = fr.read_file(datafile)
    except:
        print "ERROR: problem reading input nexus file."
        return 6

    #Check that all taxa are present
    try:
        allFound = True
        if options.includeFiles is not None:
            for taxa in includeTaxa.values():
                if taxa not in d.values():
                   print "missing taxon " + taxa
                   allFound = False
    except:
        print "ERROR: problem checking if all taxa present"
        return 7


    #Now the steps to write out the new file (if all taxa present)
    if not allFound:
        print "Not all taxa present.  Processing stopped for " + datafile
        return 1

    else:

    	#Create mb block to attach to end of new nexus file
    	try:
            if fr.mb_block_found:
       	        mb_block = fr.get_mb_block()
            else:
                mb_block = create_mb_block(options.mb_ngen, options.nst, options.rates, options.aamodel, options.burnin, options.samplefreq)
    	except:
            print "ERROR: problem reading input nexus file."
            return 8

    	#Write out new nexus file.
    	try:
    	    wf = fileWriter(fr.get_ntax(), fr.get_nchar(), fr.get_format_line(), mb_block)
            wf.write_File(datafile, includeTaxa, mb_block)
        except:
            print "ERROR: problem writing output nexus file"
            return 9

    #Otherwise, simply return without running through mrbayes
    #step 2: launch mb
    mb_command = "./" + mrbayes_executable + " input.nex"
    try:
        with open("input.nex") as f:
		content = f.readlines()
        retValue = subprocess.call(mb_command, shell=True)
    except OSError as e:
        print "Error executing MrBayes"
        print "Execution failed:", e
        return 4
    except:
        print "Unknown MrBayes execution error: command = " + mb_command
        return 5

    #get outputfile names
    try:
        outputFilename = remainder[1]
    except:
        print "ERROR: problem finding output name."
        return 6

    # Step 3: rename output file
    try:
        os.rename("out.t", outputFilename + ".t")
    except:
        print "ERROR: problem renaming output file (out.t) to " + outputFilename + ".t"
        return 7

    
    # Step 4: remove unwanted output
    if retValue == 0:
        try:
           if os.path.exists("input.nex"):
               os.remove("input.nex")
        except:
           print "ERROR: problem deleting input file (input.nex)."
           return 8

        try:
           files = os.listdir("./")
           for file in files:
               if file.startswith("out."):
                   os.remove(file)
        except:
           print "ERROR: problem deleting mrbayes output files."
           return 9
    

    return 0
    
sys.exit(main())


