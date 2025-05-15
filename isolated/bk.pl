:- ['../ex_3/bk.pl'].
:- ['prim.pl'].


% % BK of circuit graphs
% % Circuit gates (AND gates with one input) labelled with numbers
% gate(1).
% gate(2).
% gate(3).
% gate(4).
% gate(5).
% gate(6).
% gate(7).

% % The output of ith gate is labelled with a symbol
% out(0, src).
% out(1, a).
% out(2, b).
% out(3, c).
% out(4, d).
% out(5, e).
% out(6, f).
% out(7, g).
% out(8, light).

% % Is Gate2 connected to gate Gate1?
% is_connected(0, 1).
% is_connected(1, 2).
% is_connected(2, 3).
% is_connected(3, 4).
% is_connected(3, 5).
% is_connected(4, 6).
% is_connected(5, 7).
% is_connected(6, 8).
% is_connected(7, 8).

% % Is gate A to gate B a path?
% path(A,B) :- equal(A,B).
% path(A,B) :- is_connected(A,C), path(C,B).

% % Two gates are the same
% equal(A, A).
% not_equal(A, B) :- gate(A), gate(B), not(equal(A, B)).

% % Given A, find every H that satisfies P(A, H)
% find_all(P, A, L):- 
%     findall(H, call(P, A, H), L).

% % True if P(A, H) holds for every H in L
% all(P, [H|T], C) :- 
%     call(P, H, C), !,
%     all(P, T, C).
% all(_, [], _).

% % Does gate A share a linear path with gate B (B precedes A if A \== B)?
% same_circuit(A, B) :- gate(A), gate(B), N is A // 100, M is B // 100, N == M.

% empty([]).
% is_not_empty(L) :- not(empty(L)), forall(member(E, L), nonvar(E)).