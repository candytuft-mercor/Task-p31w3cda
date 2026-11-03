Cause 1: price stored and compared as text. FIxed with a REAL column and float parameters.
Casue 2: pagination offset added one on later pages. Fixed with (page - 1) * page_size.
Also: min_price was exclusive but the docs says inclusive. Fixed with >=.