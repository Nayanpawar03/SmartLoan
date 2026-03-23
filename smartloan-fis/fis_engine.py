# smartloan-fis/fis_engine.py

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


def build_fis():
    # --- Stage 1 Inputs ---
    payment_history = ctrl.Antecedent(np.arange(0, 101, 1), 'payment_history')
    utilization      = ctrl.Antecedent(np.arange(0, 101, 1), 'utilization')
    dti              = ctrl.Antecedent(np.arange(0, 101, 1), 'dti')
    income           = ctrl.Antecedent(np.arange(0, 500001, 5000), 'income')
    emi              = ctrl.Antecedent(np.arange(0, 50001, 1000), 'emi')
    credit_history   = ctrl.Antecedent(np.arange(0, 21, 1), 'credit_history')
    inquiries        = ctrl.Antecedent(np.arange(0, 11, 1), 'inquiries')

    behaviour_score  = ctrl.Consequent(np.arange(0, 101, 1), 'behaviour_score')
    financial_score  = ctrl.Consequent(np.arange(0, 101, 1), 'financial_score')
    experience_score = ctrl.Consequent(np.arange(0, 101, 1), 'experience_score')

    payment_history['poor']    = fuzz.trimf(payment_history.universe, [0, 0, 60])
    payment_history['average'] = fuzz.trimf(payment_history.universe, [50, 70, 90])
    payment_history['good']    = fuzz.trimf(payment_history.universe, [80, 100, 100])

    utilization['low']    = fuzz.trimf(utilization.universe, [0, 0, 30])
    utilization['medium'] = fuzz.trimf(utilization.universe, [20, 50, 80])
    utilization['high']   = fuzz.trimf(utilization.universe, [70, 100, 100])

    dti['low']    = fuzz.trimf(dti.universe, [0, 0, 25])
    dti['medium'] = fuzz.trimf(dti.universe, [20, 40, 60])
    dti['high']   = fuzz.trimf(dti.universe, [50, 100, 100])

    income['low']    = fuzz.trimf(income.universe, [0, 0, 100000])
    income['medium'] = fuzz.trimf(income.universe, [50000, 200000, 350000])
    income['high']   = fuzz.trimf(income.universe, [300000, 500000, 500000])

    emi['low']    = fuzz.trimf(emi.universe, [0, 0, 15000])
    emi['medium'] = fuzz.trimf(emi.universe, [10000, 25000, 40000])
    emi['high']   = fuzz.trimf(emi.universe, [35000, 50000, 50000])

    credit_history['short']  = fuzz.trimf(credit_history.universe, [0, 0, 5])
    credit_history['medium'] = fuzz.trimf(credit_history.universe, [3, 8, 15])
    credit_history['long']   = fuzz.trimf(credit_history.universe, [10, 20, 20])

    inquiries['few']      = fuzz.trimf(inquiries.universe, [0, 0, 2])
    inquiries['moderate'] = fuzz.trimf(inquiries.universe, [1, 4, 7])
    inquiries['many']     = fuzz.trimf(inquiries.universe, [6, 10, 10])

    behaviour_score['low']    = fuzz.trimf(behaviour_score.universe, [0, 0, 40])
    behaviour_score['medium'] = fuzz.trimf(behaviour_score.universe, [30, 50, 70])
    behaviour_score['high']   = fuzz.trimf(behaviour_score.universe, [60, 100, 100])

    financial_score['low']    = fuzz.trimf(financial_score.universe, [0, 0, 40])
    financial_score['medium'] = fuzz.trimf(financial_score.universe, [30, 50, 70])
    financial_score['high']   = fuzz.trimf(financial_score.universe, [60, 100, 100])

    experience_score['low']    = fuzz.trimf(experience_score.universe, [0, 0, 40])
    experience_score['medium'] = fuzz.trimf(experience_score.universe, [30, 50, 70])
    experience_score['high']   = fuzz.trimf(experience_score.universe, [60, 100, 100])

    rules1 = [
        ctrl.Rule(payment_history['good'] & utilization['low'],    behaviour_score['high']),
        ctrl.Rule(payment_history['good'] & utilization['medium'], behaviour_score['high']),
        ctrl.Rule(payment_history['good'] & utilization['high'],   behaviour_score['medium']),
        ctrl.Rule(payment_history['average'] & utilization['low'],    behaviour_score['high']),
        ctrl.Rule(payment_history['average'] & utilization['medium'], behaviour_score['medium']),
        ctrl.Rule(payment_history['average'] & utilization['high'],   behaviour_score['low']),
        ctrl.Rule(payment_history['poor'] & utilization['low'],    behaviour_score['medium']),
        ctrl.Rule(payment_history['poor'] & utilization['medium'], behaviour_score['low']),
        ctrl.Rule(payment_history['poor'] & utilization['high'],   behaviour_score['low']),
        ctrl.Rule(dti['low'] & income['high'] & emi['low'],        financial_score['high']),
        ctrl.Rule(dti['low'] & income['medium'],                   financial_score['high']),
        ctrl.Rule(dti['medium'] & income['medium'] & emi['medium'],financial_score['medium']),
        ctrl.Rule(dti['low'] & income['low'],                      financial_score['medium']),
        ctrl.Rule(dti['high'] & emi['high'],                       financial_score['low']),
        ctrl.Rule(dti['high'] & income['low'],                     financial_score['low']),
        ctrl.Rule(emi['high'],                                     financial_score['low']),
        ctrl.Rule(dti['medium'] & income['high'],                  financial_score['medium']),
        ctrl.Rule(dti['medium'] & emi['high'],                     financial_score['low']),
        ctrl.Rule(credit_history['long'] & inquiries['few'],       experience_score['high']),
        ctrl.Rule(credit_history['long'] & inquiries['moderate'],  experience_score['medium']),
        ctrl.Rule(credit_history['long'] & inquiries['many'],      experience_score['medium']),
        ctrl.Rule(credit_history['medium'] & inquiries['few'],     experience_score['medium']),
        ctrl.Rule(credit_history['medium'] & inquiries['moderate'],experience_score['medium']),
        ctrl.Rule(credit_history['medium'] & inquiries['many'],    experience_score['low']),
        ctrl.Rule(credit_history['short'] & inquiries['few'],      experience_score['medium']),
        ctrl.Rule(credit_history['short'] & inquiries['moderate'], experience_score['low']),
        ctrl.Rule(credit_history['short'] & inquiries['many'],     experience_score['low']),
    ]

    fis1_ctrl = ctrl.ControlSystem(rules1)
    fis1      = ctrl.ControlSystemSimulation(fis1_ctrl)

    # --- Stage 2 ---
    behaviour  = ctrl.Antecedent(np.arange(0, 101, 1), 'behaviour')
    financial  = ctrl.Antecedent(np.arange(0, 101, 1), 'financial')
    experience = ctrl.Antecedent(np.arange(0, 101, 1), 'experience')
    credit_score = ctrl.Consequent(np.arange(300, 851, 1), 'credit_score')

    behaviour['low']    = fuzz.trimf(behaviour.universe, [0, 0, 40])
    behaviour['medium'] = fuzz.trimf(behaviour.universe, [30, 50, 70])
    behaviour['high']   = fuzz.trimf(behaviour.universe, [60, 100, 100])

    financial['low']    = fuzz.trimf(financial.universe, [0, 0, 40])
    financial['medium'] = fuzz.trimf(financial.universe, [30, 50, 70])
    financial['high']   = fuzz.trimf(financial.universe, [60, 100, 100])

    experience['low']    = fuzz.trimf(experience.universe, [0, 0, 40])
    experience['medium'] = fuzz.trimf(experience.universe, [30, 50, 70])
    experience['high']   = fuzz.trimf(experience.universe, [60, 100, 100])

    credit_score['very_low']  = fuzz.trimf(credit_score.universe, [300, 300, 450])
    credit_score['low']       = fuzz.trimf(credit_score.universe, [400, 500, 600])
    credit_score['fair']      = fuzz.trimf(credit_score.universe, [550, 650, 720])
    credit_score['good']      = fuzz.trimf(credit_score.universe, [700, 780, 820])
    credit_score['excellent'] = fuzz.trimf(credit_score.universe, [800, 850, 850])

    rules2 = [
        ctrl.Rule(behaviour['low'],                                                 credit_score['very_low']),
        ctrl.Rule(financial['low'] & behaviour['medium'],                           credit_score['low']),
        ctrl.Rule(financial['low'] & behaviour['high'],                             credit_score['fair']),
        ctrl.Rule(behaviour['high'] & financial['high'] & experience['high'],       credit_score['excellent']),
        ctrl.Rule(behaviour['high'] & financial['high'] & experience['medium'],     credit_score['good']),
        ctrl.Rule(behaviour['high'] & financial['medium'] & experience['high'],     credit_score['good']),
        ctrl.Rule(behaviour['high'] & financial['medium'] & experience['medium'],   credit_score['good']),
        ctrl.Rule(behaviour['medium'] & financial['medium'] & experience['medium'], credit_score['fair']),
        ctrl.Rule(behaviour['medium'] & financial['high'],                          credit_score['good']),
        ctrl.Rule(behaviour['medium'] & experience['high'],                         credit_score['fair']),
        ctrl.Rule(experience['low'] & behaviour['high'],                            credit_score['fair']),
        ctrl.Rule(experience['low'] & behaviour['medium'],                          credit_score['low']),
        ctrl.Rule(behaviour['high'] & financial['low'],                             credit_score['fair']),
        ctrl.Rule(behaviour['medium'] & financial['low'],                           credit_score['low']),
        ctrl.Rule(behaviour['medium'] & financial['medium'] & experience['low'],    credit_score['low']),
    ]

    fis2_ctrl = ctrl.ControlSystem(rules2)
    fis2      = ctrl.ControlSystemSimulation(fis2_ctrl)

    return fis1, fis2


