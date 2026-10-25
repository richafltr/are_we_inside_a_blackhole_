n = inputs["n"]
k = sum(rng.random() < inputs["selection_probability"] for j in range(n))
pvalue = min(1.0, 2 * sum(math.comb(n, j) * 0.5**n for j in range(min(k, n-k)+1)))
result = {"n": n, "k": k, "p_value": pvalue, "generating_probability": inputs["selection_probability"]}
