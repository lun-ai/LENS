% :- ['all_bk.pl'].

% General BK for all circuits
% Find the smaller and larger number of two numbers
min(A, B, C) :- min_list([A,B],C).
max(A, B, C) :- max_list([A,B],C).

% Is a number A greater than / less than or equal to another number in a triplet
gt(A, B) :- A > B.
leq(A, B) :- A =< B.

% A gate F partitions the circuit: gates on the same branch as F and gates on different branches
partition(F, P1, P2) :- findall(X, (gate(X), on_same_branch(X, F)), P1), 
                        findall(X, (gate(X), \+ on_same_branch(X, F)), P2).

% Are multiple gates connected to gate X?
has_branches(X) :- is_connected(X, Y), is_connected(X, Z), Y \== Z.

% Is gate X on the same branch as Y where X is an upstream gate?
on_same_branch(X, X).
on_same_branch(X, Y) :- is_connected(X, Z), \+ has_branches(X), on_same_branch(Z, Y).

% Compute the minimum size of partitions
min_size(P1, P2, N) :- length(P1, N1), length(P2, N2), N is min(N1, N2).
max_size(P1, P2, N) :- length(P1, N1), length(P2, N2), N is max(N1, N2).

% Given a fault, compute the minimum and maximum partition sizes
partition_sizes(F, (Min, Max)) :- partition(F, P1, P2), min_size(P1, P2, Min), max_size(P1, P2, Max).
min_partition_size(F, N) :- partition_sizes(F, (N, _)).

% Return the partitions with a larger min partition size
max_min_size((A,B), (C,_), (A,B)) :- max(A, C, A).
max_min_size((A,_), (C,D), (C,D)) :- max(A, C, C).

% Get an element of a triplet
fst((A, _, _), A).
snd((_, B, _), B).
trd((_, _, C), C).

% Update an element/all elements of a triplet
update_fst((_,B,C),A1,(A1,B,C)).
update_snd((A,_,C),B1,(A,B1,C)).
update_trd((A,B,_),C1,(A,B,C1)).
update_all(In, Arg1, Arg2, Arg3, Out) :- update_fst(In, Arg1, In1), update_snd(In1, Arg2, In2), update_trd(In2, Arg3, Out).

% Get the head/tail of a list
tail([_|T],T).
head([H|_],H).

% Get the head and tail of a list
head_fault(In, H) :- fst(In, List), head(List, H).
tail_faults(In, T) :- fst(In, List), tail(List, T).

empty([]).
zero(0).
% empty_partitions((0, 0)).
eq(A, A).

% V1 arguments are tuples
% select_test((+Faults, +Size, +Test), (?Faults1, ?Size1, ?Test1))
% select_test(In, Out) :- fst(In, L), empty(L), eq(In, Out). 
% select_test(In, Out) :- head_fault(In, F), min_partition_size(F, K), snd(In, N), gt(K, N), tail_faults(In, Fs), out(F, O), update_all(In, Fs, K, O, In1), select_test(In1, Out).
% select_test(In, Out) :- head_fault(In, F), min_partition_size(F, K), snd(In, N), leq(K, N), tail_faults(In, Fs), update_fst(In, Fs, In1), select_test(In1, Out).

% V2 
% select_test(+Faults, ?Size, ?Test)
select_test(Faults, Size, Test) :- empty(Faults), zero(Size), gate(Test). 
select_test(Faults, Size, Test) :- head(Faults, Test), tail(Faults, Fs), 
                                   select_test(Fs, K, T), gate(T), 
                                   min_partition_size(Test, Size), gt(Size, K).
select_test(Faults, Size, Test) :- head(Faults, T), tail(Faults, Fs), 
                                   select_test(Fs, Size, Test),  
                                   min_partition_size(T, K), leq(K, Size).

% V3
% select_test(+Faults, ?Partitions)
% select_test(Faults, Partitions) :- empty(Faults), empty_partitions(Partitions).
% select_test(Faults, Partitions) :- head(Faults, Test), tail(Faults, Fs), 
%                                    select_test(Fs, P1),
%                                    partition_sizes(Test, P2),
%                                    max_min_size(P1, P2, Partitions).