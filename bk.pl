% General BK for all circuits
Current flow from X to Y when gate Z is faulty
current(src, Y, Z) :- out(X, Y), X \== Z.
current(X, Y, Z) :- flow(X, Z), out(U, Y), U \== Z.
% current(src, Y) :- out(X, Y).
% current(X, Y) :- flow(X).

% A faulty gate partitions the circuit: electric-flowing and non-electric-flowing gate outputs
partition(F, (P1, P2)) :- findall(Y, (gate(X), out(X, Y), flow(Y, F)), P1), 
                          findall(Y, (gate(X), out(X, Y), \+ flow(Y, F)), P2).

% % Which gates' outputs only affect the current gate's output?
% has_branches(X) :- current(X, Y, _), current(X, Z, _), Y \== Z.
% % Is X on the same branch as Y where X is an upstream gate?
% on_same_branch(X, Y) :- current(X, Y, _), \+ has_branches(X).

% partition(F, (P1, P2)) :- findall(X, (gate(X), on(light, X)), P1), findall(X, (gate(X), \+ on(light, X)), P2).


% Minimum size of partitions
min_size((P1, P2), N) :- length(P1, N1), length(P2, N2), N is min(N1, N2).
min_partition_size(F, N) :- partition(F, Ps), min_size(Ps, N).

% If a number is greater than / less than or equal to another number in a triplet
gt(A, (_, B, _)) :- A > B.
leq(A, (_, B, _)) :- A =< B.

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

% All hypothesised fault positives are
fault(In, H) :- fst(In, List), head(List, H).
faults(In, T) :- fst(In, List), tail(List, T).

empty([]).
eq(A, A).

% dnc((+Faults, +Size, +Test), (?Faults1, ?Size1, ?Test1))
% dnc_1(In, Out) :- fst_head(In, F), update_trd(In, F, In1), dnc_2(In1, Out).
% dnc_2(In, Out) :- fst_tail(In, T), update_fst(In, T, In1), dnc(In1, Out).
dnc(In, Out) :- fst(In, L), empty(L), eq(In, Out). 
dnc(In, Out) :- fault(In, F), min_partition_size(F, K), gt(K, In), faults(In, Fs), out(F, O), update_all(In, Fs, K, O, In1), dnc(In1, Out).
dnc(In, Out) :- fault(In, F), min_partition_size(F, K), leq(K, In), faults(In, Fs), update_fst(In, Fs, In1), dnc(In1, Out).