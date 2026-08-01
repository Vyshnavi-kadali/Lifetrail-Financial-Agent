import logging

# Set up logging to save interactions to a file for Phase 2
logging.basicConfig(
    filename='lifetrail_baseline.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

class LifeTrailBaseline:
    def __init__(self):
        # 2026 Inflation Assumptions from Phase 1.docx
        self.rates = {"gold": 0.18, "education": 0.12, "lifestyle": 0.08}

    def calculate_savings(self, goal_type, current_cost, years):
        """Standard math for future projections."""
        rate = self.rates.get(goal_type.lower(), 0.08)
        future_cost = current_cost * ((1 + rate) ** years)
        monthly_savings = future_cost / (years * 12)
        return round(future_cost, 2), round(monthly_savings, 2), int(rate * 100)

    def calculate_new_regime_tax(self, taxable_income):
        """Precise 2026 New Regime Slab Logic with 12L Rebate."""
        if taxable_income <= 1200000:
            return 0
        
        tax = 0
        if taxable_income > 400000: tax += min(taxable_income - 400000, 400000) * 0.05
        if taxable_income > 800000: tax += min(taxable_income - 800000, 400000) * 0.10
        if taxable_income > 1200000: tax += min(taxable_income - 1200000, 400000) * 0.15
        if taxable_income > 1600000: tax += min(taxable_income - 1600000, 400000) * 0.20
        if taxable_income > 2000000: tax += min(taxable_income - 2000000, 400000) * 0.25
        if taxable_income > 2400000: tax += (taxable_income - 2400000) * 0.30
        return tax

    def calculate_old_regime_tax(self, taxable_income):
        """Old Regime Slab Logic with 5L Rebate limit."""
        if taxable_income <= 500000:
            return 0
            
        tax = 0
        if taxable_income > 250000: tax += min(taxable_income - 250000, 250000) * 0.05
        if taxable_income > 500000: tax += min(taxable_income - 500000, 500000) * 0.20
        if taxable_income > 1000000: tax += (taxable_income - 1000000) * 0.30
        return tax

    def run_tax_module(self):
        """Calculates tax based on user-selected regime and salary."""
        print("\n--- 2026 Comparative Tax Calculator ---")
        salary_str = input("Please enter your annual salary (e.g., 1500000): ")
        
        try:
            salary = float(salary_str)
            print("\nSelect Tax Regime:")
            print("1. New Tax Regime (Default, ₹75k Standard Deduction)")
            print("2. Old Tax Regime (₹50k Standard Deduction)")
            regime_choice = input("Selection (1/2): ").strip()

            if regime_choice == "1":
                regime_name = "New Regime"
                sd = 75000
                taxable = max(0, salary - sd)
                base_tax = self.calculate_new_regime_tax(taxable)
            else:
                regime_name = "Old Regime"
                sd = 50000
                taxable = max(0, salary - sd)
                base_tax = self.calculate_old_regime_tax(taxable)

            # Apply 4% Health & Education Cess
            final_tax = round(base_tax * 1.04, 2)
            salary_after_tax = salary - final_tax

            print(f"\n[RESULTS - {regime_name.upper()}]")
            print(f"Salary Provided: ₹{salary:,.2f}")
            print(f"Standard Deduction: ₹{sd:,.2f}")
            print(f"Taxable Income: ₹{taxable:,.2f}")
            print(f"Projected 2026 Tax (incl. Cess): ₹{final_tax:,.2f}")
            print(f"Take-home Pay: ₹{salary_after_tax:,.2f}")

            # LOGGING
            logging.info(f"TAX CALC: {regime_name} | Salary={salary} | Tax={final_tax}")

        except ValueError:
            print("Error: Please enter numbers only for salary.")

    def run_goal_module(self):
        """Calculates goal savings based on fresh user input."""
        print("\n--- 2026 Goal Planner ---")
        print("Available Categories: Gold (18%), Education (12%), Lifestyle (8%)")
        
        try:
            g_type = input("Enter Goal Category: ").strip().lower()
            cost = float(input("Enter Current Cost (₹): "))
            years = int(input("Enter Timeline (Years): "))
            
            future_cost, monthly, rate = self.calculate_savings(g_type, cost, years)
            
            print(f"\n[RESULTS]")
            print(f"Category: {g_type.capitalize()} ({rate}% Inflation)")
            print(f"Cost in {years} years: ₹{future_cost:,.2f}")
            print(f"Monthly Savings Needed: ₹{monthly:,.2f}")

            # LOGGING
            logging.info(f"GOAL CALC: Category={g_type} | FutureCost={future_cost} | Monthly={monthly}")

        except ValueError:
            print("Error: Invalid numeric input. Please try again.")

# --- MAIN INTERFACE ---
def start_chatbot():
    agent = LifeTrailBaseline()
    print("=== LifeTrail Phase 2: Baseline Agent Ready ===")
    logging.info("New Session Started")

    while True:
        print("\n" + "="*45)
        print("Please select these options to which you want to proceed further:")
        print("1. Tax Calculation")
        print("2. Goal Calculation")
        print("3. Exit")
        print("="*45)
        
        choice = input("Selection (1/2/3): ").strip()

        if choice == "1":
            logging.info("User selected Tax Calculation")
            agent.run_tax_module()
        elif choice == "2":
            logging.info("User selected Goal Calculation")
            agent.run_goal_module()
        elif choice == "3" or choice.lower() in ["exit", "quit"]:
            print("Closing session. Goodbye!")
            logging.info("Session Ended")
            break
        else:
            print("Invalid selection. Please choose 1, 2, or 3.")

if __name__ == "__main__":
    start_chatbot()