% Find node A of a DAG (a circuit) that eventually reaches a given node B
% python hopper/popper.py --kbpath isolated --max-ho 3

enable_recursion.

% Predicate declarations
head_pred(isolated,2). 
body_pred(equal,2).
body_pred(is_not_empty,1).
body_pred(same_circuit,2).
body_pred(is_connected,2).
body_pred(find_all,3,ho).
body_pred(all,3,ho).

% Types
type(isolated,(element,element)). 
type(equal,(element,element)).
type(is_not_empty,(list,)).
type(same_circuit,(element,element)).
type(is_connected,(element,element)).
type(find_all,((element,element),element,list)).
type(all,((element,element),list,element)).

% Input-output signatures
direction(isolated,(in,out)). 
direction(equal,(in,out)).
direction(is_not_empty,(in,)).
direction(same_circuit,(in,out)).
direction(is_connected,(in,out)).
direction(find_all,((in,out),in,out)).
direction(all,((in,out),in,out)).

% Constraint the occurrence of predicates
occurFO(equal, 1).
occurFO(is_not_empty, 1).
occurFO(same_circuit, 1).
occurFO(is_connected, 1).
occurHO(find_all,1).
occurHO(all, 1).

:-
    body_pred(X,_),
    #count{C,X,V: body_literal(C,X,_,V)} > Z, occurFO(X,Z).

:- 
    body_pred(X,_,ho), #count{C,Y,V:  body_literal(C,Y,_,V), X=@honameparse(Y)} >Z, occurHO(X,Z).

:-
    invented_ho_used(P,_),
    head_literal(C,P,_,_),
    not body_size(C,1).

:-
    invented_ho_used(P,_),
    head_literal(C,P,_,Vars1),
    body_literal(C,_,_,Vars2),
    Vars1!= Vars2.
    
% :-
%     invented_ho_used(P,_),
%     not head_pred(P,_),
%     not body_pred(P,_). 

% :- 
%     invented_ho_used(_,_).