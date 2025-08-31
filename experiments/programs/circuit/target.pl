%%%%%%%%%%%%%%%%%%%% Main program %%%%%%%%%%%%%%%%%%%%

exclusively_powers(A,B):- is_equal(A,B).
exclusively_powers(A,B):- find_all(is_connected,A,C),not(empty_list(C)),all(exclusively_powers,C,B).

inv_ho_1(A,B):- same_circuit(A,B),exclusively_powers(B,A).
inv_ho_0(A,B):- same_circuit(A,B),not(exclusively_powers(B,A)).
partition(A,B,C):- find_all(inv_ho_0,A,C),find_all(inv_ho_1,A,B).

partition_sizes(A,B):- partition(A,E,D),size(D,C),size(E,F),pair(C,F,B).
partition_sizes(A,B):- partition(A,D,E),size(D,C),size(E,F),pair(C,F,B).

optimal_partition_sizes(A,B):- empty_partition_sizes(C),map(partition_sizes,A,D),fold(larger_min_size,C,D,B).

optimal_test(A,B):- optimal_partition_sizes(A,D),gate(C),test_point_label(C,B),partition_sizes(C,D).

%%%%%%%%%%%%%%%%%%%% Primitives %%%%%%%%%%%%%%%%%%%%

find_all(P, A, L):- 
    findall(H, call(P, A, H), L).

all(P, [H|T], C) :- 
    call(P, H, C), !,
    all(P, T, C).
all(_, [], _).

empty_list([]).

is_equal(A, A).

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

min(A, B, C) :- min_list([A,B],C).
max(A, B, C) :- max_list([A,B],C).

fold(P,Acc,[H|T],Out) :- 
    call(P,Acc,H,Inter),!,
    fold(P,Inter,T,Out).
fold(_P,Acc,[],Acc).

map(P,[H|T],[H1|T1]) :- 
    call(P,H,H1),!,
    map(P,T,T1).
map(_P,[],[]).

empty_partition_sizes([0, 0]).

same_circuit(A, B) :- gate(A), gate(B), N is A // 100, M is B // 100, N == M.


size(L, S) :- is_list(L), length(L, S).

not_list(A) :- not(is_list(A)).

pair(A,B,[A,B]) :- not_list(A), not_list(B).