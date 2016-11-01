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
    
    
