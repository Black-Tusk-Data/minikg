"""
Thinking out loud:
 - for each code file, identify the entities defined there (maybe those exported, maybe just those defined) Include member functions of classes!
 - for each code file, identify the imported code files
   - can do this by passing in the list of all known code files,
     and the top part of the target file
 - now that we know the imported code files, gather all the entities defined in those imported files and identify all the entiites that are used in the file, prefixed with the imported file name
 - finally, for each entity defined in the target file, identify any edges to all the entities that we're aware of
"""
