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
The file extensions must be ".nex".

To only run MrBayes on a particular subset of taxa, create a file in the MrBayes directory with the following format:

    translate
    1 taxa_name_1
    2 taxa_name_2
    :
    :
    37 taxa_name_last
    ;


# Set up the HTCondor job

Currently, six of MrBayes parameters can be set different from their defaults.  These are
<table>
<tr><td>parameter</td><td>meaning</td><td>default</td></tr>
<tr><td>-n</td><td>Number of generations</td><td>1,000,000</td></tr>
<tr><td>-f</td><td>Sampling frequency</td><td>1,000</td></tr>
<tr><td>-u</td><td>Proportion of samples to treat as burnin</td><td>0.25</td></tr>
<tr><td>-s</td><td>Number of substitution types</td><td>2</td></tr>
<tr><td>-r</td><td>Rates</td><td>gamma</td></tr>
<tr><td>-g</td><td>Amino acid model</td><td>None</td></tr>
</table>
