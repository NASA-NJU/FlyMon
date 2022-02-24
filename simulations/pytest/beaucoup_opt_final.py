import sys
if len(sys.argv) < 3:
    exit()
m = int(sys.argv[1])
TARGET = int(sys.argv[2])

def compute_expected_activation_time(num_total_coupon, num_to_collect, prob_each):
	# Calculate the expected number of activation needed to complete a coupon collector
	# Note: this function gives expectation, not maximum likelihood. Skewed to right.
	activation_time=0
	for i in range(num_to_collect):
		available_coupon_for_collection=num_total_coupon-i
		total_prob_triggering_any=prob_each*available_coupon_for_collection
		geo_expectation=1.0/total_prob_triggering_any
		activation_time+=geo_expectation
	return activation_time
	# sum of geometric"s expectation
	# if there"s 16 slots, each 1/128:
	# first coupon has prob 16/128
	# next has 15/128, last has 12/128

def find_best_cc_partial_smart(prob_thres, bias_factor, expected_activ, debug=False, SCORING_ALLOWED_BONUS=0.01):
	"Find the optimal partial collection scheme."
	"""
	Note 1: we use all 32 coupons when possible. However, initially we can only use less than 32.
	In this case, just use whatever we have.
	Note 2: when there are >10 coupons, do not use all of them.
	Using 32 out of 32 is not accurate (compared with 16/32 up till 28/32).
	Hence, we use at most 90% coupons if there are >10.
	Note 3: bonus heuristics for using more coupons, even if expectation is alightly further away
	The new |(expected activ-T)/T-1| cannot be 0.05 worse than the original 
	For allocation: again we use scoring. 
	We say 10 coupons compared with 5 coupons give you 100% more relative accuracy.
	However, 15 coupons compared with 10 gives you only 30%.
	After 15, it"s useless.
	"""
	inv_prob_list=[2**i for i in range(1,20)]
	priority_list=[]
	def num_cc_weight(num_cc):
		### New constraint: max bonus based on more coupons is SCORING_ALLOWED_BONUS
		score=0.0
		stage1_cc=min(num_cc,10)
		score+=0.008*(SCORING_ALLOWED_BONUS/0.10)*stage1_cc
		num_cc-=10
		if num_cc>=0:
			stage2_cc=min(num_cc,5)
			score+=0.004*(SCORING_ALLOWED_BONUS/0.10)*stage2_cc
			num_cc-=5
		return score
	
	for inv_prob in inv_prob_list:
		prob_each=(1.0/inv_prob)*bias_factor
		max_coupons_allowed=int(prob_thres/prob_each)
		if max_coupons_allowed>=32:
			max_coupons_allowed=32
		if max_coupons_allowed<1:
			continue
		upper_range=max_coupons_allowed+1
		if max_coupons_allowed>=10:
			upper_range=int(0.9*max_coupons_allowed)+1
		lower_range=1
		if max_coupons_allowed>=10:
			lower_range=int(0.3*max_coupons_allowed)
		for num_to_collect in range(lower_range,upper_range):
			this_exp_activ=compute_expected_activation_time(max_coupons_allowed, num_to_collect, prob_each)
			relative_accuracy=abs(this_exp_activ-expected_activ)/float(expected_activ)
			score=relative_accuracy-num_cc_weight(num_to_collect)
			priority_list.append((score, (this_exp_activ, relative_accuracy), (num_to_collect,max_coupons_allowed),inv_prob))
	#print(sorted(priority_list)[:20])
	opt=sorted(priority_list)[0]
	(num_to_collect,max_coupons_allowed),inv_prob=opt[-2],opt[-1]
	prob_each=(1.0/inv_prob)*bias_factor
	this_exp_activ=compute_expected_activation_time(max_coupons_allowed, num_to_collect, prob_each)
	total_activ_prob=(1.0/inv_prob)*bias_factor*max_coupons_allowed

	if debug:
		print("Finding allocation, for per-packet coupon limit=%f bias=%f activation threshold=%f" %(prob_thres, bias_factor, expected_activ))
		print("Output: each coupon probability 1/%d, collect n=%d out of m=%d coupons; expected activation after %f items, total average per-packet coupon=%f" %(inv_prob, num_to_collect,max_coupons_allowed, this_exp_activ, total_activ_prob))

	return (inv_prob, (num_to_collect,max_coupons_allowed), this_exp_activ, total_activ_prob)
	#num_cc,inv_prob=opt[-2],opt[-1]
	#total_activ_prob, this_exp_activ=activ_matrix[inv_prob][num_cc]
	#return (inv_prob, num_cc, this_exp_activ, total_activ_prob)

