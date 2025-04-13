% Learn a divide and conquer strategy to partition each input graph
% python hopper/popper.py --kbpath optimal_partition_sizes --max-ho 3 --max-rules 3

% Predicate declarations
head_pred(optimal_partition_sizes,2). 
body_pred(partition_sizes,2). 
body_pred(empty_partition_sizes,1).
body_pred(larger_min_size,3).
body_pred(map,3,ho).
body_pred(fold,4,ho).

% Types
type(optimal_partition_sizes,(list,list)). 
type(partition_sizes,(element,list)). 
type(empty_partition_sizes,(list,)).
type(larger_min_size,(list,list,list)).
type(map,((element,list),list,list)).
type(fold,((list,list,list),list,list,list)).

% Input-output signatures
direction(optimal_partition_sizes,(in,out)). 
direction(partition_sizes,(in,out)). 
direction(empty_partition_sizes,(out,)).
direction(larger_min_size,(in,in,out)).
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