#fileNexus.py
#version 1.0.1
#
#  Adapted from fileReader_condor.py and fileWriter_condor.py originally written by John Malloy.

import re,string,os,sys

def remove_comment(line):
    '''
    Remove the comments from a line
    :Input: The line from a .nexus file
    '''
    comment_found = False
    begin = False
    end = False
    line_str = ""
        
    #account for white space
    if (line == None):
        return line
        
   #see if there is a comment (marked by '[]')
    elif (re.search('\[', line) and re.search('\]', line)):
        comment_found = True
        for word in line.split():
            #check to see where the comment begins and ends
            if (re.search('\[', word)):
                begin = True
                end = False
            if (re.search('\]', word)):
                word = ""
                end = True
                begin = False
            #if the comment has started, but the end hasn't happened yet, set the
            #word to nothing
            if (begin and not end):
                word = ""
            #add the uncommented word to a growing new line
            if (word != ""):
                line_str += word + " "
                    
        #return the new line if there were comments
        return line_str
    else:
        #if no comments, return the line as is
        return line

def find_taxa_set(translate_file):
    '''
    Find the taxa set in a translation file
    :Input: The *.txt file that begins with the word 'translate'
    :Return: A list of taxa
    '''
    taxa_list = {}
    translate_found = False
    translate_end = False
    lines = [line.rstrip() for line in open(translate_file,"r")]
    for line in lines:
        if (translate_found and re.search(';', line)):
            translate_end = True
            break
        if (translate_found and not translate_end):
            indiv_taxa = line.split()
            taxa_list[indiv_taxa[0]] = indiv_taxa[1]
        if (re.search('translate', line)):
            translate_found = True
    return taxa_list

def create_mb_block(mb_ngen, mb_nst, mb_rates, mb_aamodel, mb_burnin, mb_samplefreq):
    '''
    Create a mrbayes block for a NEXUS file
    :Input: five mrbayes parameters
    :Return: a string with the mrbayes block
    '''
    #calculate sample frequency/print freq based on the number of generations
    #have a max of 100000 trees stored
    MAX_SAMPLE = 100000
    if (mb_samplefreq <= MAX_SAMPLE and mb_samplefreq<= mb_ngen):
        samplefreq = mb_samplefreq
    elif (mb_ngen <= MAX_SAMPLE):
        samplefreq = mb_ngen
    else:
        samplefreq = mb_ngen/MAX_SAMPLE + 1

    mb_block = "begin mrbayes;\n"
    mb_block += "\tset autoclose=yes nowarn=yes;\n"
    mb_block += "\tlset nst=" + str(mb_nst) + " rates=" + str(mb_rates) + ";\n"
    if( mb_aamodel != None):
        mb_block += "\tprset aamodelpr=fixed("+mb_aamodel+");\n"
    mb_block += "\tmcmcp nruns=1 ngen=" + str(mb_ngen) + " relburnin=yes burninfrac=" + str(mb_burnin) + " printfreq=" + str(mb_ngen/2) + " samplefreq=" + str(samplefreq) + " nchains=1 savebrlens=yes;\n"
    mb_block += "\tmcmc file=out;\n\tsumt;\nend;"

    return mb_block



    
