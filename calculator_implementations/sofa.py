import json
import os 
import unit_converter_new
from rounding import round_number

def compute_sofa(input_parameters):

    sofa_score = 0

    pao2 = input_parameters["partial_pressure_oxygen"][0]
    fio2 = input_parameters["fio2"][0]

    mechanical_ventilation = input_parameters.get("mechanical_ventilation", False)
    cpap = input_parameters.get("cpap", False)
    platelet_count = input_parameters["platelet_count"]

    platelet_count = unit_converter_new.conversions(input_parameters.get["platelet_count"][0], input_parameters.get["platelet_count"][1], "mg/dL", "584.66", None)

    gcs = input_parameters.get("gcs", 15) 
    bilirubin = unit_converter_new.conversions(input_parameters['bilirubin'][0], input_parameters['bilirubin'][1], "µmol/L", "584.66", None)
    sys_bp = input_parameters["sys_bp"][0]
    dia_bp = input_parameters["dia_bp"][0]

    dopamine = input_parameters.get("dopamine", [0])
    dobutamine = input_parameters.get("dobutamine", [0])
    epinephrine = input_parameters.get("epinephrine", [0])
    norepinephrine = input_parameters.get("norepinephrine", [0])

    ratio = pao2/fio2

    if 300 <= ratio < 400:
        sofa_score += 1
    elif 200 <= ratio < 300:
        sofa_score += 2
    elif ratio <= 199 and (not mechanical_ventilation and not cpap):
        sofa_score += 2
    elif 100 <= ratio < 199 and (mechanical_ventilation or cpap):
        sofa_score += 3
    elif ratio < 100 and mechanical_ventilation:
        sofa_score += 4

    if sys_bp + dia_bp < 70:
        sofa_score += 1
    elif dopamine[0] <= 5 or dobutamine[0]:
        sofa_score += 2
    elif (dopamine[0] > 5 or epinephrine[0] <= 0.1 or norepinephrine[0] <= 0.1):
            sofa_score += 3
    elif (dopamine[0] > 15 or epinephrine[0] > 0.1 or norepinephrine[0] > 0.1):
        sofa_score += 4


    if gcs < 6:
        sofa_score += 4
    elif 6 <= gcs <= 9:
        sofa_score += 3
    elif 10 <= gcs <= 12:
        sofa_score += 2
    elif 13 <= gcs <= 14:
        sofa_score += 1


    if 1.2 <= bilirubin < 2.0:
        sofa_score += 1
    elif 2.0 <= bilirubin < 6.0:
        sofa_score += 2
    elif 6.0 <= bilirubin < 12.0:
        sofa_score += 3
    elif bilirubin >= 12.0:
        sofa_score += 4


    if 100 <= platelet_count < 150:
        sofa_score += 1
    elif 50 <= platelet_count < 100:
        sofa_score += 2
    elif 20 <= platelet_count < 50:
        sofa_score += 3
    elif platelet_count < 20:
        sofa_score += 4


    if 'creatinine' not in input_parameters:
        urine_output = input_parameters["urine_output"][0]

        if urine_output < 500:
            sofa_score += 3
        elif urine_output < 200:
            sofa_score += 4

    elif 'urine_output' not in input_parameters:
        creatinine = unit_converter_new.conversions(input_parameters['creatinine'][0], input_parameters['creatinine'][1], "mg/dL", 113.12, None)

        if 1.2 <= creatinine < 2.0:
            sofa_score += 1
        elif 2.0 <= creatinine < 3.5:
            sofa_score += 2
        elif 3.5 <= creatinine < 5.0:
            sofa_score += 3
        elif creatinine >= 5.0:
            sofa_score += 4

    return sofa_score



