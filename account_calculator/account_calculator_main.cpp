#include "account_calculator.hpp"

#include <iostream>
#include <string>

int main()
{
  std::string all_instructions;
  std::string instruction;
  double apr;
  double overdraft_fee;
  std::cout << "Welcome to My Bank Account Calculator!" << std::endl;
  std::cout << "\nExample of Instructions:"
            << "\n2019-06-13 Withdraw $700.12\n2020-12-09 Deposit $700"
            << std::endl;
  std::cout << "\n**If you want to start with your current account balance,"
            << "\nthe first instruction should be a deposit of the current"
            << "\nbalance in your account using the date of your last"
            << "\ndeposit/withdrawal. Once done with the instruction(s),"
            << "\npress enter/return twice.**" << std::endl;
  std::cout << "\nInstructions:" << std::endl;
  // Each line of input/instructions is added to all_instructions until there is
  // no more input.
  while (std::getline(std::cin, instruction) && !instruction.empty())
  {
    all_instructions += instruction + "\n";
  }
  std::cout << "Overdraft Fee: $";
  std::cin >> overdraft_fee;
  std::cout << "\nAPR: ";
  std::cin >> apr;
  std::string result =
      ProcessInstructions(all_instructions, apr, overdraft_fee);
  std::cout << "\n"
            << result << std::endl;
}