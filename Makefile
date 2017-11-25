# A simple makefile for compiling three java classes
#

# define a makefile variable for the java compiler
#
#JCC = javac

# define a makefile variable for compilation flags
# the -g flag compiles with debugging information
#
#JFLAGS = -g

# typing 'make' will invoke the first target entry in the makefile 
# (the default one in this case)
#
#default:  fptminer.class
#\DataSetReader.class FPNode.class FPTree.class
# FPTree.class FPNode.class
# AssociationRule.class FrequencyComparator.class fptminer.class

# this target entry builds the Average class
# 
# and the rule associated with this entry gives the command to create it
#
preprocess: preprocess.py
	python preprocess.py

# To start over from scratch, type 'make clean'.  
# Removes all .class files, so that the next make rebuilds them
#
#clean: 
#	$(RM) *.class

