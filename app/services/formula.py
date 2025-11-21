import math
from fastapi import HTTPException


class Bodyformula:
    @staticmethod
    def bmi(weight: float, height: float) -> dict:
        """
        Calculate BMI and return category message.
        Height in centimeters, weight in kilograms.
        """
        if weight <= 0 or height <= 0:
            return {"message": "Invalid height or weight"}

        height_m = height / 100  # Convert cm to meters
        bmi_value = round(weight / (height_m ** 2), 2)

        if 0 < bmi_value < 19:
            return {
                "message": "You are underweight in regard to BMI calculation.",
                "value": bmi_value,
            }
        elif 19 <= bmi_value <= 25:
            return {
                "message": "Your weight is normal in regard to BMI calculation.",
                "value": bmi_value,
            }
        elif bmi_value > 25:
            return {
                "message": "You are overweight in regard to BMI calculation.",
                "value": bmi_value,
            }
        else:
            return {"message": "Invalid height or weight"}

    @staticmethod
    def bodyfat(waist: float, neck: float, height: float, gender: str, hips: float = 0) -> float:
        """
        Calculate body fat percentage using U.S. Navy method.
        Waist, neck, height, hips are in centimeters.
        Hips required for females.
        Returns a float body fat percentage or raises an HTTPException.
        """
        gender = gender.lower()

        try:
            if gender == "male":
                if waist <= 0 or neck <= 0 or height <= 0:
                    raise ValueError("Invalid measurements for male.")
                result = (
                    86.010 * math.log10(waist - neck)
                    - 70.041 * math.log10(height)
                    + 36.76
                )
            elif gender == "female":
                if waist <= 0 or neck <= 0 or height <= 0 or hips <= 0:
                    raise ValueError("Invalid measurements for female.")
                result = (
                    163.205 * math.log10(waist + hips - neck)
                    - 97.684 * math.log10(height)
                    - 78.387
                )
            else:
                raise ValueError("Gender not supported.")

            if not 0 <= result <= 75:
                raise ValueError("Calculated body fat % is out of valid range.")

            return round(result, 2)

        except (ValueError, TypeError) as e:
            raise HTTPException(
                status_code=422,
                detail=str(e)
            )

    @staticmethod
    def bmr(weight_kg: float, height: float, age: int, gender: str) -> float:
        """
        Calculate Basal Metabolic Rate using Mifflin-St Jeor equation.
        """
        gender = gender.lower()
        if gender == "male":
            bmr = 10 * weight_kg + 6.25 * height - 5 * age + 5
        elif gender == "female":
            bmr = 10 * weight_kg + 6.25 * height - 5 * age - 161
        else:
            raise HTTPException(status_code=422, detail="Gender must be 'male' or 'female'")
        return round(bmr, 2)

    @staticmethod
    def tdee(bmr: float, activity_level: str) -> float:
        """
        Calculate Total Daily Energy Expenditure based on activity level.
        """
        activity_factors = {
            "sedentary": 1.2,
            "light": 1.375,
            "moderate": 1.55,
            "very_active": 1.725,
            "extra_active": 1.9,
        }

        factor = activity_factors.get(activity_level.lower())
        if factor is None:
            raise HTTPException(
                status_code=422,
                detail="Invalid activity level. Choose from: sedentary, light, moderate, very_active, extra_active."
            )
        return round(bmr * factor, 2)
