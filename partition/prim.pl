% Higher Order primitive
all(P, X, L):- 
    findall(H, call(P, X, H), L).

% Are multiple gates connected to gate X?
has_branches(X) :- is_connected(X, Y), is_connected(X, Z), Y \== Z.

% Is gate X to gate Y a path without branches?
linear_path(X, X).
linear_path(X, Y) :- is_connected(X, Z), not(has_branches(X)), linear_path(Z, Y).
not_linear_path(X, Y) :- not(linear_path(X, Y)).

% Does gate X share a linear_path with gate Y (Y precedes X if X \== Y)?
same_circuit(X, Y) :- gate(X), gate(Y), N is X // 100, M is Y // 100, N == M.