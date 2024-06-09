import json 
import os
import math 
import unit_converter_new
from rounding import round_number

def compute_meldna(input_variables):

    creatinine = input_variables["creatinine"]
    creatinine = unit_converter_new.conversions(creatinine[0], creatinine[1], "mg/dL", 113.12, None)

    dialysis_twice = input_variables.get("dialysis_twice", False)
    cvvhd_present = input_variables.get("cvvhd", False)


    if creatinine < 1.0:
        creatinine = 1.0
    elif creatinine > 4.0:
        creatinine = 4.0
    elif dialysis_twice or cvvhd_present:
        creatinine = 4.0


    bilirubin = input_variables["bilirubin"]
    bilirubin = unit_converter_new.conversions(bilirubin[0], bilirubin[1], "mg/dL", None, None)

    if bilirubin < 1.0:
        bilirubin = 1.0

    sodium = input_variables["sodium"]
    sodium = unit_converter_new.conversions(sodium[0], sodium[1], "mEq/L", 22.99, 1)

    if sodium < 125:
        sodium = 125
    elif sodium > 137:
        sodium = 137


    inr = input_variables["inr"]

    if inr < 1.0:
        inr = 1.0

    meld_1 = 0.957 * math.log(creatinine) + 0.378 * math.log(bilirubin) + 1.120 * math.log(inr) + 0.643
    meld_1 = round(meld_1, 1) * 10

    if meld_1 > 11:
        
        meld = meld_1 + 1.32 * (137 - sodium) - (0.033 * meld_1 * (137 - sodium))
        meld = min(40, meld)
        return round(meld)

    meld = min(meld_1, 40)

    return round(meld)

