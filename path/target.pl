:- ['prim.pl'].

% Is gate A to gate B a path?
path(A,B) :- equal(A,B).
path(A,B) :- is_connected(A,C), path(C,B).