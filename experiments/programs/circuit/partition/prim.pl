% Given A, find every H that satisfies P(A, H)
find_all(P, A, L):- 
    findall(H, call(P, A, H), L).

% True if P(A, H) holds for every H in L
all(P, [H|T], C) :- 
    call(P, H, C), !,
    all(P, T, C).
all(_, [], _).

empty_list([]).

% Two gates are the same
is_equal(A, A).

% Compare two partitions, return the partitions with a larger min partition size
larger_min_size(A, B, A) :-
    is_list(A),
    is_list(B),
    length(A, 2),
    length(B, 2),
    min_list(A,M1),
    min_list(B,M2),
    max(M1, M2, M1).
larger_min_size(A, B, B) :-
    is_list(A),
    is_list(B),
    length(A, 2),
    length(B, 2),
    min_list(A,M1),
    min_list(B,M2),
    max(M1, M2, M2).

% Find the smaller and larger number of two numbers
min(A, B, C) :- min_list([A,B],C).
max(A, B, C) :- max_list([A,B],C).

% Higher order primitive
% List manipulation predicates
fold(P,Acc,[H|T],Out) :- 
    call(P,Acc,H,Inter),!,
    fold(P,Inter,T,Out).
fold(_P,Acc,[],Acc).

% Map a predicate over a list
map(P,[H|T],[H1|T1]) :- 
    call(P,H,H1),!,
    map(P,T,T1).
map(_P,[],[]).

% The smallest partition base case
empty_partition_sizes([0, 0]).

% Does gate A share a linear path with gate B (B precedes A if A \== B)?
same_circuit(A, B) :- gate(A), gate(B), N is A // 100, M is B // 100, N == M.


% length of a list
size(L, S) :- is_list(L), length(L, S).

% Not a list
not_list(A) :- not(is_list(A)).

% Create a pair of two numbers
pair(A,B,[A,B]) :- not_list(A), not_list(B).