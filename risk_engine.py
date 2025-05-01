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
        # More responsive to credit score changes - steeper curve
        if credit_score >= 700:
            # Good credit scores get significantly lower base PD
            base_pd = 0.1 * (1 - ((credit_score - 700) / 150))
        elif credit_score >= 600:
            # Fair credit scores get moderate base PD
            base_pd = 0.3 * (1 - ((credit_score - 600) / 100))
        else:
            # Poor credit scores still have a chance
            base_pd = 0.5 * (1 - ((credit_score - 300) / 300))
        
        # Debt-to-income ratio (higher ratio = higher risk)
        monthly_income = income / 12
        monthly_debt = debt / 12
        debt_to_income = (monthly_debt + expenses) / monthly_income
        
        # More forgiving DTI curve with progressive thresholds
        if debt_to_income <= 0.3:
            # Low DTI is very good
            dti_factor = debt_to_income * 0.5
        elif debt_to_income <= 0.4:
            # Moderate DTI is acceptable
            dti_factor = 0.15 + ((debt_to_income - 0.3) * 1.0)
        else:
            # Higher DTI has diminishing penalties
            dti_factor = 0.25 + ((debt_to_income - 0.4) * 0.8)
        
        # Cap at a reasonable maximum
        dti_factor = min(dti_factor, 0.6)
        
        # Loan amount to income ratio (higher ratio = higher risk)
        loan_to_income = loan_amount / income
        
        # More balanced loan-to-income assessment
        if loan_to_income <= 0.5:
            # Small loans relative to income are low risk
            lti_factor = loan_to_income * 0.4
        elif loan_to_income <= 1.0:
            # Moderate loans are reasonable
            lti_factor = 0.2 + ((loan_to_income - 0.5) * 0.5)
        else:
            # Large loans have diminishing penalties
            lti_factor = 0.45 + ((loan_to_income - 1.0) * 0.3)
        
        # Cap at a reasonable maximum
        lti_factor = min(lti_factor, 0.6)
        
        # Weight factors and calculate final PD
        weighted_pd = (base_pd * 0.5) + (dti_factor * 0.3) + (lti_factor * 0.2)
        
        # Apply loan term adjustment (longer loans = higher risk but with diminishing effect)
        if loan_term <= 24:
            term_factor = loan_term / 48  # Short terms are low risk
        else:
            term_factor = 0.5 + ((loan_term - 24) / 72)  # Longer terms have diminishing risk increase
        
        term_factor = min(term_factor, 0.8)  # Cap term factor
        
        final_pd = weighted_pd * (1 + (term_factor * 0.15))
        
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
        # More responsive base LGD based on credit score tiers
        if credit_score >= 750:
            # Excellent credit indicates strong recovery potential
            base_lgd = 0.3
        elif credit_score >= 650:
            # Good credit indicates reasonable recovery potential
            base_lgd = 0.4
        elif credit_score >= 550:
            # Fair credit indicates moderate recovery challenges
            base_lgd = 0.5
        else:
            # Poor credit indicates significant recovery challenges
            base_lgd = 0.6
        
        # Adjust based on loan amount with tiered approach
        if loan_amount <= 25000:
            # Small loans - higher proportional recovery costs
            amount_factor = 0.1
        elif loan_amount <= 50000:
            # Medium loans - moderate recovery efficiency
            amount_factor = 0.08
        elif loan_amount <= 75000:
            # Larger loans - better recovery efficiency
            amount_factor = 0.05
        else:
            # Very large loans - best recovery efforts
            amount_factor = 0.03
        
        # Employment status impact (employed borrowers have better recovery prospects)
        if employment_status == 'full_time':
            employment_multiplier = 0.8  # Strong income stability
        elif employment_status == 'self_employed':
            employment_multiplier = 0.85  # Good but variable income
        elif employment_status == 'part_time':
            employment_multiplier = 0.9  # Moderate income stability
        elif employment_status == 'retired':
            employment_multiplier = 0.95  # Fixed income but limited growth
        else:  # Unemployed
            employment_multiplier = 1.0  # Higher recovery challenge
        
        # Calculate final LGD with more responsive formula
        lgd = (base_lgd + amount_factor) * employment_multiplier
        
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
        # More balanced PD component (less aggressive scaling for moderate PDs)
        if pd < 0.2:
            pd_component = pd * 7  # Low PD is rewarded significantly
        elif pd < 0.4:
            pd_component = 1.4 + ((pd - 0.2) * 9)  # Moderate PD scales moderately
        else:
            pd_component = 3.2 + ((pd - 0.4) * 13)  # High PD is penalized
            
        # More balanced LGD component (more granular scaling)
        if lgd < 0.3:
            lgd_component = lgd * 3  # Low LGD is favorable
        elif lgd < 0.5:
            lgd_component = 0.9 + ((lgd - 0.3) * 4)  # Moderate LGD
        else:
            lgd_component = 1.7 + ((lgd - 0.5) * 5)  # Higher LGD
        
        # Expected loss as percentage of loan amount with tiered evaluation
        el_percentage = min(expected_loss / loan_amount, 1)
        
        if el_percentage < 0.05:
            # Very low expected loss (< 5% of loan)
            el_component = el_percentage * 40  # Scales to max of 2
        elif el_percentage < 0.15:
            # Low expected loss (5-15% of loan)
            el_component = 2 + ((el_percentage - 0.05) * 50)  # Scales from 2 to 7
        else:
            # High expected loss (> 15% of loan)
            el_component = 7 + ((el_percentage - 0.15) * 20)  # Scales from 7 to 10
        
        # Weighted average with adjusted weights - PD has slightly less influence
        risk_rating = (pd_component * 0.4) + (lgd_component * 0.3) + (el_component * 0.3)
        
        # Convert to 1-10 scale and round to nearest integer
        # Slightly compress the rating to make approvals more likely
        scaled_rating = max(min(round(risk_rating), 10), 1)
        
        return scaled_rating
    
    @staticmethod
    def get_recommendation(risk_rating, pd, debt_to_income_ratio):
        """
        Provide loan recommendation based on risk metrics
        
        Returns:
        - recommendation: "Approve", "Review", or "Reject"
        - reasons: List of reasons for the recommendation
        """
        reasons = []
        
        # More lenient decision thresholds
        if risk_rating <= 4:  # Increased from 3 to 4
            recommendation = "Approve"
            
            if risk_rating <= 2:
                reasons.append("Excellent risk profile")
            else:
                reasons.append("Good risk profile")
                
        elif risk_rating <= 7:  # Same threshold but more lenient interpretation
            # Special handling for borderline cases
            if risk_rating <= 5 and pd < 0.25 and debt_to_income_ratio < 0.45:
                recommendation = "Approve"
                reasons.append("Acceptable risk profile with good factors")
                
                if pd > 0.2:
                    reasons.append("Consider slightly lower loan amount for better terms")
            else:
                recommendation = "Review"
                
                if pd > 0.25:  # Increased from 0.2 to 0.25
                    reasons.append("Moderate probability of default")
                
                if debt_to_income_ratio > 0.45:  # Increased from 0.4 to 0.45
                    reasons.append("Elevated debt-to-income ratio")
                    
                reasons.append("Risk factors require additional review")
        else:
            # Only truly high-risk applications are rejected
            if risk_rating >= 9:  # Only ratings of 9-10 are automatic rejects
                recommendation = "Reject"
                
                if pd > 0.4:  # Increased from 0.3 to 0.4
                    reasons.append("High probability of default")
                
                if debt_to_income_ratio > 0.55:  # Increased from 0.5 to 0.55
                    reasons.append("Excessive debt-to-income ratio")
                    
                reasons.append("Overall risk rating exceeds acceptable threshold")
            else:
                # Risk ratings of 8 go to review instead of reject
                recommendation = "Review"
                reasons.append("High risk factors requiring detailed evaluation")
                
                if pd > 0.35:
                    reasons.append("Elevated probability of default")
                    
                if debt_to_income_ratio > 0.5:
                    reasons.append("High debt-to-income ratio")
        
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
