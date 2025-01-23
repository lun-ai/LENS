% General BK for all circuits
% Find the smaller and larger number of two numbers
min(A, B, C) :- min_list([A,B],C).
max(A, B, C) :- max_list([A,B],C).

% Is a number A greater than / less than or equal to another number in a triplet
gt(A, B) :- A > B.
leq(A, B) :- A =< B.

% A gate F partitions the circuit: gates on the same branch as F and gates on different branches
same_circuit(X, Y) :- gate(X), gate(Y), N is X // 100, M is Y // 100, N == M.
partition(F, P1, P2) :- all(share_subpath, F, P1), 
                        all(n_subpath, F, P2).

% Are multiple gates connected to gate X?
has_branches(X) :- is_connected(X, Y), is_connected(X, Z), Y \== Z.

% Is gate X to gate Y a path (no branches)?
subpath(X, X).
subpath(X, Y) :- is_connected(X, Z), \+ has_branches(X), subpath(Z, Y).

% Does gate X share a subpath with gate Y (Y precedes X if X \== Y)?
share_subpath(X, Y) :- same_circuit(X, Y), subpath(Y, X).
n_subpath(X, Y) :- same_circuit(X, Y), \+ subpath(Y, X).

% Compute the minimum size of partitions
min_size(P1, P2, N) :- length(P1, N1), length(P2, N2), min(N1, N2, N).
max_size(P1, P2, N) :- length(P1, N1), length(P2, N2), max(N1, N2, N).

% Given a fault, compute the minimum and maximum partition sizes
partition_sizes(F, S) :- partition(F, P1, P2), pair(P1, P2, S).

% Create a pair of partition sizes where the size of the smaller partition is the first element
pair(A,B,[Min,Max]) :- min_size(A, B, Min), max_size(A, B, Max).

% Return the partitions with a larger min partition size
max_min_size([A,B], [C,D], [A,B]) :- not_list(A), not_list(B), not_list(C), not_list(D), max(A, C, A).
max_min_size([A,B], [C,D], [C,D]) :- not_list(A), not_list(B), not_list(C), not_list(D), max(A, C, C).

% Not a list
not_list(A) :- \+ is_list(A).

fst([A, _], A).
snd([_,B],B).

% List manipulation predicates
fold(_P,Acc,[],Acc).
fold(P,Acc,[H|T],Out) :- 
    call(P,Acc,H,Inter),
    fold(P,Inter,T,Out).

map(_P,[],[]).
map(P,[H|T],[H1|T1]) :- 
    call(P,H,H1),
    map(P,T,T1).

all(P, X, L):- 
    findall(H, call(P, X, H), L).

% Get the head/tail of a list
tail([_|T],T).
head([H|_],H).

% Get the head and tail of a list
head_fault(In, H) :- fst(In, List), head(List, H).
tail_faults(In, T) :- fst(In, List), tail(List, T).

empty([]).
% zero(0).
empty_partitions([0, 0]).
eq(A, A).