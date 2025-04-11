:- ['bk.pl'].

select_test(A,B):- empty_partitions(D),map(partition_sizes,A,C),fold(larger_min_size,D,C,B).