class fileReader:
    """
    Reads files (in .nexus format) for relevant information
    """
    
    def __init__(self):
        self.ntax_line = ""
        self.ntax = "0"
        self.nchar_line = ""
        self.nchar = ""
        self.mb_block_found = False
        self.mb_block = ""
        self.format_line = ""
        self.taxa = []
        self.ref_dict = {}
        #used in calculation of number of trees to store
        self.NGEN = 100000

    
    def read_file(self, filename):
        '''
        Reads the .nex file and stores all relevant information
        :Input: The file to be analyzed, as well as various information to build a mrBayes block - the number of states, the number
            of generations, the rates, and the burnin value
        '''
        ntax_found = False
        nchar_found = False
        matrix_found = False
        end_matrix = False
        found_mb = False
        found_end_of_mb = False
        self.mb_block = ""
        self.taxa = []

        file = open(filename, "r")
        for line in file:
            #remove the comments
            line = remove_comment(line)
            
            #find the number of taxa
            if (re.search('(?<=ntax=)', line.lower())):
                self.ntax_line = re.search('(?<=ntax=)', line.lower())
                words = self.ntax_line.string.split()
                for word in words:
                    if "ntax" in word.lower():
                        self.ntax = word.split("=")
                        self.ntax = self.ntax[1]
                        self.ntax = re.sub('[^0-9]','',self.ntax)
                        self.ntax =  int(self.ntax)
                        ntax_found = True
                        
            #find the number of characters
            if (re.search('(?<=nchar=)', line.lower())):
                self.nchar_line = re.search('(?<=nchar=)', line.lower())
                words = self.nchar_line.string.split()
                for word in words:
                    if "nchar" in word.lower():
                        self.nchar = word.split("=")
                        self.nchar = self.nchar[1]
                        self.nchar = re.sub('[^0-9]','',self.nchar)
                        self.nchar = int(self.nchar)
                        nchar_found = True
            
            #find the formatting description 
            if re.search('format', line.lower()):
                self.format_line = line

            #find the taxa
            #find beginning of the matrix
            if (re.search('matrix', line.lower())):
                matrix_found = True

            #find end of matrix
            elif (matrix_found and re.search(';', line)):
                end_matrix = True

            #find the taxa within the matrix
            elif matrix_found and not end_matrix:
                words = line.split()
                #store the first word (the taxa name) in the taxa list
                if (words != []):
                    self.taxa.append(words[0])
 
                
            #find the mb block
            if (re.search('begin mrbayes', line.lower())):
                found_mb = True
            if (found_mb and found_end_of_mb != True):
                self.mb_block += line + "\n"
            if (found_mb and re.search('end', line.lower())):
                found_end_of_mb = True

        self.mb_block_found = found_mb

        d = {}
        for i in range(len(self.taxa)):
            if self.taxa[i] not in d.values():
                d[len(d)] = self.taxa[i]
        return d

                
    def get_ntax(self):
        '''
        :Return: The number of taxa
        '''
        return self.ntax
    
    def get_nchar(self):
        '''
        :Return: The number of characters
        '''
        return self.nchar
    
    def get_format_line(self):
        '''
        :Return: The FORMAT line of the nexus file
        '''
        return self.format_line
    
    def get_mb_block(self):
        '''
        :Return: The mrBayes block of the file
        '''
        return self.mb_block

    def mb_block_found(self):
        '''
        :Return: True if mrBayes block found in file
        '''
        return self.mb_block_found

    
