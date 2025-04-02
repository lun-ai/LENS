% Are multiple gates connected to gate A?
branches(A) :- is_connected(A, B), is_connected(A, C), B \== C.
not_branches(A) :- not(branches(A)).

% Two gates are the same
same_gate(A, A).