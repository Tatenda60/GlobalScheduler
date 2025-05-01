import numpy as np
import pandas as pd
from datetime import datetime

class CreditRiskEngine:
    """Engine for credit risk modeling and loan decision making"""
    
    @staticmethod
    def calculate_probability_of_default(credit_score, income, expenses, debt, loan_amount, loan_term):
        """
        Calculate Probability of Default (PD)
        
        PD is the likelihood that a borrower will default on a loan.
        Formula is a simplified model based on credit score, income-to-debt ratio,
        and loan amount relative to income.
        
        Returns a value between 0 and 1
        """
        # Base PD derived from credit score (higher score = lower PD)
        # Credit scores typically range from 300-850
        base_pd = 1 - (credit_score / 850)
        
        # Debt-to-income ratio (higher ratio = higher risk)
        monthly_income = income / 12
        monthly_debt = debt / 12
        debt_to_income = (monthly_debt + expenses) / monthly_income
        dti_factor = min(debt_to_income, 1)  # Cap at 1
        
        # Loan amount to income ratio (higher ratio = higher risk)
        loan_to_income = loan_amount / income
        lti_factor = min(loan_to_income, 1)  # Cap at 1
        
        # Weight factors and calculate final PD
        weighted_pd = (base_pd * 0.5) + (dti_factor * 0.3) + (lti_factor * 0.2)
        
        # Apply loan term adjustment (longer loans = higher risk)
        term_factor = min(loan_term / 60, 1)  # Assuming max term is 60 months
        
        final_pd = weighted_pd * (1 + (term_factor * 0.2))
        
        # Ensure PD is between 0 and 1
        return min(max(final_pd, 0), 1)
    
    @staticmethod
    def calculate_loss_given_default(loan_amount, credit_score, employment_status):
        """
        Calculate Loss Given Default (LGD)
        
        LGD is the amount of money a bank or lender loses when a borrower defaults,
        after taking into account recovery costs.
        
        Returns a value between 0 and 1
        """
        # Base LGD (higher amounts have higher recovery costs, proportionally lower recoveries)
        base_lgd = 0.5  # Starting with 50% loss
        
        # Adjust based on loan amount (larger loans may have better recovery efforts)
        amount_factor = min(loan_amount / 100000, 1)  # Cap at 1
        
        # Credit score impact (higher scores may indicate better assets/collateral)
        credit_factor = 1 - (credit_score / 850)
        
        # Employment status impact (employed borrowers may have better recovery)
        employment_multiplier = 1.0
        if employment_status in ['full_time', 'self_employed']:
            employment_multiplier = 0.8
        elif employment_status == 'part_time':
            employment_multiplier = 0.9
        else:  # Unemployed or retired
            employment_multiplier = 1.1
        
        # Calculate final LGD
        lgd = (base_lgd + (amount_factor * 0.1) + (credit_factor * 0.2)) * employment_multiplier
        
        # Ensure LGD is between 0 and 1
        return min(max(lgd, 0), 1)
    
    @staticmethod
    def calculate_exposure_at_default(loan_amount, loan_term):
        """
        Calculate Exposure at Default (EAD)
        
        EAD is the total value that a lender is exposed to when a borrower defaults.
        For simple term loans, this is typically the remaining principal.
        
        Returns the dollar amount exposed at estimated default time
        """
        # Simplified model: Assume defaults typically happen 1/3 through the loan term
        # Calculate remaining principal at that point
        default_point = loan_term / 3
        
        # Simple linear amortization for estimation
        percent_remaining = 1 - (default_point / loan_term)
        
        # EAD is the remaining principal at expected default time
        ead = loan_amount * max(percent_remaining, 0)
        
        return ead
    
    @staticmethod
    def calculate_expected_loss(pd, lgd, ead):
        """
        Calculate Expected Loss (EL)
        
        EL = PD * LGD * EAD
        
        Returns the dollar amount of expected loss
        """
        return pd * lgd * ead
    
    @staticmethod
    def calculate_risk_rating(pd, lgd, expected_loss, loan_amount):
        """
        Calculate a risk rating on a scale of 1-10
        
        1 = lowest risk, 10 = highest risk
        """
        # PD component (higher PD = higher risk rating)
        pd_component = pd * 10
        
        # LGD component (higher LGD = higher risk rating)
        lgd_component = lgd * 5
        
        # Expected loss as percentage of loan amount
        el_percentage = min(expected_loss / loan_amount, 1)
        el_component = el_percentage * 10
        
        # Weighted average for final rating
        risk_rating = (pd_component * 0.5) + (lgd_component * 0.2) + (el_component * 0.3)
        
        # Convert to 1-10 scale and round to nearest integer
        return max(min(round(risk_rating * 10), 10), 1)
    
    @staticmethod
    def get_recommendation(risk_rating, pd, debt_to_income_ratio):
        """
        Provide loan recommendation based on risk metrics
        
        Returns:
        - recommendation: "Approve", "Review", or "Reject"
        - reasons: List of reasons for the recommendation
        """
        reasons = []
        
        # Decision thresholds
        if risk_rating <= 3:
            recommendation = "Approve"
            reasons.append("Low risk profile")
        elif risk_rating <= 7:
            recommendation = "Review"
            
            if pd > 0.2:
                reasons.append("Moderate probability of default")
            
            if debt_to_income_ratio > 0.4:
                reasons.append("High debt-to-income ratio")
                
            reasons.append("Risk factors require manual review")
        else:
            recommendation = "Reject"
            
            if pd > 0.3:
                reasons.append("High probability of default")
            
            if debt_to_income_ratio > 0.5:
                reasons.append("Excessive debt-to-income ratio")
                
            if risk_rating > 8:
                reasons.append("Overall risk rating exceeds acceptable threshold")
        
        return recommendation, reasons
    
    @classmethod
    def assess_loan_application(cls, application_data):
        """
        Assess a loan application and return a complete risk assessment
        
        Parameters:
        - application_data: Dict containing loan application data
        
        Returns:
        - assessment: Dict containing all risk metrics and recommendation
        """
        # Extract application data
        loan_amount = application_data['loan_amount']
        loan_term = application_data['loan_term']
        credit_score = application_data['credit_score']
        annual_income = application_data['annual_income']
        monthly_expenses = application_data['monthly_expenses']
        existing_debt = application_data['existing_debt']
        employment_status = application_data['employment_status']
        
        # Calculate monthly income
        monthly_income = annual_income / 12
        
        # Calculate debt-to-income ratio
        debt_to_income_ratio = (existing_debt / 12 + monthly_expenses) / monthly_income
        
        # Calculate risk metrics
        pd = cls.calculate_probability_of_default(
            credit_score, annual_income, monthly_expenses, 
            existing_debt, loan_amount, loan_term
        )
        
        lgd = cls.calculate_loss_given_default(
            loan_amount, credit_score, employment_status
        )
        
        ead = cls.calculate_exposure_at_default(loan_amount, loan_term)
        
        expected_loss = cls.calculate_expected_loss(pd, lgd, ead)
        
        risk_rating = cls.calculate_risk_rating(pd, lgd, expected_loss, loan_amount)
        
        recommendation, reasons = cls.get_recommendation(
            risk_rating, pd, debt_to_income_ratio
        )
        
        # Prepare assessment result
        assessment = {
            'probability_of_default': pd,
            'loss_given_default': lgd,
            'exposure_at_default': ead,
            'expected_loss': expected_loss,
            'risk_rating': risk_rating,
            'recommendation': recommendation,
            'reasons': reasons,
            'timestamp': datetime.utcnow()
        }
        
        return assessment
    
    @staticmethod
    def validate_csv_format(file_path):
        """
        Validate if the uploaded CSV file has the required format
        
        Parameters:
        - file_path: Path to the CSV file
        
        Returns:
        - is_valid: Boolean indicating if the file is valid
        - error_message: Error message if the file is invalid, None otherwise
        """
        required_columns = [
            'loan_amount', 'loan_term', 'credit_score', 'annual_income',
            'monthly_expenses', 'existing_debt', 'employment_status'
        ]
        
        try:
            # Read the CSV file
            df = pd.read_csv(file_path)
            
            # Check if all required columns are present
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                return False, f"Missing required columns: {', '.join(missing_columns)}"
            
            # Check for any null values in required columns
            null_columns = [col for col in required_columns if df[col].isnull().any()]
            
            if null_columns:
                return False, f"Null values found in columns: {', '.join(null_columns)}"
            
            # Check for non-numeric values in numeric columns
            numeric_columns = [
                'loan_amount', 'loan_term', 'credit_score', 
                'annual_income', 'monthly_expenses', 'existing_debt'
            ]
            
            non_numeric_columns = []
            for col in numeric_columns:
                try:
                    pd.to_numeric(df[col])
                except:
                    non_numeric_columns.append(col)
            
            if non_numeric_columns:
                return False, f"Non-numeric values found in columns: {', '.join(non_numeric_columns)}"
            
            # Check for valid employment status values
            valid_statuses = ['full_time', 'part_time', 'self_employed', 'unemployed', 'retired']
            invalid_statuses = df[~df['employment_status'].isin(valid_statuses)]['employment_status'].unique()
            
            if len(invalid_statuses) > 0:
                return False, f"Invalid employment status values: {', '.join(invalid_statuses)}"
            
            return True, None
            
        except Exception as e:
            return False, f"Error reading CSV file: {str(e)}"
    
    @classmethod
    def process_csv_data(cls, file_path):
        """
        Process CSV data and return risk assessments for all applications
        
        Parameters:
        - file_path: Path to the CSV file
        
        Returns:
        - assessments: List of dicts containing risk assessments
        """
        # Validate the CSV file
        is_valid, error_message = cls.validate_csv_format(file_path)
        
        if not is_valid:
            raise ValueError(error_message)
        
        # Read the CSV file
        df = pd.read_csv(file_path)
        
        # Process each application
        assessments = []
        
        for _, row in df.iterrows():
            application_data = {
                'loan_amount': float(row['loan_amount']),
                'loan_term': int(row['loan_term']),
                'credit_score': int(row['credit_score']),
                'annual_income': float(row['annual_income']),
                'monthly_expenses': float(row['monthly_expenses']),
                'existing_debt': float(row['existing_debt']),
                'employment_status': row['employment_status']
            }
            
            assessment = cls.assess_loan_application(application_data)
            
            # Add the original application data to the assessment
            assessment['application_data'] = application_data
            
            assessments.append(assessment)
        
        return assessments
