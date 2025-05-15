% Given A, find every H that satisfies P(A, H)
find_all(P, A, L):- 
    findall(H, call(P, A, H), L).

% True if P(A, H) holds for every H in L
all(P, [H|T], C) :- 
    call(P, H, C), !,
    all(P, T, C).
all(_, [], _).

% Does gate A share a linear path with gate B (B precedes A if A \== B)?
% same_circuit(A, B) :- gate(A), gate(B), N is A // 100, M is B // 100, N == M.

empty([]).
not_empty(L) :- not(empty(L)), forall(member(E, L), nonvar(E)).