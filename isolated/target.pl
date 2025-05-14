:- ['prim.pl'].

% inv_1(A, B) :- path(A, B), is_connected(A,B).
% inv_2(A, B) :- path(A, B), equal(A, B).
% inv_3(A, B) :- path(A, B), not_equal(A, B).
% isolated(A, B) :- inv_2(A, B), equal(A, B).
% isolated(A, B) :- inv_3(A, B), find_all(inv_1, A, C), all(isolated, C, B).

% isolated(A, B) :- equal(A, B).
% isolated(A, B) :- path(A, B), not_equal(A, B), find_all(is_connected, A, C), all(isolated, C, B).

% isolated(A, B) :- equal(A, B).
% isolated(A, B) :- same_circuit(A, B), find_all(is_connected, A, C), is_not_empty(C), all(isolated, C, B).

isolated(A,B):- equal(A,B).
isolated(A,B):- find_all(is_connected,A,C),all(equal,C,B).
isolated(A,B):- same_circuit(A,B),is_connected(B,D),find_all(is_connected,D,C),is_not_empty(C),all(same_circuit,C,E),equal(E,A).