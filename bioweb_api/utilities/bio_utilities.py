'''
Copyright 2014 Bio-Rad Laboratories, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

@author: Dan DiCara
@date:   Jun 1, 2014
'''
#===============================================================================
# Imports
#===============================================================================
from Bio import SeqIO

#===============================================================================
# Utility Methods
#===============================================================================
def validate_fasta(fasta):
    '''
    Use biopython to read in the FASTA and return True if >1 records are found.
    Otherwise, return False. Fasta can be a file path or a file handle.
    '''
    identifiers = [seq_record.id for seq_record in SeqIO.parse(fasta, "fasta")]
    
    try:
        # If input is a file handle, return it to the start of file.
        fasta.seek(0)
    except:
        pass
    
    return len(identifiers) > 0
        
#===============================================================================
# Run Main
#===============================================================================
if __name__ == "__main__":
    fasta_file = "../../full.fasta"
    print validate_fasta(fasta_file)