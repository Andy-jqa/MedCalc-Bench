import os
import json 
import age_conversion
import unit_converter_new

def curb_65(input_parameters):

    curb_65_score = 0

    confusion = input_parameters.get("confusion", False)
    bun = unit_converter_new.conversions(input_parameters["bun"][0], input_parameters["bun"][1], "mg/dL", 28.02, None)
    respiratory_rate = input_parameters["respiratory_rate"][0]
    sys_bp = input_parameters["sys_bp"][0]
    dia_bp = input_parameters["dia_bp"][0]
    age = age_conversion.age_conversion(input_parameters["age"])

    if confusion:
        curb_65_score += 1
    if bun > 19:
        curb_65_score += 1
    if respiratory_rate >= 30:
        curb_65_score += 1
    if sys_bp < 90 or dia_bp <= 60:
        curb_65_score += 1
    if age >= 65:
        curb_65_score += 1

    return curb_65_score

def curb_65_explanation(input_parameters):

    curb_65_score = 0
    explanation = "The Curb-65 score is current at 0 points.\n"

    bun_exp, bun = unit_converter_new.conversion_explanation(input_parameters["bun"][0], "BUN", 28.02, None, input_parameters["bun"][1], "mg/dL")
    
    respiratory_rate = int(input_parameters["respiratory_rate"][0])
    sys_bp = int(input_parameters["sys_bp"][0])
    dia_bp = int(input_parameters["dia_bp"][0])
    age_exp, age = age_conversion.age_conversion_explanation(input_parameters["age"])

    explanation += age_exp

    if age >= 65:
        explanation +=f"The patient's age is greater than or equal to 65 years, and so we add 1 point to the score, making the current total {curb_65_score} + 1 = {curb_65_score + 1}.\n"
        curb_65_score += 1
    else:
        explanation +=f"The patient's age is less than 65 years, and so we add 0 points to the score, keeping the current total at {curb_65_score}.\n"


    if 'confusion' not in input_parameters:
        explanation += f"Whether the patient has confusion is not reported in the note. Hence, we assume this to be false, and so 0 points are added to the score, making the current total {curb_65_score}.\n"
    elif input_parameters["confusion"]:
        explanation += f"Because the patient has confusion, 1 point is added to score making the current total {curb_65_score} + 1 = {curb_65_score + 1}.\n"
        curb_65_score += 1
    else:
        explanation += f"Because the patient does not have confusion, 0 points are added to the score, keeping the score at {curb_65_score}.\n"

    explanation += bun_exp

    if bun > 19:
        explanation += f"The patient's BUN concentration is greater than 19 mg/dL and so we add 1 point to score making the current total {curb_65_score} + 1 = {curb_65_score + 1}.\n"
        curb_65_score += 1
    else:
        explanation += f"The patient's BUN concentration is less than or equal to 19 mg/dL and so 0 points are added to score, keeping the current total at {curb_65_score}.\n"

    explanation += f"The patient's respiratory rate is {respiratory_rate} breaths per minute. "

    if respiratory_rate >= 30:
        explanation += f"Because the respiratory rate is greater than 30 breaths per minute, 1 point is added to the score, making the current total {curb_65_score} + 1 = {curb_65_score + 1}.\n"
        curb_65_score += 1
    else:
        explanation += f"Because the respiratory rate is greater than 30 breaths per minute, 0 points are added to the score, keeping the current total at {curb_65_score}.\n"

    explanation += f"The patient's systiolic blood pressure is {sys_bp} mm Hg. The patient's diastolic blood pressure is {dia_bp} mm Hg. "

    if sys_bp < 90 or dia_bp <= 60:
        explanation += f"For a point a point to be added, the systiolic blood pressure must be less than 90 mm Hg or the diastolic blood pressure must be less than or equal to 60 mm Hg. Because at least one of these statements is true, 1 point is added to score, making the current total {curb_65_score} + 1 = {curb_65_score + 1}.\n"
        curb_65_score += 1
    else:
        explanation += f"For a point a point to be added, the systiolic blood pressure must be less than 90 mm Hg or the diastolic blood pressure must be less than or equal to 60 mm Hg. Because neither of these statements are true, 0 points are added to score, keeping the current total to {curb_65_score}.\n"

    explanation += f"The patient's Curb-65 score is {curb_65_score}.\n"

    return {"Explanation": explanation, "Answer": curb_65_score, "Calculator Answer": curb_65(input_parameters)}


test_outputs = [{"confusion": True, "bun": [8, "mmol/L"], "respiratory_rate": [56, "breaths per minute"], "sys_bp": [85, "mm Hg"], "dia_bp": [55, "mm Hg"], "age": [66, "years"]}, 
               {"confusion": False, "bun": [6, "mmol/L"], "respiratory_rate": [29, "breaths per minute"], "sys_bp": [91, "mm Hg"], "dia_bp": [61, "mm Hg"], "age": [63, "years"]}, 
              ]

outputs = {}
explanations = ""
for i, test_case in enumerate(test_outputs):
    outputs[i] = curb_65_explanation(test_case)
    explanations += "Explanation:\n"
    explanations += outputs[i]["Explanation"]
    explanations += "\n"

'''
file_name = "explanations/bsa.json"
os.makedirs(os.path.dirname(file_name), exist_ok=True)

with open(file_name, 'w') as file:
    json.dump(outputs, file, indent=4)
'''


file_name = "explanations/curb-65.txt"
os.makedirs(os.path.dirname(file_name), exist_ok=True)

with open(file_name, 'w') as file:
    file.write(explanations)
