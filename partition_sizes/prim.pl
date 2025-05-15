% length of a list
size(L, S) :- is_list(L), length(L, S).

% Not a list
not_list(A) :- not(is_list(A)).

% Create a pair of two numbers
pair(A,B,[A,B]) :- not_list(A), not_list(B).