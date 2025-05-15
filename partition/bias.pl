% Learn to partition an input graph
% python hopper/popper.py --kbpath partition --max-ho 2 --max-rules 3 --max-body 2

% Predicate declarations
head_pred(partition,3). 
body_pred(isolated,2).
body_pred(not_isolated,2).
body_pred(same_circuit,2).
body_pred(find_all,3,ho).

% Types
type(partition,(element,list,list)). 
type(isolated,(element,element)).
type(not_isolated,(element,element)).
type(same_circuit,(element,element)).
type(find_all,((element,element),element,list)).

% Input-output signatures
direction(partition,(in,out,out)). 
direction(isolated,(in,out)).
direction(not_isolated,(in,out)).
direction(same_circuit,(in,out)).
direction(find_all,((in,out),in,out)).

% Must use the following predicates
:- not body_literal(_,same_circuit,_,(0,1)).
:- not body_literal(_,isolated,_,(1,0)).
:- not body_literal(_,not_isolated,_,(1,0)).