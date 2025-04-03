:- ['prim.pl'].
% Is gate A to gate B a path without branches?
linearpath(A,B):- same_gate(A,B).
linearpath(A,B):- not(branches(A)),is_connected(A,C),linearpath(C,B).

% The negation
not_linearpath(A,B) :- not(linearpath(A,B)).