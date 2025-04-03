% Learn a divide and conquer strategy to partition each input graph
% python hopper/popper.py --kbpath select_test --max-ho 3 --max-rules 3

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

% The number of occurences of map is limited to 0. 
% #defined body_literal/4.
% occurHO(map,1).
% occurHO(fold,0).

% :-
%     body_pred(X,_),
%     #count{C,V: body_literal(C,X,_,V)} > Z, occurFO(X,Z).

% :- body_pred(X,_,ho), #count{C,V:  body_literal(C,Y,_,V), X=@nameparse(Y)} >Z, occurHO(X,Z).