class fileWriter:
    '''
    Writes files needed for analyses
    '''
    def __init__(self, ntax, nchar, format_line, mb_block):
        if (ntax != None):
            self.ntax = ntax
        if (nchar != None):
            self.nchar = nchar
        if (format_line != None):
            self.format_line = format_line
        if (mb_block != None):
            self.mb_block = mb_block

        #file header
        self.header = ""
        self.data = []
        self.tax_list = []

    def init_header(self):
        '''
        Builds the header of a .nex file
        '''
        self.header = ""
        self.header += "#NEXUS\n\nBEGIN DATA;\n\tDIMENSIONS NTAX=" + str(len(self.tax_list))
        self.header += " NCHAR=" + str(self.nchar) + ";\n" + self.format_line
        self.header += "\tMATRIX\n"
        
    def init_taxa(self, filename, includeTaxa, zip_file=0):
        '''
        Finds genetic data associated with each taxon, and build a string containing both the taxa and its associated data
        :Input: The file path to an individual .nexus file
        :Return: True if all taxa were found in the file, False otherwise
        '''
        #boolean to make sure the matrix header has been seen
        matrix_found = False
        
        self.tax_list = []      #initialize the genetic data to be written to the data
        self.data = []          #the sequences
        taxa_line_count = []    #the number of lines (>1 for interleaved) of data per taxon
        taxa_counter = 0

        if includeTaxa is not None:                                          #added 25 Sep 2016 by SJH
            taxaIndices = sorted([int(x) for x in includeTaxa.keys()])
            for num in range(len(taxaIndices)):
                self.tax_list.append(includeTaxa[str(taxaIndices[num])])
                self.data.append("")
                taxa_line_count.append(0)

        #find the genetic data associated with each taxon
        orig_file = open(filename, 'r')
        for line in orig_file:
            line = remove_comment(line.rstrip())                                 #added 24 Aug 2016 by SJH.  Added rstrip 4 Nov 2016 by SJH
            #find the matrix header
            if (re.search('matrix', line.lower())):
                matrix_found = True
            
            elif matrix_found and line[:1] == ";":                                  #added 25 sep 2016
                matrix_found = False

            elif matrix_found:                                                  #switched from if to elif 25 Sep 2016 by SJH
		#propTaxaName = re.match("^\s*([^\s-]*)\s",line)		#added 24 Aug 2016 by SJH
		propTaxaName = re.match("^\s*([^\s]*)\s",line)			#added 24 Aug 2016 by SJH - removed dash 4 Nov 2016 SJH
                if propTaxaName:					       	#added 24 Aug 2016 by SJH
			propTaxaName = propTaxaName.group(1)			#added 24 Aug 2016 by SJH
		else:								#added 24 Aug 2016 by SJH
			propTaxaName = line					#added 24 Aug 2016 by SJH
                taxa_found = False
                if self.tax_list:                                               #added 25 Sep 2016 by SJH
                    for i in range(len(self.tax_list)):
                        if propTaxaName == self.tax_list[i] :			#changed 24 Aug 2016 by SJH
                            taxa_found = True
                            if taxa_line_count[i] == 0 :
                                self.data[i] += line.rstrip()
                                taxa_counter += 1
                            else:
                                sequence_data = re.search(r"(?<=\s)[A-Za-z-?]+$", line)    #changed " " to \s   24 Aug 2016 SJH
                                                                                           #added "?" to matchable sequence characters - 25 Sep  2016 SJH
                                self.data[i] += sequence_data.group(0)
                            taxa_line_count[i] += 1
                if includeTaxa is None and taxa_found is False and len(propTaxaName) > 0:                        #this section added 25 Sep 2016 by SJH
                    #print("adding: ",propTaxaName)
                    self.tax_list.append(propTaxaName)
                    self.data.append(line.rstrip())
                    taxa_line_count.append(1)
                    taxa_counter += 1
        orig_file.close()

        #if all taxa not found, return false
        if (includeTaxa is not None and taxa_counter != len(taxaIndices)):
            return False
        else:
            return True

    def set_mb_block(self, mb_block):
        self.mb_block = mb_block

 
    def write_File(self, filename, includeTaxa, mb_block):
        '''
        Writes the n-taxon file to a file, called "<filename>.nex", which will be analyzed with mrBayes
        :Input: The original filename of the .nexus files, the taxa to include and the mrbayes block to include
        :Return: True if all taxon had data and were written to the *.nex file, False otherwise
        '''
        try:
            taxa_found = self.init_taxa(filename, includeTaxa)
        except:
            print "fileWriter_condor: Could not initialize"
            return 1

        #if all taxa have been found, build the quartet file. Don't build it otherwise.
        if (taxa_found):
            name = "input.nex"

            try:
                new_file = open(name, 'w')
            except:
                return findErrorCode("fileWriter_condor: Could not open new nexus file")

            try:
                self.init_header()
                new_file.write(self.header)
            except:
                return findErrorCode("fileWriter_condor: Could not create or write header")

            try:
                for i in range(len(self.tax_list)):
                    new_file.write(self.data[i] + "\n")
            except:
                return findErrorCode("fileWriter_condor: Could not write data")

            try:
                new_file.write(";\n\nEND;")
            except:
                return findErrorCode("fileWriter_condor: Could not write END to data block")

            #include a mrBayes block
            try:
                new_file.write("\n\n" + self.mb_block + "\n")
            except:
                return findErrorCode("fileWriter_condor: Could not write MrBayes Block")

            try:
                new_file.close()
            except:
                return findErrorCode("fileWriter_condor: Could not close new nexus file")

            return 0
        else:
            return findErrorCode("fileWriter_condor: not all taxa found")
            
    def add_to_output_file(self, cf_dict, ciLow_dict, ciHigh_dict, which_taxa):
        '''
        Adds a line of data to the output.csv file
        :Input: The concordance_factor dictionary containing the concordance factors associated with specific splits,
            and the numbers of the individual taxa in the quartet
        '''
        line = ""
        #go through the random taxa list and add those taxon numbers, along with split-associated CFs, to the line
        for num in which_taxa:
            line += str(num) + ","
        line += str(cf_dict["{1,2|3,4}"]) + ","
        line += str(cf_dict["{1,3|2,4}"]) + ","
        line += str(cf_dict["{1,4|2,3}"]) + ","
        line += str(ciLow_dict["{1,2|3,4}"]) + ","
        line += str(ciHigh_dict["{1,2|3,4}"]) + ","
        line += str(ciLow_dict["{1,3|2,4}"]) + ","
        line += str(ciHigh_dict["{1,3|2,4}"]) + ","
        line += str(ciLow_dict["{1,4|2,3}"]) + ","
        line += str(ciHigh_dict["{1,4|2,3}"]) + "\n"
        output_file = open("QuartetAnalysis.csv", 'a')
        output_file.write(line)
        output_file.close()

    def add_to_supple_file(self, genestring, quartet_taxa):
        '''
        Adds a line of data to the QuartetAnalysis.supple file
        :Input: the quartet taxa and the gene data previously written (gene #, prob (1,2), prob (1,3), prob (1,4)
        '''
        line = ""
        #go through the random taxa list and add those taxon numbers, along with split-associated CFs, to the line
        for num in quartet_taxa:
            line += str(num) + ","
        line += genestring
        output_file = open("QuartetAnalysis.supple", 'a')
        output_file.write(line)
        output_file.close()
