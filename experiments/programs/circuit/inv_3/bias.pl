% Predicate declarations
head_pred(inv_3,2). 
body_pred(inv_2,2). 
body_pred(empty_partition_sizes,1).
body_pred(larger_min_size,3).
body_pred(map,3,ho).
body_pred(fold,4,ho).

% Types
type(inv_3,(list,list)). 
type(inv_2,(element,list)). 
type(empty_partition_sizes,(list,)).
type(larger_min_size,(list,list,list)).
type(map,((element,list),list,list)).
type(fold,((list,list,list),list,list,list)).

% Input-output signatures
direction(inv_3,(in,out)). 
direction(inv_2,(in,out)). 
direction(empty_partition_sizes,(out,)).
direction(larger_min_size,(in,in,out)).
direction(map,((in,out),in,out)).
direction(fold,((in,in,out),in,in,out)).

% Turn off invented predicates in HO
:- invented_ho_used(_,_).