def get_score_band(score: float):
    if score >= 800: return "Excellent", "Very Low"
    if score >= 700: return "Good",      "Low"
    if score >= 600: return "Fair",      "Medium"
    if score >= 500: return "Poor",      "High"
    return "Very Poor", "Very High"


def run_fis(payment_history, credit_utilization, debt_to_income_ratio,
            monthly_income, existing_emi, credit_history_length, num_inquiries):

    fis1, fis2 = build_fis()

    fis1.input['payment_history'] = min(max(payment_history, 0), 100)
    fis1.input['utilization']     = min(max(credit_utilization, 0), 100)
    fis1.input['dti']             = min(max(debt_to_income_ratio, 0), 100)
    fis1.input['income']          = min(max(monthly_income, 0), 500000)
    fis1.input['emi']             = min(max(existing_emi, 0), 50000)
    fis1.input['credit_history']  = min(max(credit_history_length, 0), 20)
    fis1.input['inquiries']       = min(max(num_inquiries, 0), 10)
    fis1.compute()

    b = fis1.output['behaviour_score']
    f = fis1.output['financial_score']
    e = fis1.output['experience_score']

    fis2.input['behaviour']  = b
    fis2.input['financial']  = f
    fis2.input['experience'] = e
    fis2.compute()

    raw_score = fis2.output['credit_score']
    score_band, risk_level = get_score_band(raw_score)

    return {
        "fuzzy_credit_score": round(raw_score),
        "score_band": score_band,
        "risk_level": risk_level,
        "demographic_score": round(e, 2),
        "financial_score": round(f, 2),
        "asset_score": round(b, 2),
    }
