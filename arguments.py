#arguments.py
#version 1.0.0

import os, optparse

def buildArgList(whichArgs, options):
    #build arguments for later submit files
    args = ""
    if( "i" in whichArgs ): 
      if options.includeFiles is not None: args += " -i " + str(options.includeFiles)
    if( "C" in whichArgs ): 
      if options.onlyCompleteGenes != 0: args += " -C 1"

    if ("g" in whichArgs and options.aamodel != None): args += " -g " + options.aamodel
    if( "n" in whichArgs ): args += " -n " + str(options.mb_ngen)
    if( "r" in whichArgs ): args += " -r " + options.rates
    if( "s" in whichArgs ): args += " -s " + str(options.nst)
    if( "u" in whichArgs ): args += " -u " + str(options.burnin)
    if( "f" in whichArgs ): args += " -f " + str(options.samplefreq)



    return args
    


def getParser():
    parser = optparse.OptionParser()
    #general options
    parser.add_option('-i', '--includeFiles', dest = 'includeFiles', default = None, help = 'Text file containing user-specified nexus-formatted files (one per line) to analyze')
    parser.add_option('-C', '--onlyCompleteGenes', dest = 'onlyCompleteGenes', type = 'int', default = '0', help = 'Set to 1 if only genes found on all taxa to be included.')

    mb_group = optparse.OptionGroup(parser, "mrBayes options", "Optional arguments for mrBayes analyses")
    mb_group.add_option('-s', '--nst', dest = 'nst', type = 'int', default = 2, help = 'Determines the nst parameter of mrBayes')
    mb_group.add_option('-n', '--mb_ngen', dest = 'mb_ngen', type = 'int', default = 1000000, help = 'The number of generations of mrBayes')
    mb_group.add_option('-r', '--rates', dest = 'rates', default = 'gamma', help = 'Determines the rate parameter of mrBayes')
    mb_group.add_option('-g', '--aamodel', dest = 'aamodel', default=None, help='amino acid model, such as Poisson, Jones')
    mb_group.add_option('-u', '--burnin', dest = 'burnin', type = 'float', default = '0.25', help = 'Burnin frequency for mrBayes')
    mb_group.add_option('-f', '--samplefreq', dest = 'samplefreq', type = 'int', default = '1000', help = 'sample frequency for mrBayes')


    parser.add_option_group(mb_group)
    
    
    return parser

