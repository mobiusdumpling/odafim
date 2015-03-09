import random
import numpy as np

def flatten(lst):
    return [x for y in lst for x in y]

def almost_int(x):
    return abs(x - round(x))<=0.00001

def bader_ofer(fractional_results):
    parties = list(fractional_results) # give consistent order to parties
    fractional_mand = np.array([fractional_results[party] for party in parties])
    tot_mandates = fractional_mand.sum()
    assert almost_int(tot_mandates)
    result = np.floor(fractional_mand)
    leftover_mand = int(round(tot_mandates - result.sum()))
    for i in range(leftover_mand):
        bader_ofer_scores = fractional_mand / (result+1)
        odef_winner = np.argmax(bader_ofer_scores)
        result[odef_winner] += 1
    result = {parties[i] : result[i] for i in range(len(result))}
    return result

def run_simulation(survey, odafim):
    noise_multiplier = 1.0
    assert int(noise_multiplier) == noise_multiplier
    assert set(flatten(odafim)) <= set(survey)
    no_odafim = set(survey) - set(flatten(odafim))
    parties = list(survey) # ordered list of parties
    tot_mandates = sum(survey.values())
    assert int(tot_mandates) == tot_mandates
    total = {party : list() for party in parties}
    num_simulations = 100000
    for _ in range(num_simulations):
        noisy_survey = {party : survey[party] + (random.random() - 0.5) * noise_multiplier for party in survey}
        assert all([v>0 for v in noisy_survey.values()])
        norm_factor1 = tot_mandates / sum(noisy_survey.values())
        noisy_survey = {party : noisy_survey[party] * norm_factor1 for party in noisy_survey}
        bader_ofer_step1 = {party : noisy_survey[party] for party in no_odafim}
        bader_ofer_step1.update({pair : noisy_survey[pair[0]] + noisy_survey[pair[1]] for pair in odafim})
        step1_res = bader_ofer(bader_ofer_step1)
        assert abs(sum(step1_res.values())-120.0)<=0.0001
        simu_result = {party : step1_res[party] for party in no_odafim}
        for pair in odafim:
            norm_factor2 = step1_res[pair] / (noisy_survey[pair[0]] + noisy_survey[pair[1]])
            pair_bader_ofer = {party : noisy_survey[party] * norm_factor2 for party in pair}
            simu_result.update(bader_ofer(pair_bader_ofer))
        assert abs(sum(simu_result.values())-120)<=0.0001
        for party in parties:
            total[party].append(simu_result[party])
    result = {party : sum(total[party]) / num_simulations for party in parties}
    return result

March6_survey =\
       {"avoda" : 24,
        "likud" : 23,
        "arab" : 13,
        "lapid" : 12,
        "bennet" : 11,
        "kahlon" : 9,
        "shas" : 8,
        "aguda" : 6,
        "liberman" : 5,
        "meretz" : 5,
        "yahad" : 4}
assert sum(March6_survey.values()) == 120
alternative_odafim_agreements = [("avoda", "lapid"),
                                 ("arab", "meretz"),
                                 ("likud", "bennet"),
                                 ("aguda", "shas"),
                                 ("liberman", "kahlon")]
normal_odafim_agreements = [("avoda", "meretz"),
                            ("likud", "bennet"),
                            ("aguda", "shas"),
                            ("liberman", "kahlon")]


normal_results = run_simulation(March6_survey, normal_odafim_agreements)
alt_results = run_simulation(March6_survey, alternative_odafim_agreements)
alt_gains = {party : alt_results[party] - normal_results[party] for party in normal_results}
for party in normal_results:
    print "With the proposed change to the odafim agreement,", party, "would have gained", round(alt_gains[party], 3), "mandates"

center_left_coalition = {"arab", "avoda", "meretz", "lapid"}
extended_center_left_coalition = {"arab", "avoda", "meretz", "lapid", "shas", "aguda", "kahlon"}
print "In total, the center-left coalition would gain", sum([alt_gains[party] for party in center_left_coalition]), "mandates"
print "The extended center-left coalition (with kahlon and religious parties) would gain", sum([alt_gains[party] for party in extended_center_left_coalition]), "mandates"