def compute_sofa_explanation(input_parameters):

    explanation = "The patient's current SOFA score is 0.\n"

    sofa_score = 0

    pao2 = input_parameters["partial_pressure_oxygen"][0]
    fio2 = input_parameters["fio2"][0]

    dopamine = input_parameters.get("dopamine", [0])
    dobutamine = input_parameters.get("dobutamine", [0])
    epinephrine = input_parameters.get("epinephrine", [0])
    norepinephrine = input_parameters.get("norepinephrine", [0])

    explanation += f"The patient's partial pressure of oxygen is {pao2} mm Hg and FiO₂ percentage is {fio2} %. "
    ratio = round_number(pao2/fio2)
    explanation += f"This means that the patient's partial pressure of oxygen to FiO₂ ratio is {ratio}. "

    if "mechanical_ventilation" not in input_parameters:
        explanation += "Whether the patient is on mechanical ventillation is not reported and so we assume this to be false. "
        input_parameters["mechanical_ventilation"] = False
    elif input_parameters["mechanical_ventilation"]:
        explanation += "The patient is reported to be on mechanical ventillation. "
    else:
        explanation += "The patient is reported to not be on mechanical ventillation. "
        input_parameters["mechanical_ventilation"] = False

    if "cpap" not in input_parameters:
        explanation += "Whether the patient is on continuous positive airway pressure is not reported and so we assume this to be false. "
        input_parameters["cpap"] = False
    elif input_parameters["cpap"]:
        explanation += "The patient is reported to be using continuous positive airway pressure. "
    else:
        explanation += "The patient is reported to not be using continuous positive airway pressure. "


    if 300 <= ratio < 400:
        explanation += f"Because the patient's partial pressure of oxygen to FiO₂ ratio is between 300 and 400, we increase the score by one point, makeing the current total {sofa_score} + 1 = {sofa_score + 1}.\n"
        sofa_score += 1
    elif 200 <= ratio < 300:
        explanation += f"Because the patient's partial pressure of oxygen to FiO₂ ratio is between 200 and 300, we increase the score by two points, makeing the current total {sofa_score} + 2 = {sofa_score + 2}.\n"
        sofa_score += 2
    elif ratio <= 199 and (not input_parameters["mechanical_ventilation"] and not input_parameters["cpap"]):
        explanation += f"Because the patient's partial pressure of oxygen to FiO₂ ratio is between 200 and 300, the patient is not on mechanical ventillation and is not using continious positive airway pressure, we increase the score by two points, makeing the current total {sofa_score} + 2 = {sofa_score + 2}.\n"
        sofa_score += 2
    elif 100 <= ratio < 199 and (input_parameters["mechanical_ventilation"] or input_parameters["cpap"] ):
        explanation += f"Because the patient's partial pressure of oxygen to FiO₂ ratio is between 100 to 199, and the patient is using at least one of (i) mechanical ventillation or (ii) continious positive airway pressure, we increase the score by three points, makeing the current total {sofa_score} + 3 = {sofa_score + 3}.\n"
        sofa_score += 3
    elif ratio < 100 and input_parameters["mechanical_ventilation"]:
        explanation += f"Because the patient's partial pressure of oxygen to FiO₂ ratio is less than 100, and the patient is using at least one of (i) mechanical ventillation or (ii) continious positive airway pressure, we increase the score by four points, makeing the current total {sofa_score} + 4 = {sofa_score + 4}.\n"
        sofa_score += 4

    if  'sys_bp' in input_parameters and 'dia_bp' in input_parameters and 1/3 * input_parameters['sys_bp'][0] + 2/3 * input_parameters['dia_bp'][0] < 70 and (not dobutamine[0] and not epinephrine[0] and not norepinephrine[0]):
        sys_bp = input_parameters['sys_bp'][0]
        dia_bp = input_parameters['dia_bp'][0]
        map = round_number(1/3 * sys_bp + 2/3 * dia_bp)
        explanation = f"The patient's systolic blood pressure is {sys_bp} mm Hg and the patient's diastolic blood pressure is {dia_bp} mm Hg, making the patient's mean arterial blood pressure {map} mm Hg. "
        explanation += f"For one point to be given, the patient's mean arterial pressure must be less than 70 mm Hg, making the current total {sofa_score} + 1 = {sofa_score + 1}.\n"
        sofa_score += 1
    elif dopamine[0] <= 5 or dobutamine[0]:
        explanation += f"For two points to be given, the patient must be taking less than or equal to 5 micrograms/kg/min or any amount of dobutamine. Because at least one of these cases is true for the patient, we increment the score by two points, making the current total {sofa_score} + 2 = {sofa_score + 2}.\n"
        sofa_score += 2
    elif (dopamine[0] > 5 or epinephrine[0] <= 0.1 or norepinephrine[0] <= 0.1):
        explanation += f"For three points to be given, the patient must be taking more than 5 micrograms/kg/min, less than or equal to 0.1 micrograms/kg/min of epinephrine, or less than or equal to 0.1 micrograms/kg/min of norepinephrine. Because at least one of these cases is true for the patient, we increment the score by three points, making the current total {sofa_score} + 3 = {sofa_score + 3}.\n"
        sofa_score += 3
    elif (dopamine[0] > 15 or epinephrine[0] > 0.1 or norepinephrine[0] > 0.1):
        explanation += f"For four points to be given, the patient must be taking more than 15 micrograms/kg/min, more than 0.1 micrograms/kg/min of epinephrine, or more than 0.1 micrograms/kg/min of norepinephrine. Because at least one of these cases is true for the patient, we increment the score by four points, making the current total {sofa_score} + 4 = {sofa_score + 4}.\n"
        sofa_score += 4

    if 'gcs' not in input_parameters:
        gcs = 15
        explanation += f"The patient's glasgow coma score is {gcs}. "
    else:
        gcs = input_parameters["gcs"]
        explanation += f"The patient's glasgow coma score is not reported so we take it to be 15. "

    if gcs < 6:
        explanation += f"Because the patient's glasgow coma score is less than 6, we add 4 points to the score, making the current score {sofa_score} + 4 = {sofa_score + 4}.\n "
        sofa_score += 4
    elif 6 <= gcs <= 9:
        explanation += f"Because the patient's glasgow coma score is between 6 and 9, we add 3 points to the score, making the current score {sofa_score} + 3 = {sofa_score + 3}.\n "
        sofa_score += 3
    elif 10 <= gcs <= 12:
        explanation += f"Because the patient's glasgow coma score is between 10 and 12, we add 2 points to the score, making the current score {sofa_score} + 2 = {sofa_score + 2}.\n "
        sofa_score += 2
    elif 13 <= gcs <= 14:
        explanation += f"Because the patient's glasgow coma score is between 13 and 14, we add 1 point to the score, making the current score {sofa_score} + 1 = {sofa_score + 1}.\n "
        sofa_score += 1
    else:
        explanation += f"Because the patient's glasgow coma score is 15, we add 0 points to the score, keeping the score at {sofa_score}.\n "

    bilirubin_exp, bilirubin = unit_converter_new.conversion_explanation(input_parameters['bilirubin'][0], 'bilirubin', 584.66, None, input_parameters['bilirubin'][1], "mg/dL")
    explanation += bilirubin_exp

    if bilirubin < 1.2:
        explanation += f"Because the patient's bilirubin concentration is less than 1.2 mg/dL, we add 0 points to the score, keeping the score at {sofa_score}.\n "
    if 1.2 <= bilirubin < 2.0:
        explanation += f"Because the patient's bilirubin concentration is at least 1.2 mg/dL but less than 2.0 mg/dL, we increment the score by one point, make the current score {sofa_score} + 1 = {sofa_score + 1}.\n"
        sofa_score += 1
    elif 2.0 <= bilirubin < 6.0:
        explanation += f"Because the patient's bilirubin concentration is at least 2.0 mg/dL but less than 6.0 mg/dL, we increment the score by two points, make the current score {sofa_score} + 2 = {sofa_score + 2}.\n"
        sofa_score += 2
    elif 6.0 <= bilirubin < 12.0:
        explanation += f"Because the patient's bilirubin concentration is at least 6.0 mg/dL but less than 12.0 mg/dL, we increment the score by three points, make the current score {sofa_score} + 3 = {sofa_score + 3}.\n"
        sofa_score += 3
    elif bilirubin >= 12.0:
        explanation += f"Because the patient's bilirubin concentration is at least 12.0 mg/dL, we increment the score by four points, make the current score {sofa_score} + 4 = {sofa_score + 4}.\n"
        sofa_score += 4

    platelet_count_exp, platelet_count = unit_converter_new.convert_to_units_per_liter_explanation(input_parameters["platelet_count"][0],input_parameters["platelet_count"][1], "platelet", "µL")
    explanation += platelet_count_exp


    if platelet_count >= 150000:
        explanation += f"Because the patient's platelet count is at least 150*10³/µL, we do not any points to the score, keeping the current score at {sofa_score}.\n"
    if 100000 <= platelet_count < 150000:
        explanation += f"Because the patient's platelet count is between 100*10³/µL but less than 150*10³/µL, we increment the score by one point, making the current score {sofa_score} + 1 = {sofa_score + 1}.\n"
        sofa_score += 1
    elif 50000 <= platelet_count < 100000:
        explanation += f"Because the patient's platelet count is between 50*10³/µL but less than 100*10³/µL, we increment the score by two points, making the current score {sofa_score} + 2 = {sofa_score + 2}.\n"
        sofa_score += 2
    elif 20000 <= platelet_count < 50000:
        explanation += f"Because the patient's platelet count is between 20*10³/µL but less than 50*10³/µL, we increment the score by three points, making the current score {sofa_score} + 3 = {sofa_score + 3}.\n"
        sofa_score += 3
    elif platelet_count < 20000:
        explanation += f"Because the patient's platelet count is less than 20*10³/µL, we increment the score by four points, making the current score {sofa_score} + 4 = {sofa_score + 4}.\n"
        sofa_score += 4


    if 'creatinine' not in input_parameters:
        urine_output = input_parameters["urine_output"][0]

        explanation += f"The patients urine output is {urine_output} mL/day. "

        if urine_output < 500:
            explanation += f"Because the patient's urine output is less than 500 mL/day, we increment the score by three points, making the current total {sofa_score} + 3 = {sofa_score + 3}.\n"
            sofa_score += 3
        elif urine_output < 200:
            explanation += f"Because the patient's urine output is less than 200 mL/day, we increment the score by four points, making the current total {sofa_score} + 4 = {sofa_score + 4}.\n"
            sofa_score += 4

    elif 'urine_output' not in input_parameters:
        creatinine_exp, creatinine = unit_converter_new.conversion_explanation(input_parameters['creatinine'][0], "creatinine", 113.12 , None, input_parameters['creatinine'][1], "mg/dL")

        explanation += creatinine_exp

        if 1.2 <= creatinine < 2.0:
            explanation += f"Because the patient's creatinine concentration is at least 1.2 mg/dL but less than 2.0 mg/dL, we increment the score by one point, making the current total {sofa_score} + 1 = {sofa_score + 1}.\n"
            sofa_score += 1
        elif 2.0 <= creatinine < 3.5:
            explanation += f"Because the patient's creatinine concentration is at least 2.0 mg/dL but less than 3.5 mg/dL, we increment the score by two points, making the current total {sofa_score} + 2 = {sofa_score + 2}.\n"
            sofa_score += 2
        elif 3.5 <= creatinine < 5.0:
            explanation += f"Because the patient's creatinine concentration is at least 3.5 mg/dL but less than 5.0 mg/dL, we increment the score by three points, making the current total {sofa_score} + 3 = {sofa_score + 3}.\n"
            sofa_score += 3
        elif creatinine >= 5.0:
            explanation += f"Because the patient's creatinine concentration is greater than 5.0 mg/dL, we increment the score by four points, making the current total {sofa_score} + 4 = {sofa_score + 4}.\n"
            sofa_score += 4

    explanation += f"Hence, the patient's SOFA score is {sofa_score} points.\n"

    return {"Explanation": explanation, "Answer": sofa_score}


