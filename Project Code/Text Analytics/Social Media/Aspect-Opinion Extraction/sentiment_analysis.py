#Alec Larsen - University of the Witwatersrand, South Africa, 2012 import shlex, subprocess
import shlex
import subprocess
import os
import re

def RateSentiment(sentiString):
    currentWorkingDirectory = os.getcwd()
    #open a subprocess using shlex to get the command line string into the correct args list format
    p = subprocess.Popen(shlex.split("java -jar SentiStrength.jar stdin sentidata " + currentWorkingDirectory + "/SentStrength_Data/"),stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    #communicate via stdin the string to be rated. Note that all spaces are replaced with +
    stdout_text, stderr_text = p.communicate(sentiString.replace(" ","+"))
    #remove the tab spacing between the positive and negative ratings. e.g. 1    -5 -> 1-5
    stdout_text = stdout_text.rstrip().replace("\t","")
    positive = int(re.search('([0-5]) -', stdout_text).group(1))
    negative = int(re.search('-([0-5])', stdout_text).group(1))
    #return stdout_text
    return positive - negative