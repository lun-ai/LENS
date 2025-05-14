% Two gates are the same
equal(A, A).
not_equal(A, B) :- gate(A), gate(B), not(equal(A, B)).