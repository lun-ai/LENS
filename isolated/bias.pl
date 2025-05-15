% Find node A of a DAG (a circuit) that eventually reaches a given node B
% python hopper/popper.py --kbpath isolated --max-ho 3 --max-rules 2

enable_recursion.

% Predicate declarations
head_pred(isolated,2). 
body_pred(equal,2).
body_pred(not_empty,1).
body_pred(is_connected,2).
body_pred(find_all,3,ho).
body_pred(all,3,ho).

% Types
type(isolated,(element,element)). 
type(equal,(element,element)).
type(not_empty,(list,)).
type(is_connected,(element,element)).
type(find_all,((element,element),element,list)).
type(all,((element,element),list,element)).

% Input-output signatures
direction(isolated,(in,out)). 
direction(equal,(in,out)).
direction(not_empty,(in,)).
direction(is_connected,(in,out)).
direction(find_all,((in,out),in,out)).
direction(all,((in,out),in,out)).

% Constraint the occurrence of predicates
occurFO(equal, 1).
occurFO(not_empty, 1).
occurFO(is_connected, 1).
occurHO(find_all,1).
occurHO(all, 1).

:-
    body_pred(X,_),
    #count{C,X,V: body_literal(C,X,_,V)} > Z, occurFO(X,Z).

:- 
    body_pred(X,_,ho), #count{C,Y,V:  body_literal(C,Y,_,V), X=@honameparse(Y)} >Z, occurHO(X,Z).

:- invented_ho_used(_,_).
% :- not body_literal(0,equal,_,(0,1)).
% :- not body_literal(_,same_circuit,_,(0,1)).
% :- not body_literal(_,find_all___0is_connected,_,(0,2)).
% :- not body_literal(_,all___0isolated,_,(2,1)).
% :- not body_literal(_,not_empty,_,(2,)).