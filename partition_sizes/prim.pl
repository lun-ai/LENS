% length of a list
size(L, S) :- is_list(L), length(L, S).

% Create a pair of two numbers
pair(A,B,[A,B]) :- not_list(A), not_list(B).