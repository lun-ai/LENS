% Given A, find every H that satisfies P(A, H)
find_all(P, A, L):- 
    findall(H, call(P, A, H), L).

% True if P(A, H) holds for every H in L
all(P, [H|T], C) :- 
    call(P, H, C), !,
    all(P, T, C).
all(_, [], _).

empty([]).
not_empty(L) :- not(empty(L)), forall(member(E, L), nonvar(E)).

% Two gates are the same
equal(A, A).
not_equal(A, B) :- gate(A), gate(B), not(equal(A, B)).