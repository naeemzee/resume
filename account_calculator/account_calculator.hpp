/*
Creating a bank account calculator that can process withdraws and deposits,
calculate interest, and apply overdraft fees. The most important function is
named ProcessInstructions. It takes as arguments a multiline string (where each
line of the string denotes a date and an instruction) and a double denoting the
Annual Percent Rate (apr, i.e. the interest rate for the account). This function
returns a multiline string denoting the results of performing the instructions
requested.
*/

#pragma once
#include <string>

void Deposit(double &, const double &);

bool Withdraw(double &, const double &);

void Overdraft(double &, const double &, const double &);

double InterestPerMonth(const double &, const double &);

void StringDateToInts(const std::string &, int &, int &, int &);

int NumberOfFirstOfMonths(const std::string &, const std::string &);

double InterestEarned(const double &, const double &, const std::string &,
                      const std::string &);

std::string ProcessInstruction(const std::string &, std::string &, double &,
                               const double &, const double &);

std::string ProcessInstructions(const std::string &, const double &,
                                const double &);