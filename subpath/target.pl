subpath(X, X).
subpath(X, Y) :- is_connected(X, Z), \+ has_branches(X), subpath(Z, Y).
not_subpath(X, Y) :- \+ subpath(X, Y).