% Learn a divide and conquer strategy to partition each input graph
% python hopper/popper.py --kbpath . --max-ho 3 --max-body 10 --max-rules 3

% Predicate declarations
head_pred(select_test,2). 
body_pred(partition_sizes,2). 
body_pred(empty_partitions,1).
body_pred(max_min_size,3).
body_pred(map,3,ho).
body_pred(fold,4,ho).

% Types
type(select_test,(list,list)). 
type(partition_sizes,(element,list)). 
type(empty_partitions,(list,)).
type(max_min_size,(list,list,list)).
type(map,((element,list),list,list)).
type(fold,((list,list,list),list,list,list)).

% Input-output signatures
direction(select_test,(in,out)). 
direction(partition_sizes,(in,out)). 
direction(empty_partitions,(out,)).
direction(max_min_size,(in,in,out)).
direction(map,((in,out),in,out)).
direction(fold,((in,in,out),in,in,out)).

% :- 
%     body_literal(C1,partition,_,_),
%     body_literal(C2,pair,_,_),
%     C1 != C2.

% :- 
%     body_literal(C1,max,_,_),
%     body_literal(C2,min,_,_),
%     C1 != C2.

% % The number of occurences of map is limited to 0.  

% #script (python)
% from clingo.symbol import *
% def nameparse(t):
%     return Function(name=t.name.split("___")[0])
% #end.

% #defined body_literal/4.
% occurHO(map,1).
% occurHO(fold,1).
% occurFO(empty_partitions,1).
% occurFO(max_min_size,1).
% occurFO(partition,1).
% occurFO(pair,1).

% :-
%     body_pred(X,_),
%     #count{C,V: body_literal(C,X,_,V)} > Z, occurFO(X,Z).

% :- body_pred(X,_,ho), #count{C,V:  body_literal(C,Y,_,V), X=@nameparse(Y)} >Z, occurHO(X,Z).