def compute_meldna_explanation(input_variables):
    
    meldna = 0

    explanation = "The formula for computing the MELD Na is to first apply the following equation: MELD(i) = 0.957 x ln(Cr) + 0.378 x ln(bilirubin) + 1.120 x ln(INR) + 0.643.\n"
    explanation += "If the MELD(i) is greater than 11 after rounding to the nearest tenth and multiplying the MELD(i) by 10, we apply the following equation: MELD = MELD(i) + 1.32 x (137 - Na) -  [ 0.033 x MELD(i) x (137 - Na)]. The MELD Na score is capped at 40. "
    explanation += "The concentration of Na is mEq/L, the concentration of bilirubin is mg/dL, and the concentration of creatinine is mg/dL.\n"


    creatinine_exp, creatinine = unit_converter_new.conversion_explanation(input_variables["creatinine"][0], "creatinine", 113.12, None, input_variables["creatinine"][1], "mg/dL")
    
    explanation += creatinine_exp + "\n"

    if "dialysis_twice" not in input_variables:
        explanation += "Whether the patient has went through dialysis at least twice in the past week is not mentioned, and so we assume this to be false.\n"
        input_variables["dialysis_twice"] = False
    elif input_variables["dialysis_twice"]:
        explanation += "The patient is reported to have went through dialysis at least twice in the past week.\n"
    else:
        explanation += "The patient has not went through dialysis at least twice in the past week.\n"

    if "cvvhd" not in input_variables:
        explanation += "Whether the patient has went through continuous veno-venous hemodialysis in the past 24 hours is not mentioned, and so we assume this to be false.\n"
        input_variables["cvvhd"] = False
    elif input_variables["cvvhd"]:
        explanation += "The patient is reported to have went through continuous veno-venous hemodialysis in the past 24 hours.\n"
    else:
        explanation += "The patient is reported to not have done dialysis at least twice in the past week.\n"


    if creatinine < 1.0:
        explanation += "The patient's creatinine concentration is less than 1.0 mg/dL, and so we set the creatinine concentration to 1.0 mg/dL.\n"
        creatinine = 1.0
    elif creatinine > 4.0:
        explanation += "The creatinine concentration is greater than 4.0 mg/dL, and so we set the creatinine concentration to 4.0 mg/dL.\n"
        creatinine = 4.0
    elif input_variables["dialysis_twice"] or input_variables["cvvhd"]:
        explanation += "Because the patient has went through at least one of (i) dialysis two or more times in the past 7 days or (ii) continuous veno-venous hemodialysis in the past 24 hours, we set the creatinine concentration to 4.0 mg/dL.\n"
        creatinine = 4.0

    bilirubin_exp, bilirubin = unit_converter_new.conversion_explanation(input_variables["bilirubin"][0], "bilirubin", None, None, input_variables["bilirubin"][1], "mg/dL")
    
    explanation += bilirubin_exp 

    if bilirubin < 1.0:
        explanation += "The patient's bilirubin concentration is less than 1.0 mg/dL, and so we set the bilirubin concentration to 1.0 mg/dL.\n"
        bilirubin = 1.0
    else:
        explanation += "\n"
    
    inr = input_variables["inr"]

    explanation += f"The patient's INR is {inr}. "

    if inr < 1.0:
        explanation += "The patient's INR is less than 1.0, and so we set the INR to 1.0.\n"
        inr = 1.0
    else:
        explanation += "\n"

    sodium_exp, sodium = unit_converter_new.conversion_explanation(input_variables["sodium"][0], "sodium", 22.99, 1, input_variables["sodium"][1], "mEq/L")

    explanation += sodium_exp

    if sodium < 125:
        explanation += "The sodium concentration is less than 125 mEq/L, and so we set the sodium concentration to 125 mEq/L.\n"
        sodium = 125
    elif sodium > 137:
        explanation += "The sodium concentration is greater than 137 mEq/L, and so we set the sodium concentration to 137 mEq/L.\n"
        sodium = 137
    else:
        explanation += "\n"

    meld_i = 0.957 * math.log(creatinine) + 0.378 * math.log(bilirubin) + 1.120 * math.log(inr) + 0.643
    meld_i_rounded = round(meld_i)
    meld_10 = round(meld_i_rounded * 10)

    explanation += f"Applying the first equation gives us 0.957 x ln({creatinine}) + 0.378 x ln({bilirubin}) + 1.120 x ln({inr}) + 0.643 = {meld_i}. "
    explanation += f"Rounding to the nearest tenth makes the MELD (i) score {meld_i_rounded}. We then multiply by 10, making the MELD(i) score {meld_10}.\n"

    meld = round(meld_10 + 1.32 * (137 - sodium) - (0.033 * meld_10 * (137 - sodium)))

    if meld_10 > 11:
        explanation += f"Because the MELD (i) score is greater than 11, we then apply the second equation, giving us {meld_10} + 1.32 x (137 - {sodium}) -  [0.033 x {meld_i} x (137 - {sodium})] = {meld}.\n"
        
        if meld > 40:
            meldna = 40
            explanation += "The maximum the MELD Na score can be is 40, and so the patient's MELD score is 40."
        else:
            meldna = meld
            explanation += f"The MELD Na score is less than 40, and so we keep the score as it is. The patient's MELDNa score, rounded to the nearest integer, is {round(meldna)} points.\n"

    else:
        meldna = meld_10
        explanation += f"The patient's MELD (i) score is less than 11, and so we do not apply the second equation, making the patient's MELD Na score, {round(meldna)} points.\n"

    return {"Explanation": explanation, "Answer": round(meldna),  "Calculator Answer": compute_meldna(input_variables)}


'''
test_outputs = [{"sodium": [130, "mmol/L"],
                 "creatinine": [4.0, "mg/dL"],
                 "bilirubin": [1.9, "mg/dL"],
                 "inr": [2]
                 }, 
                 
                {"sodium": [130, "mmol/L"],
                 "creatinine": [1.0, "mg/dL"],
                 "bilirubin": [1.0, "mg/dL"],
                 "inr": [1.0], 
                 "dialysis_twice": True},

                 {"sodium": [120, "mmol/L"],
                 "creatinine": [0.9, "mg/dL"],
                 "bilirubin": [0.9, "mg/dL"],
                 "inr": [0.9], 
                 "dialysis_twice": False},
                 
                 ]

outputs = {}
explanations = ""
for i, test_case in enumerate(test_outputs):
    outputs[i] =  compute_meldna_explanation(test_case)
    explanations += "Explanation:\n"
    explanations += outputs[i]["Explanation"]
    explanations += "\n"


file_name = "explanations/meldna_score.json"
os.makedirs(os.path.dirname(file_name), exist_ok=True)

with open(file_name, 'w') as file:
    json.dump(outputs, file, indent=4)



file_name = "explanations/meldna_score.txt"
os.makedirs(os.path.dirname(file_name), exist_ok=True)

with open(file_name, 'w') as file:
    file.write(explanations)

'''