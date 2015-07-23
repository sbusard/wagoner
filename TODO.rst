1. How can we be sure to start and end words as they start and end in the given text?

By adding a special character for starting and ending words, we can start with the starting character and end with the ending character. But with the current generating algorithm, it is impossible to be sure to end at the given length.

One solution would be to use a graph-based solution à la MePGen, where we extract from the table a graph showing possible extensions with weights on arcs, and restrict the graph to the given length, assuring that any generated word is the given length and ends with the ending character.