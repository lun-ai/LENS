% Learn a divide and conquer strategy to partition each input graph based on test-outcome pairs

enable_recursion.

head_pred(dnc,2). 
body_pred(fst,2).
body_pred(empty,1).
body_pred(eq,2).
body_pred(leq,2).
body_pred(gt,2).
body_pred(fault,2).
body_pred(faults,2).
body_pred(out,2).
body_pred(update_fst,3).
body_pred(update_all,2).
body_pred(min_partition_size,2).

type(dnc,(tuple,tuple)). 
type(fst,(tuple,list)).
type(empty,(list)).
type(eq,(tuple,tuple)).
type(leq,(num,tuple)).
type(gt,(num,tuple)).
type(fault,(tuple,element)).
type(faults,(tuple,list)).
type(out,(num,sym)).
type(update_fst,(tuple,list,tuple)).
type(update_all,(tuple,list,num,sym,tuple)).
type(min_partition_size,(num,num)).


direction(dnc,(in,out)). 
direction(fst,(in,out)).
direction(empty,(in)).
direction(eq,(in,in)).
direction(leq,(in,in)).
direction(gt,(in,in)).
direction(fault,(in,out)).
direction(faults,(in,out)).
direction(out,(in,out)).
direction(update_fst,(in,in,out)).
direction(update_all,(in,in,in,in,out)).
direction(min_partition_size,(in,out)).