% HO predicate
all(P, X, L):- 
    findall(H, call(P, X, H), L).

% Are multiple gates connected to gate X?
has_branches(X) :- is_connected(X, Y), is_connected(X, Z), Y \== Z.

% Is gate X to gate Y a path (no branches)?
subpath(X, X).
subpath(X, Y) :- is_connected(X, Z), \+ has_branches(X), subpath(Z, Y).
not_subpath(X, Y) :- \+ subpath(X, Y).

% Does gate X share a subpath with gate Y (Y precedes X if X \== Y)?
same_circuit(X, Y) :- gate(X), gate(Y), N is X // 100, M is Y // 100, N == M.