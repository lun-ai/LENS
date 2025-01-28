:- ['bk.pl'].

% V4 with abstractions
% select_test(+Faults, ?Partition_sizes)
select_test(A,B):- empty_partitions(D),map(partition_sizes,A,C),fold(max_min_size,D,C,B).