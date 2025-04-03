% Return the partitions with a larger min partition size
max_min_size([A,B], [C,D], [A,B]) :- not_list(A), not_list(B), not_list(C), not_list(D), max(A, C, A).
max_min_size([A,B], [C,D], [C,D]) :- not_list(A), not_list(B), not_list(C), not_list(D), max(A, C, C).

% Find the smaller and larger number of two numbers
min(A, B, C) :- min_list([A,B],C).
max(A, B, C) :- max_list([A,B],C).

% Not a list
not_list(A) :- not(is_list(A)).

% Higher order primitive
% List manipulation predicates
fold(_P,Acc,[],Acc).
fold(P,Acc,[H|T],Out) :- 
    call(P,Acc,H,Inter),
    fold(P,Inter,T,Out).

% Map a predicate over a list
map(_P,[],[]).
map(P,[H|T],[H1|T1]) :- 
    call(P,H,H1),
    map(P,T,T1).

% The smallest partition base case
empty_partitions([0, 0]).