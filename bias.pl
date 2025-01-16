% Learn a divide and conquer strategy to partition each input graph based on test-outcome pairs

enable_recursion.

head_pred(select_test,3). 
body_pred(empty,1).
body_pred(zero,1).
body_pred(gate,1).
body_pred(leq,2).
body_pred(gt,2).
body_pred(head,2).
body_pred(tail,2).
body_pred(min_partition_size,2).

type(select_test,(list,element,element)). 
type(empty,(list,)).
type(zero,(element,)).
type(gate,(element,)).
type(leq,(element,element)).
type(gt,(element,element)).
type(head,(list,element)).
type(tail,(list,list)).
type(min_partition_size,(element,element)).

direction(select_test,(in,out,out)). 
direction(empty,(in,)).
direction(zero,(in,)).
direction(gate,(in,)).
direction(leq,(in,in)).
direction(gt,(in,in)).
direction(head,(in,out)).
direction(tail,(in,out)).
direction(min_partition_size,(in,out)).

only_once(empty).
only_once(zero).
only_once(gate).
only_once(leq).
only_once(gt).
only_once(head).
only_once(tail).
only_once(min_partition_size).

max_body(10).

:-
    only_once(P),
    clause(C),
    #count{Vars : body_literal(C,P,A,Vars)} > 1.

:-
    body_literal(_,leq,1,_), body_literal(_,gt,1,_).

% included_clause(Cl, id1) :-
%     head_literal(Cl,select_test,3,(0,1,2)),
%     body_literal(Cl,empty,1,(0,)),
%     body_literal(Cl,zero,1,(1,)),
%     body_literal(Cl,gate,1,(2,)).

% :- 
%     included_clause(Cl, id1),
%     clause_size(Cl, 3).

% :-  
%     body_literal(0,head,2,_).

% :-  
%     body_literal(0,tail,2,_).

% :-
%     body_literal(A,empty,1,_),
%     body_literal(A,zero,1,_),
%     body_literal(A,gate,1,_),
%     A > 0.

% :- 
%     body_literal(2,tail,_,_).

% :-
%     body_literal(2,gt,_,_).

% :-
%     body_literal(2,leq,_,_).