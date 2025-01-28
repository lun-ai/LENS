size(L, S) :- is_list(L), length(L, S).

% Not a list
not_list(A) :- \+ is_list(A).

% Create a pair of two numbers
pair(A,B,[A,B]) :- not_list(A), not_list(B).

% Find the smaller and larger number of two numbers
min(A, B, C) :- min_list([A,B],C).
max(A, B, C) :- max_list([A,B],C).