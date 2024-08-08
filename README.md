## Dynamic Phone and CNIC Validator using DFA

## Overview
The Dynamic Phone and CNIC Validator is a Python-based project that utilizes Deterministic Finite Automata (DFA) to validate phone numbers and CNIC (Computerized National Identity Card) numbers. This project is designed to ensure that the phone number and CNIC match the correct format and originate from the same country, with a focus on countries like Pakistan, India, and Iran.

## Features
**Dynamic DFA for Phone Validation:** Validates phone numbers based on country codes and specific network providers.
**Dynamic DFA for CNIC Validation:** Validates CNIC numbers with checks on province codes and gender determination.
**Cross-Validation:** Ensures the phone number's country code matches the CNIC's country.
**Support for Multiple Countries:** Currently supports Pakistan, India, and Iran, with the flexibility to add more.

## How It Works
**Phone Number Validation:** The phone number is processed through a DFA to determine if it matches the defined rules for format and network. Country code and network provider are extracted if the phone number is valid.
**CNIC Validation:** The CNIC is processed to check its validity based on the length, province code, and gender digit. The CNIC's country code is extracted and validated.
**Cross-Matching:** The phone number's country code is compared with the CNIC's country code. If they don't match, validation fails.
**Input:** Enter the phone number when prompted. Enter the CNIC number if the phone number is valid.

## Files Included
**validator.py:** Main script for running the validation process.
**num_dfa_config.txt:** DFA configuration for phone numbers.
**cnic_dfa_config.txt:** DFA configuration for CNIC numbers.
**country_network_info.txt:** Information on country codes and network providers.
**cnic_info.txt:** Information on CNIC country codes and provinces.
