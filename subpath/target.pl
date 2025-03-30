subpath(X, X).
subpath(X, Y) :- is_connected(X, Z), not(has_branches(X)), subpath(Z, Y).
not_subpath(X, Y) :- not(subpath(X, Y)).