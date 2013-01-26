# -*- coding: utf-8 -*-
#
# fixed2free.py: Conversion of Fortran code from fixed to free
#                source form.
#
# Copyright (C) 2012    Elias Rabel
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Script that converts fixed form Fortran code to free form
Usage: file name as first command line parameter

python fixed2free.py file.f > file.f90
"""

# author: Elias Rabel, 2012
# Let me know when you find this script useful:
# ylikx.0 at gmail
# https://www.github.com/ylikx/

# TODO:
# *) Does not handle multi-line strings
# *) problems with comments between continued lines - could be easily fixed
# *) Improve command line usage

class FortranLine:
    def __init__(self, line):
        self.line = line
        self.line_conv = line
        self.isComment = False
        self.isContinuation = False
        self.__analyse()
        
    def __repr__(self):
        return self.line_conv
        
    def continueLine(self):
        self.line_conv = self.line_conv.rstrip() + " &\n"
        
    def __analyse(self):
        line = self.line
        firstchar = line[0] if len(line) > 0 else ''
        self.label = line[1:5].strip().lower() + ' ' if len(line) > 1 else ''
        cont_char = line[5] if len(line) >= 6 else ''
        fivechars = line[1:5] if len(line) > 1 else ''
        self.isShort = (len(line) <= 6)
        
        self.isEmpty = len(line) == 0
        self.isComment = firstchar in "cC*!"
        self.isNewComment = '!' in fivechars and not self.isComment
        self.isOMP = self.isComment and "$omp" == self.label
        if self.isOMP:
            self.isComment = False
            self.label = ''
        self.isCppLine = (firstchar == '#')        
        self.isContinuation = (not (cont_char.isspace() or cont_char == '0') and 
                              (not self.isComment and not self.isNewComment or self.isOMP) 
                               and not self.isCppLine)

        # convert
        self.code = line[6:] if len(line) > 6 else '\n'
        
        if self.isComment:
            #self.line_conv = '!' + gap + cont_char + self.code
            self.line_conv = '!' + line[1:]
        elif self.isNewComment or self.isCppLine:
            self.line_conv = line
        elif self.isOMP:
            self.line_conv = '!' + line[1:5] + ' ' + self.code #TODO
        elif not self.label.isspace():
            self.line_conv = self.label + self.code
        else:
            self.line_conv = self.code
            
        #if self.isContinuation:
        #    self.line_conv = self.code + self.excessLine
            

def convertToFree(stream):
    linestack = []
        
    for line in stream:
        convline = FortranLine(line)
        
        if not convline.isComment and not convline.isNewComment:
            if convline.isContinuation and linestack: 
                linestack[0].continueLine()         
            for l in linestack: yield str(l)
            linestack = []
            
        linestack.append(convline)
        
    for l in linestack: yield str(l)
        

if __name__ == "__main__":

    import sys

    infile = open(sys.argv[1], 'r')
    for line in convertToFree(infile):
        print line,
    
    infile.close()
