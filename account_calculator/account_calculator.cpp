#include "account_calculator.hpp"

#include <iomanip>
#include <iostream>
#include <sstream>
#include <string>

// Modifies the balance to reflect the deposit amount.
void Deposit(double &balance, const double &amount) { balance += amount; }

// Modifies the balance to reflect the withdrawal amount (if there is a
// balance larger than the amount requested). Returns a bool
// indicating if the withdraw succeeded (that the balance was reduced).
bool Withdraw(double &balance, const double &amount)
{
  if (balance > amount)
  {
    balance -= amount;
    return true;
  }
  return false;
}

// Modifies the balance to reflect the withdrawal amount (regardless
// of if there is a balance larger than the amount requested).
// There is a $35 fee for performing an overdraft subtracted
// from the balance as well.
void Overdraft(double &balance, const double &amount,
               const double &overdraft_fee)
{
  balance -= (amount + overdraft_fee);
}

// Returns the interest generated on the balance for one
// month (one twelfth of the year).
double InterestPerMonth(const double &balance, const double &apr)
{
  double interest = ((apr / 100) / 12) * balance;
  // Modifies interest so that it is a decimal with only 2
  // decimal places and then returns it.
  return (int)(100 * interest) / 100.0;
}

// Processes the string into those three referenced ints in the parameter.
void StringDateToInts(const std::string &date, int &year, int &month,
                      int &day)
{
  year = std::stoi(date.substr(0, 4));
  month = std::stoi(date.substr(5, 2));
  day = std::stoi(date.substr(8, 2));
}

// This function is used to help calculate interest. Interest
// is accrued on the first of the month. Returns the number of
// times interest will accrue.
int NumberOfFirstOfMonths(const std::string &date_early,
                          const std::string &date_late)
{
  int year_early;
  int year_late;
  int month_early;
  int month_late;
  int day_early;
  int day_late;
  StringDateToInts(date_early, year_early, month_early, day_early);
  StringDateToInts(date_late, year_late, month_late, day_late);
  if (year_late == year_early)
  {
    if (month_late > month_early)
      return month_late - month_early;
    return month_early - month_late;
  }
  return 12 * (year_late - 1 - year_early) + (12 - month_early) + month_late;
}

// This function is used to calculate the amount of accrued interest.
double InterestEarned(const double &balance, const double &apr,
                      const std::string &date_early,
                      const std::string &date_late)
{
  int num_of_times_interest_accrued =
      NumberOfFirstOfMonths(date_early, date_late);
  double balance_copy = balance;
  for (int i = 0; i != num_of_times_interest_accrued; i++)
  {
    double interest = InterestPerMonth(balance_copy, apr);
    balance_copy += interest;
  }
  return balance_copy - balance;
}

// Modifies ss to contain a string with all the results of the instructions
// requested (except overdraft).
void StringStreamContainingResults(std::stringstream &ss,
                                   const std::string &line,
                                   const std::string &previous_date,
                                   const double &original_balance,
                                   double &balance,
                                   const double &interest_accrued)
{
  // If previous_date contains a year or month earlier than the year or month
  // in line, and the original balance is greater than or equal to zero, add
  // the interest to the balance and modify ss.
  if ((std::stoi(previous_date.substr(0, 4)) < std::stoi(line.substr(0, 4)) ||
       std::stoi(previous_date.substr(5, 2)) < std::stoi(line.substr(5, 2))) &&
      original_balance >= 0)
  {
    balance += interest_accrued;
    // line.substr(0, 10) is the date from string line.
    ss << "On " + line.substr(0, 10) + ": Instructed to perform \"" +
              line.substr(11, std::string::npos) + "\"\nSince " +
              previous_date + ", interest has accrued "
       << NumberOfFirstOfMonths(previous_date, line.substr(0, 10))
       << " times.\n$" << interest_accrued
       << " interest has been earned.\nBalance: " << std::fixed
       << std::setprecision(2) << balance << "\n";
  }
  else if (original_balance < 0)
  {
    ss << "On " + line.substr(0, 10) + ": Instructed to perform \"" +
              line.substr(11, std::string::npos) + "\"\nSince " +
              previous_date + ", interest has accrued "
       << NumberOfFirstOfMonths(previous_date, line.substr(0, 10))
       << " times.\n$0.00 interest has been earned.\nBalance: " << std::fixed
       << std::setprecision(2) << balance << "\n";
  }
  else
  {
    ss << "On " + line.substr(0, 10) + ": Instructed to perform \"" +
              line.substr(11, std::string::npos) + "\"\nBalance: "
       << std::fixed << std::setprecision(2) << balance << "\n";
  }
}

