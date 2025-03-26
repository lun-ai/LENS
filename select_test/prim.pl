% General BK for all circuits

% Return the partitions with a larger min partition size
max_min_size([A,B], [C,D], [A,B]) :- not_list(A), not_list(B), not_list(C), not_list(D), max(A, C, A).
max_min_size([A,B], [C,D], [C,D]) :- not_list(A), not_list(B), not_list(C), not_list(D), max(A, C, C).

% List manipulation predicates
fold(_P,Acc,[],Acc).
fold(P,Acc,[H|T],Out) :- 
    call(P,Acc,H,Inter),
    fold(P,Inter,T,Out).

map(_P,[],[]).
map(P,[H|T],[H1|T1]) :- 
    call(P,H,H1),
    map(P,T,T1).

empty_partitions([0, 0]).