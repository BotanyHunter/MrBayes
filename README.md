# MrBayes
HTCondor files to run MrBayes on all files in a directory

# Getting Starting
Navigate to your working directory on the HTCondor submit node
and type the following command:

    git clone https://github.com/BotanyHunter/MrBayes.git

which will create a new directory called <b>MrBayes</b> and download:
<ol>
  <li>five python scripts</li>
  <li>this README file</li>
  <li>the MrBayes executable, mb, version 3.2.4 (1.815.501 bytes)</li>
</ol>

# Your molecular data

Create a new directory inside MrBayes and give it a name such as <b>data</b>.</br></br>
Place all files on which you would like to run MrBayes (in nexus format) into the directory.
The file extensions must be ".nex".  If necessary, see repository PhylogeneticFileConversions to batch convert
files from phylip format to nexus.

To only run MrBayes on a particular subset of taxa, create a file in the MrBayes directory with the format
shown below. Of course, the names being those specimens to be included and the number being from 1 to the number to be included.

    translate
    1 taxa_name_1
    2 taxa_name_2
    :
    :
    37 taxa_name_last
    ;


# Set up the HTCondor job

Currently, six of MrBayes parameters can be set.  All others will be set to their defaults.  The six are
<table>
<tr><td>parameter</td><td>meaning</td><td>default</td></tr>
<tr><td>-n</td><td>Number of generations</td><td>1,000,000</td></tr>
<tr><td>-f</td><td>Sampling frequency</td><td>1,000</td></tr>
<tr><td>-u</td><td>Proportion of samples to treat as burnin</td><td>0.25</td></tr>
<tr><td>-s</td><td>Number of substitution types</td><td>2</td></tr>
<tr><td>-r</td><td>Rates</td><td>gamma</td></tr>
<tr><td>-g</td><td>Amino acid model</td><td>None</td></tr>
</table>

There are two additional parameters
<table>
<tr><td>parameter</td><td>meaning</td><td>default</td></tr>
<tr><td>-i</td><td>Name of file with specimens to include</td><td>Include all specimens</td></tr>
<tr><td>-C</td><td>1 if to only include genes found on all taxa</td><td>0</td></tr>
</table>

Once these parameters are considered, run the setup program to create the HTCondor submit and dag file.

    python run_mrbayes.py -i toInclude.txt -C 1 -n 5000000 -f 50000 -s 6

# Run the HTCondor job
To run the job, simply enter the following command from the HTCondor submit node:

    condor_submit_dag run_mrbayes.dag
    
The tree files, \*.t, are gathered into a tarball, run_mrbayes.tar.  This file should be
renamed so as not to be overwritten.  The details of each MrBayes run are placed in the /log directory.