// Modifies ss to contain a string with all the results of the instructions
// requested (including overdraft).
void StringStreamWithResultsAndOverdraft(std::stringstream &ss,
                                         const std::string &line,
                                         const std::string &previous_date,
                                         const double &original_balance,
                                         double &balance,
                                         const double &interest_accrued)
{
  // If previous_date contains a year or month earlier than the year or month
  // in line, and the original balance is greater than or equal to zero, add
  // the interest to the balance and modify ss.
  if ((std::stoi(previous_date.substr(0, 4)) < std::stoi(line.substr(0, 4)) ||
       std::stoi(previous_date.substr(5, 2)) < std::stoi(line.substr(5, 2))) &&
      original_balance >= 0)
  {
    balance += interest_accrued;
    // line.substr(0, 10) is the date from string line.
    ss << "On " + line.substr(0, 10) + ": Instructed to perform \"" +
              line.substr(11, std::string::npos) + "\"\nSince " +
              previous_date + ", interest has accrued "
       << NumberOfFirstOfMonths(previous_date, line.substr(0, 10))
       << " times.\n$" << interest_accrued
       << " interest has been earned.\nOverdraft!\nBalance: " << std::fixed
       << std::setprecision(2) << balance << "\n";
  }
  else if (original_balance < 0)
  {
    ss << "On " + line.substr(0, 10) + ": Instructed to perform \"" +
              line.substr(11, std::string::npos) + "\"\nSince " +
              previous_date + ", interest has accrued "
       << NumberOfFirstOfMonths(previous_date, line.substr(0, 10))
       << " times.\n$0.00 interest has been earned.\nOverdraft!\nBalance: "
       << std::fixed << std::setprecision(2) << balance << "\n";
  }
  else
  {
    ss << "On " + line.substr(0, 10) + ": Instructed to perform \"" +
              line.substr(11, std::string::npos) + "\"\nOverdraft!\nBalance: "
       << std::fixed << std::setprecision(2) << balance << "\n";
  }
}

// Processes a single command/line and returns a string
// (possible with multiple lines) indicating the work done to perform
// the instruction. It also updates the balance to reflect any changes
// and updates the previous_date to the current date of the command/line
// it is processing.
std::string ProcessInstruction(const std::string &line,
                               std::string &previous_date, double &balance,
                               const double &apr, const double &overdraft_fee)
{
  std::stringstream ss;
  if (previous_date == "")
    previous_date = line.substr(0, 10);
  double original_balance = balance;
  double interest_accrued =
      InterestEarned(balance, apr, previous_date, line.substr(0, 10));
  if (line.find("Deposit") != std::string::npos)
  {
    Deposit(balance,
            std::stod(line.substr(line.find("$") + 1, std::string::npos)));
    StringStreamContainingResults(ss, line, previous_date, original_balance,
                                  balance, interest_accrued);
  }
  else if (line.find("Withdraw") != std::string::npos)
  {
    if (Withdraw(balance, std::stod(line.substr(line.find("$") + 1,
                                                std::string::npos))) == true)
    {
      StringStreamContainingResults(ss, line, previous_date, original_balance,
                                    balance, interest_accrued);
    }
    else
    {
      Overdraft(balance,
                std::stod(line.substr(line.find("$") + 1, std::string::npos)),
                overdraft_fee);
      StringStreamWithResultsAndOverdraft(
          ss, line, previous_date, original_balance, balance, interest_accrued);
    }
  }
  previous_date = line.substr(0, 10);
  return ss.str();
}

// Calls process_command multiple times possibly and returns a string
// (possibly with multiple lines) indicating the result(s) of performing
// the instructions requested.
std::string ProcessInstructions(const std::string &multiline, const double &apr,
                                const double &overdraft_fee)
{
  std::stringstream ss(multiline);
  double balance = 0;
  std::string previous_date = "";
  std::string results_of_instructions = "";
  for (std::string line; getline(ss, line);)
  {
    results_of_instructions +=
        ProcessInstruction(line, previous_date, balance, apr, overdraft_fee);
  }
  return results_of_instructions;
}