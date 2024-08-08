####  Dynamic DFA with output  Phone and CNIC validation
class PhoneNumberAndNICChecker:
    def __init__(self, phone_dfa_config_path, cnic_dfa_config_path, country_network_info_path, cnic_info_path):
        self.load_phone_dfa_config(phone_dfa_config_path)
        self.load_cnic_dfa_config(cnic_dfa_config_path)
        self.load_country_network_info(country_network_info_path)
        self.load_cnic_info(cnic_info_path)
        self.reset()

    def load_phone_dfa_config(self, path):
        with open(path, 'r') as file:
            sections = file.read().split('\n\n')
            self.phone_states = set(sections[0].split('\n')[1].split())
            self.phone_alphabet = set(sections[1].split('\n')[1].split())
            self.phone_initial_state = sections[2].split('\n')[1]
            self.phone_final_states = set(sections[3].split('\n')[1].split())
            self.phone_transition_table = {}
            for line in sections[4].split('\n')[1:]:
                if line.strip():  # removes empty lines
                    state, transitions = line.split(': ')
                    self.phone_transition_table[state] = {}
                    for transition in transitions.split(', '):
                        symbol, target_state = transition.split(' -> ')
                        self.phone_transition_table[state][symbol] = target_state

    def load_cnic_dfa_config(self, path):
        with open(path, 'r') as file:
            sections = file.read().split('\n\n')
            self.cnic_states = set(sections[0].split('\n')[1].split())
            self.cnic_alphabet = set(sections[1].split('\n')[1].split())
            self.cnic_initial_state = sections[2].split('\n')[1]
            self.cnic_final_states = set(sections[3].split('\n')[1].split())
            self.cnic_transition_table = {}
            for line in sections[4].split('\n')[1:]:
                if line.strip():  # removes empty lines
                    state, transitions = line.split(': ')
                    self.cnic_transition_table[state] = {}
                    for transition in transitions.split(', '):
                        symbol, target_state = transition.split(' -> ')
                        self.cnic_transition_table[state][symbol] = target_state

    def load_country_network_info(self, path):
        self.country_network_info = {}
        with open(path, 'r') as file:
            lines = file.readlines()
            current_country_code = None
            current_country = None
            networks = {}
            for line in lines:
                line = line.strip()
                if not line:
                    if current_country_code:
                        self.country_network_info[current_country_code] = {
                            "country": current_country,
                            "networks": networks
                        }
                    current_country_code = None
                    current_country = None
                    networks = {}
                elif current_country_code is None:
                    current_country_code = line
                elif line.startswith("Country:"):
                    current_country = line.split("Country:")[1].strip()
                elif line.startswith("Networks:"):
                    continue # skips Networks: line from txt (only label no data)
                else:
                    prefix, provider = line.split(': ')
                    networks[prefix] = provider
            if current_country_code:
                self.country_network_info[current_country_code] = {
                    "country": current_country,
                    "networks": networks
                }

    def load_cnic_info(self, path):
        self.cnic_info = {}
        with open(path, 'r') as file:
            lines = file.readlines()
            current_country_code = None
            current_country = None
            provinces = {}
            for line in lines:
                line = line.strip()
                if not line:
                    if current_country_code:
                        self.cnic_info[current_country_code] = {
                            "country": current_country,
                            "provinces": provinces
                        }
                        print(f"Loaded data for country code {current_country_code}: {self.cnic_info[current_country_code]}")
                    current_country_code = None
                    current_country = None
                    provinces = {}
                elif current_country_code is None:
                    current_country_code = line
                elif line.startswith("Country:"):
                    current_country = line.split("Country:")[1].strip()
                elif line.startswith("Province:"):
                    continue
                else:
                    prefix, province = line.split(': ')
                    provinces[prefix] = province
            if current_country_code:
                self.cnic_info[current_country_code] = {
                    "country": current_country,
                    "provinces": provinces
                }
                #print(f"Loaded data for country code {current_country_code}: {self.cnic_info[current_country_code]}")


    def reset(self):
        self.current_state = self.phone_initial_state
        self.current_input = ""

    def process_phone_input(self, input_string):
        self.reset()
        for symbol in input_string:
            if symbol in self.phone_alphabet and self.current_state in self.phone_transition_table and symbol in self.phone_transition_table[self.current_state]:
                self.current_state = self.phone_transition_table[self.current_state][symbol]
            else:
                self.current_state = 'DE'  
                break
        self.current_input = input_string

    def is_phone_accepted(self):
        return self.current_state in self.phone_final_states

    def get_phone_number_info(self, phone_number):
        self.process_phone_input(phone_number)
        if not self.is_phone_accepted():
            return {"status": "rejected", "message": "Invalid phone number"}

        country_code = None
        network_code = None
        for i in range(1, len(phone_number)):
            prefix = phone_number[:i]
            if prefix in self.country_network_info:
                country_code = prefix
                network_code = phone_number[i:]
                break

        if not country_code:
            return {"status": "rejected", "message": "Country code not found"}

        country_info = self.country_network_info[country_code]
        networks = country_info["networks"]
        provider = None
        for i in range(1, len(network_code)):
            prefix = network_code[:i]
            if prefix in networks:
                provider = networks[prefix]
                break

        if not provider:
            return {"status": "rejected", "message": "Network provider not found"}

        return {
            "status": "accepted",
            "country": country_info["country"],
            "provider": provider,
            "phone_number": phone_number,
            "country_code": country_code  # Adding country_code to the output
        }

    def process_cnic_input(self, cnic):
        self.current_state = self.cnic_initial_state
        for symbol in cnic:
            if symbol in self.cnic_alphabet and self.current_state in self.cnic_transition_table and symbol in self.cnic_transition_table[self.current_state]:
                self.current_state = self.cnic_transition_table[self.current_state][symbol]
            else:
                self.current_state = 'DE'
                break

    def is_cnic_accepted(self):
        return self.current_state in self.cnic_final_states

    def get_cnic_info(self, cnic):
        self.process_cnic_input(cnic)
        if not self.is_cnic_accepted():
            return {"status": "rejected", "message": "Invalid CNIC"}

        country_info = None
        province_code = ""
        cnic_country_code = ""
        if len(cnic) == 13:
            cnic_country_code = "0092"  # Pakistan
            country_info = self.cnic_info.get(cnic_country_code)
            province_code = cnic[:2]
        elif len(cnic) == 12:
            cnic_country_code = "0091"  # India
            country_info = self.cnic_info.get(cnic_country_code)
            province_code = cnic[:4]
        
        elif len(cnic) == 10:
            cnic_country_code = "0098"  # Iran
            country_info = self.cnic_info.get(cnic_country_code)
            province_code = cnic[:2]

        if not country_info or province_code not in country_info["provinces"]:
            return {"status": "rejected", "message": "Invalid CNIC"}

        country = country_info["country"]
        province = country_info["provinces"][province_code]

        gender_digit = int(cnic[-1])
        gender = "Female" if gender_digit % 2 == 0 else "Male"

        return {
            "status": "accepted",
            "cnic": cnic,
            "country": country,
            "province": province,
            "gender": gender,
            "cnic_country_code": cnic_country_code  # Adding CNIC country code to the output
        }


def validate_phone_number_and_cnic(phone_number):
    dfa.reset()
    dfa.process_phone_input(phone_number)
    is_valid_phone = dfa.is_phone_accepted()
    if is_valid_phone:
        phone_info = dfa.get_phone_number_info(phone_number)
        print("The phone number is valid.")
        print(phone_info)
        if phone_info["country"] in ["Pakistan", "India", "Iran"]:
            cnic = input("Enter CNIC number: ")
            cnic_info = dfa.get_cnic_info(cnic)
            if cnic_info["status"] == "accepted":
                # Check if the country codes match
                if phone_info["country_code"] == cnic_info["cnic_country_code"]:
                    print("The CNIC is valid and matches the phone number's country.")
                    print(cnic_info)
                else:
                    print("The CNIC is invalid as it does not match the phone number's country.")
            else:
                print("The CNIC is invalid.")
        else:
            print("CNIC validation not available for this country.")
    else:
        print("The phone number is invalid.")

phone_dfa_config_path = 'num_dfa_config.txt'
cnic_dfa_config_path = 'cnic_dfa_config.txt'
country_network_info_path = 'country_network_info.txt'
cnic_info_path = 'cnic_info.txt'
dfa = PhoneNumberAndNICChecker(phone_dfa_config_path, cnic_dfa_config_path, country_network_info_path, cnic_info_path)

phone_number = input("Enter phone number: ")
validate_phone_number_and_cnic(phone_number)



####  Dynamic DFA with output  
# class PhoneNumberChecker:
#     def __init__(self, dfa_config_path, country_network_info_path):
#         self.load_dfa_config(dfa_config_path)
#         self.load_country_network_info(country_network_info_path)
#         self.reset()

#     def load_dfa_config(self, path):
#         with open(path, 'r') as file:
#             sections = file.read().split('\n\n')
#             self.states = set(sections[0].split('\n')[1].split())
#             self.alphabet = set(sections[1].split('\n')[1].split())
#             self.initial_state = sections[2].split('\n')[1]
#             self.final_states = set(sections[3].split('\n')[1].split())
#             self.transition_table = {}
#             for line in sections[4].split('\n')[1:]:
#                 if line.strip():  # its removes empty lines
#                     state, transitions = line.split(': ')
#                     self.transition_table[state] = {}
#                     for transition in transitions.split(', '):
#                         symbol, target_state = transition.split(' -> ')
#                         self.transition_table[state][symbol] = target_state

#     def load_country_network_info(self, path):
#         self.country_network_info = {}
#         with open(path, 'r') as file:
#             lines = file.readlines()
#             current_country_code = None
#             current_country = None
#             networks = {}
#             for line in lines:
#                 line = line.strip()
#                 if not line:
#                     if current_country_code:
#                         self.country_network_info[current_country_code] = {
#                             "country": current_country,
#                             "networks": networks
#                         }
#                     current_country_code = None
#                     current_country = None
#                     networks = {}
#                 elif current_country_code is None:
#                     current_country_code = line
#                 elif line.startswith("Country:"):
#                     current_country = line.split("Country:")[1].strip()
#                 elif line.startswith("Networks:"):
#                     continue # skips Networks: line from txt (only label no data)
#                 else:
#                     prefix, provider = line.split(': ')
#                     networks[prefix] = provider
#             if current_country_code:
#                 self.country_network_info[current_country_code] = {
#                     "country": current_country,
#                     "networks": networks
#                 }

#     def reset(self):
#         self.current_state = self.initial_state
#         self.current_input = ""

#     def process_input(self, input_string):
#         print(f"Starting DFA processing with initial state: {self.initial_state}")
#         self.current_input = input_string
#         for symbol in input_string:
#             print(f"Current state: {self.current_state}, processing symbol: '{symbol}'")
#             if symbol not in self.alphabet:
#                 print(f"Symbol '{symbol}' not in alphabet.")
#                 self.current_state = 'DE'
#                 break
#             self.current_state = self.transition_table[self.current_state].get(symbol, 'DE')
#             print(f"Transitioned to state: {self.current_state}")
#             if self.current_state == 'DE':
#                 print("Entered dead state.")
#                 break
#         is_valid = self.current_state in self.final_states
#         print(f"Final state: {self.current_state}, is valid: {is_valid}")
#         return is_valid

#     def get_output(self):
#         country_code = self.current_input[:4]
#         remaining_number = self.current_input[4:]
#         if country_code in self.country_network_info:
#             country_info = self.country_network_info[country_code]
#             country = country_info['country']
#             network_provider = None
#             if 'networks' in country_info:
#                 for prefix, provider in country_info['networks'].items():
#                     if remaining_number.startswith(prefix):
#                         network_provider = provider
#                         break
#             if network_provider:
#                 return f"Country: {country}, Network Provider: {network_provider}"
#             return f"Country: {country}"
#         return "Unknown country code or network provider."

# def validate_phone_number(phone_number):
#     dfa.reset()
#     is_valid = dfa.process_input(phone_number)
#     if is_valid:
#         print("The phone number is valid.")
#         print(dfa.get_output())
#     else:
#         print("The phone number is invalid.")

# dfa_config_path = 'num_dfa_config.txt'
# country_network_info_path = 'country_network_info.txt'
# dfa = PhoneNumberChecker(dfa_config_path, country_network_info_path)

# phone_number = input("Enter phone number: ")
# validate_phone_number(phone_number)




#### DFA with output  
# class PhoneNumberChecker:
#     def __init__(self, transition_table, initial_state, final_states, states, alphabet, country_network_info):
#         self.transition_table = transition_table
#         self.initial_state = initial_state
#         self.final_states = final_states
#         self.states = states
#         self.alphabet = alphabet
#         self.country_network_info = country_network_info
#         self.reset()

#     def reset(self):
#         self.current_state = self.initial_state
#         self.current_input = ""

#     def process_input(self, input_string):
#         print(f"Starting DFA processing with initial state: {self.initial_state}")
#         self.current_input = input_string
#         for symbol in input_string:
#             print(f"Current state: {self.current_state}, processing symbol: '{symbol}'")
#             if symbol not in self.alphabet:
#                 print(f"Symbol '{symbol}' not in alphabet.")
#                 self.current_state = 'DE'
#                 break
#             self.current_state = self.transition_table[self.current_state].get(symbol, 'DE')
#             print(f"Transitioned to state: {self.current_state}")
#             if self.current_state == 'DE':
#                 print("Entered dead state.")
#                 break
#         is_valid = self.current_state in self.final_states
#         print(f"Final state: {self.current_state}, is valid: {is_valid}")
#         return is_valid

#     def get_output(self):
#         country_code = self.current_input[:4]  
#         remaining_number = self.current_input[4:]
#         if country_code in self.country_network_info:
#             country_info = self.country_network_info[country_code]
#             country = country_info['country']
#             network_provider = None
#             if 'networks' in country_info:
#                 for prefix, provider in country_info['networks'].items():
#                     if remaining_number.startswith(prefix):
#                         network_provider = provider
#                         break
#             if network_provider:
#                 return f"Country: {country}, Network Provider: {network_provider}"
#         else:
#             return f"Country: {country}"
#         return "Unknown country code or network provider."
#         # if country_code in self.country_network_info:
#         #     country_info = self.country_network_info[country_code]
#         #     country = country_info['country']
#         #     if 'networks' in country_info:
#         #         for prefix_range, provider in country_info['networks'].items():
#         #             for prefix in prefix_range:
#         #                 if remaining_number.startswith(prefix):
#         #                     return f"Country: {country}, Network Provider: {provider}"
#         #     return f"Country: {country}"
#         # return "Unknown country code or network provider."

# states = {'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f', 'DE'}
# alphabet = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9'}
# transition_table = {
#     'A': {'0': 'B', '1': 'DE', '2': 'DE', '3': 'DE', '4': 'DE', '5': 'DE', '6': 'DE', '7': 'DE', '8': 'DE', '9': 'DE'},
#     'B': {'0': 'C', '1': 'DE', '2': 'DE', '3': 'DE', '4': 'DE', '5': 'DE', '6': 'DE', '7': 'DE', '8': 'DE', '9': 'DE'},
#     'C': {'0': 'DE', '1': 'DE', '2': 'DE', '3': 'DE', '4': 'DE', '5': 'DE', '6': 'DE', '7': 'DE', '8': 'DE', '9': 'D'},
#     'D': {'0': 'P', '1': 'a', '2': 'E', '3': 'T', '4': 'DE', '5': 'DE', '6': 'DE', '7': 'DE', '8': 'W', '9': 'DE'},
#     'E': {'0': 'DE', '1': 'DE', '2': 'DE', '3': 'F', '4': 'DE', '5': 'DE', '6': 'DE', '7': 'DE', '8': 'DE', '9': 'DE'},
#     'F': {'0': 'G', '1': 'G', '2': 'G', '3': 'G', '4': 'G', '5': 'DE', '6': 'DE', '7': 'G', '8': 'DE', '9': 'DE'},
#     'G': {'0': 'H', '1': 'H', '2': 'H', '3': 'H', '4': 'H', '5': 'H', '6': 'H', '7': 'H', '8': 'H', '9': 'H'},
#     'H': {'0': 'I', '1': 'I', '2': 'I', '3': 'I', '4': 'I', '5': 'I', '6': 'I', '7': 'I', '8': 'I', '9': 'I'},
#     'I': {'0': 'J', '1': 'J', '2': 'J', '3': 'J', '4': 'J', '5': 'J', '6': 'J', '7': 'J', '8': 'J', '9': 'J'},
#     'J': {'0': 'K', '1': 'K', '2': 'K', '3': 'K', '4': 'K', '5': 'K', '6': 'K', '7': 'K', '8': 'K', '9': 'K'},
#     'K': {'0': 'L', '1': 'L', '2': 'L', '3': 'L', '4': 'L', '5': 'L', '6': 'L', '7': 'L', '8': 'L', '9': 'L'},
#     'L': {'0': 'M', '1': 'M', '2': 'M', '3': 'M', '4': 'M', '5': 'M', '6': 'M', '7': 'M', '8': 'M', '9': 'M'},
#     'M': {'0': 'N', '1': 'N', '2': 'N', '3': 'N', '4': 'N', '5': 'N', '6': 'N', '7': 'N', '8': 'N', '9': 'N'},
#     'N': {'0': 'O', '1': 'O', '2': 'O', '3': 'O', '4': 'O', '5': 'O', '6': 'O', '7': 'O', '8': 'O', '9': 'O'},
#     'O': {'0': 'DE', '1': 'DE', '2': 'DE', '3': 'DE', '4': 'DE', '5': 'DE', '6': 'DE', '7': 'DE', '8': 'DE', '9': 'DE'},
#     'P': {'0': 'DE', '1': 'DE', '2': 'DE', '3': 'DE', '4': 'DE', '5': 'Q', '6': 'DE', '7': 'DE', '8': 'DE', '9': 'DE'},
#     'Q': {'0': 'R', '1': 'R', '2': 'DE', '3': 'R', '4': 'R', '5': 'DE', '6': 'DE', '7': 'DE', '8': 'DE', '9': 'DE'},
#     'R': {'0': 'S', '1': 'S', '2': 'S', '3': 'S', '4': 'S', '5': 'S', '6': 'S', '7': 'S', '8': 'S', '9': 'S'},
#     'S': {'0': 'I', '1': 'I', '2': 'I', '3': 'I', '4': 'I', '5': 'I', '6': 'I', '7': 'I', '8': 'I', '9': 'I'},
#     'T': {'0': 'DE', '1': 'DE', '2': 'DE', '3': 'DE', '4': 'DE', '5': 'DE', '6': 'DE', '7': 'U', '8': 'DE', '9': 'DE'},
#     'U': {'0': 'V', '1': 'V', '2': 'V', '3': 'V', '4': 'V', '5': 'V', '6': 'V', '7': 'V', '8': 'V', '9': 'V'},
#     'V': {'0': 'I', '1': 'I', '2': 'I', '3': 'I', '4': 'I', '5': 'I', '6': 'I', '7': 'I', '8': 'I', '9': 'I'},
#     'W': {'0': 'DE', '1': 'DE', '2': 'DE', '3': 'DE', '4': 'DE', '5': 'DE', '6': 'DE', '7': 'DE', '8': 'DE', '9': 'X'},
#     'X': {'0': 'Y', '1': 'DE', '2': 'DE', '3': 'Y', '4': 'DE', '5': 'DE', '6': 'DE', '7': 'DE', '8': 'DE', '9': 'DE'},
#     'Y': {'0': 'Z', '1': 'Z', '2': 'Z', '3': 'Z', '4': 'Z', '5': 'Z', '6': 'Z', '7': 'Z', '8': 'Z', '9': 'Z'},
#     'Z': {'0': 'I', '1': 'I', '2': 'I', '3': 'I', '4': 'I', '5': 'I', '6': 'I', '7': 'I', '8': 'I', '9': 'I'},
#     'a': {'0': 'DE', '1': 'DE', '2': 'DE', '3': 'DE', '4': 'b', '5': 'DE', '6': 'DE', '7': 'DE', '8': 'DE', '9': 'DE'},
#     'b': {'0': 'c', '1': 'DE', '2': 'DE', '3': 'DE', '4': 'DE', '5': 'DE', '6': 'DE', '7': 'DE', '8': 'DE', '9': 'DE'},
#     'c': {'0': 'DE', '1': 'DE', '2': 'DE', '3': 'DE', '4': 'd', '5': 'd', '6': 'DE', '7': 'DE', '8': 'DE', '9': 'DE'},
#     'd': {'0': 'e', '1': 'e', '2': 'e', '3': 'e', '4': 'e', '5': 'e', '6': 'e', '7': 'e', '8': 'e', '9': 'e'},
#     'e': {'0': 'f', '1': 'f', '2': 'f', '3': 'f', '4': 'f', '5': 'f', '6': 'f', '7': 'f', '8': 'f', '9': 'f'},
#     'f': {'0': 'J', '1': 'J', '2': 'J', '3': 'J', '4': 'J', '5': 'J', '6': 'J', '7': 'J', '8': 'J', '9': 'J'},
#     'DE': {'0': 'DE', '1': 'DE', '2': 'DE', '3': 'DE', '4': 'DE', '5': 'DE', '6': 'DE', '7': 'DE', '8': 'DE', '9': 'DE'}
# }
# initial_state = 'A'
# final_states = {'O'}

# country_network_info = {
#     '0092': {
#         'country': 'Pakistan',
#         'networks': {
#             ('30', '31', '32'): 'Jazz',
#             ('33',): 'Ufone',
#             ('34',): 'Telenor',
#             ('35', '36', '37'): 'Zong'
#         }
#     },
#     '0090': {
#         'country': 'Turkey',
#         'networks': {
#             ('500', '501', '502', '503', '504', '505', '506', '507', '508', '509'): 'TurkTelecom',
#             ('510', '511', '512', '513', '514', '515', '516', '517', '518', '519', '520', '521', '522', '523', '524', '525', '526', '527', '528', '529', '530', '531', '532', '533', '534', '535', '536', '537', '538', '539'): 'Turkcell',
#             ('540', '541', '542', '543', '544', '545', '546', '547', '548', '549'): 'Vodafone'
#         }
#     },
#     '0093': {
#         'country': 'Afghanistan',
#         'networks': {
#             ('70', '71'): 'AWCC',
#             ('79', '72'): 'Roshan',
#             ('78', '73'): 'Etisalat',
#             ('77', '76'): 'MTN',
#             ('74',): 'Salaam',
#             ('75',): 'AfghanTelecom'
#         }
#     },
#     '0098': {
#         'country': 'Iran',
#         'networks': {
#             ('900', '901', '902'): 'MTN',
#             ('903', '904', '905', '906', '907', '908', '909'): 'Irancell'
#         }
#     },
#     '0091': {
#         'country': 'India',
#         'networks': {
#             ('404',): 'Airtel',
#             ('405',): 'MTS'
#         }
#     }
# }

# dfa = PhoneNumberChecker(transition_table, initial_state, final_states, states, alphabet, country_network_info)

# def validate_phone_number(phone_number):
#     dfa.reset()
#     is_valid = dfa.process_input(phone_number)
#     if is_valid:
#         print("The phone number is valid.")
#         print(dfa.get_output())
#     else:
#         print("The phone number is invalid.")

# phone_number = input("Enter phone number: ")
# validate_phone_number(phone_number)




####dfamachine
# class PhoneNumberChecker:
#     def __init__(self, transition_table, initial_state, final_states, states, alphabet):
#         self.transition_table = transition_table
#         self.initial_state = initial_state
#         self.final_states = final_states
#         self.states = states
#         self.alphabet = alphabet
#         self.reset()

#     def reset(self):
#         self.current_state = self.initial_state

#     def process_input(self, input_string):
#         print(f"Starting DFA processing with initial state: {self.initial_state}")
#         for symbol in input_string:
#             print(f"Current state: {self.current_state}, processing symbol: '{symbol}'")
#             if symbol not in self.alphabet:
#                 print(f"Symbol '{symbol}' not in alphabet.")
#                 self.current_state = 'DE'
#                 break
#             self.current_state = self.transition_table[self.current_state].get(symbol, 'DE')
#             print(f"Transitioned to state: {self.current_state}")
#             if self.current_state == 'DE':
#                 print("Entered dead state.")
#                 break
#         is_valid = self.current_state in self.final_states
#         print(f"Final state: {self.current_state}, is valid: {is_valid}")
#         return is_valid

# states = {'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f', 'DE'}

# alphabet = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9'}

# transition_table = {
#     'A': {'0': 'B', '1': 'DE', '2': 'DE', '3': 'DE', '4': 'DE', '5': 'DE', '6': 'DE', '7': 'DE', '8': 'DE', '9': 'DE'},
#     'B': {'0': 'C', '1': 'DE', '2': 'DE', '3': 'DE', '4': 'DE', '5': 'DE', '6': 'DE', '7': 'DE', '8': 'DE', '9': 'DE'},
#     'C': {'0': 'DE', '1': 'DE', '2': 'DE', '3': 'DE', '4': 'DE', '5': 'DE', '6': 'DE', '7': 'DE', '8': 'DE', '9': 'D'},
#     'D': {'0': 'P', '1': 'a', '2': 'E', '3': 'T', '4': 'DE', '5': 'DE', '6': 'DE', '7': 'DE', '8': 'W', '9': 'DE'},
#     'E': {'0': 'DE', '1': 'DE', '2': 'DE', '3': 'F', '4': 'DE', '5': 'DE', '6': 'DE', '7': 'DE', '8': 'DE', '9': 'DE'},
#     'F': {'0': 'G', '1': 'G', '2': 'G', '3': 'G', '4': 'G', '5': 'DE', '6': 'DE', '7': 'G', '8': 'DE', '9': 'DE'},
#     'G': {'0': 'H', '1': 'H', '2': 'H', '3': 'H', '4': 'H', '5': 'H', '6': 'H', '7': 'H', '8': 'H', '9': 'H'},
#     'H': {'0': 'I', '1': 'I', '2': 'I', '3': 'I', '4': 'I', '5': 'I', '6': 'I', '7': 'I', '8': 'I', '9': 'I'},
#     'I': {'0': 'J', '1': 'J', '2': 'J', '3': 'J', '4': 'J', '5': 'J', '6': 'J', '7': 'J', '8': 'J', '9': 'J'},
#     'J': {'0': 'K', '1': 'K', '2': 'K', '3': 'K', '4': 'K', '5': 'K', '6': 'K', '7': 'K', '8': 'K', '9': 'K'},
#     'K': {'0': 'L', '1': 'L', '2': 'L', '3': 'L', '4': 'L', '5': 'L', '6': 'L', '7': 'L', '8': 'L', '9': 'L'},
#     'L': {'0': 'M', '1': 'M', '2': 'M', '3': 'M', '4': 'M', '5': 'M', '6': 'M', '7': 'M', '8': 'M', '9': 'M'},
#     'M': {'0': 'N', '1': 'N', '2': 'N', '3': 'N', '4': 'N', '5': 'N', '6': 'N', '7': 'N', '8': 'N', '9': 'N'},
#     'N': {'0': 'O', '1': 'O', '2': 'O', '3': 'O', '4': 'O', '5': 'O', '6': 'O', '7': 'O', '8': 'O', '9': 'O'},
#     'O': {'0': 'DE', '1': 'DE', '2': 'DE', '3': 'DE', '4': 'DE', '5': 'DE', '6': 'DE', '7': 'DE', '8': 'DE', '9': 'DE'},
#     'P': {'0': 'DE', '1': 'DE', '2': 'DE', '3': 'DE', '4': 'DE', '5': 'Q', '6': 'DE', '7': 'DE', '8': 'DE', '9': 'DE'},
#     'Q': {'0': 'R', '1': 'R', '2': 'DE', '3': 'R', '4': 'R', '5': 'DE', '6': 'DE', '7': 'DE', '8': 'DE', '9': 'DE'},
#     'R': {'0': 'S', '1': 'S', '2': 'S', '3': 'S', '4': 'S', '5': 'S', '6': 'S', '7': 'S', '8': 'S', '9': 'S'},
#     'S': {'0': 'I', '1': 'I', '2': 'I', '3': 'I', '4': 'I', '5': 'I', '6': 'I', '7': 'I', '8': 'I', '9': 'I'},
#     'T': {'0': 'DE', '1': 'DE', '2': 'DE', '3': 'DE', '4': 'DE', '5': 'DE', '6': 'DE', '7': 'U', '8': 'DE', '9': 'DE'},
#     'U': {'0': 'V', '1': 'V', '2': 'V', '3': 'V', '4': 'V', '5': 'V', '6': 'V', '7': 'V', '8': 'V', '9': 'V'},
#     'V': {'0': 'I', '1': 'I', '2': 'I', '3': 'I', '4': 'I', '5': 'I', '6': 'I', '7': 'I', '8': 'I', '9': 'I'},
#     'W': {'0': 'DE', '1': 'DE', '2': 'DE', '3': 'DE', '4': 'DE', '5': 'DE', '6': 'DE', '7': 'DE', '8': 'DE', '9': 'X'},
#     'X': {'0': 'Y', '1': 'DE', '2': 'DE', '3': 'Y', '4': 'DE', '5': 'DE', '6': 'DE', '7': 'DE', '8': 'DE', '9': 'DE'},
#     'Y': {'0': 'Z', '1': 'Z', '2': 'Z', '3': 'Z', '4': 'Z', '5': 'Z', '6': 'Z', '7': 'Z', '8': 'Z', '9': 'Z'},
#     'Z': {'0': 'I', '1': 'I', '2': 'I', '3': 'I', '4': 'I', '5': 'I', '6': 'I', '7': 'I', '8': 'I', '9': 'I'},
#     'a': {'0': 'DE', '1': 'DE', '2': 'DE', '3': 'DE', '4': 'b', '5': 'DE', '6': 'DE', '7': 'DE', '8': 'DE', '9': 'DE'},
#     'b': {'0': 'c', '1': 'DE', '2': 'DE', '3': 'DE', '4': 'DE', '5': 'DE', '6': 'DE', '7': 'DE', '8': 'DE', '9': 'DE'},
#     'c': {'0': 'DE', '1': 'DE', '2': 'DE', '3': 'DE', '4': 'd', '5': 'd', '6': 'DE', '7': 'DE', '8': 'DE', '9': 'DE'},
#     'd': {'0': 'e', '1': 'e', '2': 'e', '3': 'e', '4': 'e', '5': 'e', '6': 'e', '7': 'e', '8': 'e', '9': 'e'},
#     'e': {'0': 'f', '1': 'f', '2': 'f', '3': 'f', '4': 'f', '5': 'f', '6': 'f', '7': 'f', '8': 'f', '9': 'f'},
#     'f': {'0': 'J', '1': 'J', '2': 'J', '3': 'J', '4': 'J', '5': 'J', '6': 'J', '7': 'J', '8': 'J', '9': 'J'},
#     'DE': {'0': 'DE', '1': 'DE', '2': 'DE', '3': 'DE', '4': 'DE', '5': 'DE', '6': 'DE', '7': 'DE', '8': 'DE', '9': 'DE'}
# }

# initial_state = 'A'
# final_states = {'O'}

# dfa = PhoneNumberChecker(transition_table, initial_state, final_states, states, alphabet)

# def validate_phone_number(phone_number):
#     dfa.reset()

#     is_valid = dfa.process_input(phone_number)
#     return is_valid

# # Take input from the user
# phone_number = input("Enter phone number: ")
# if validate_phone_number(phone_number):
#     print("The phone number is valid.")
# else:
#     print("The phone number is invalid.")


##mealymachine
# class PhoneNumberChecker:
#     def __init__(self):
#         self.states = {'start', 'country_code', 'network_code', 'phone_number'}
#         self.alphabet = {'+', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9'}
#         self.transition_function = {
#             'start': {'+': 'country_code'},
#             'country_code': {'9': 'country_code', '2': 'country_code', '3': 'network_code'},
#             'network_code': {'0': 'phone_number', '1': 'phone_number', '2': 'phone_number',
#                              '3': 'phone_number', '4': 'phone_number', '5': 'phone_number',
#                              '6': 'phone_number', '7': 'phone_number', '8': 'phone_number',
#                              '9': 'phone_number'},
#             'phone_number': {'0': 'phone_number', '1': 'phone_number', '2': 'phone_number',
#                              '3': 'phone_number', '4': 'phone_number', '5': 'phone_number',
#                              '6': 'phone_number', '7': 'phone_number', '8': 'phone_number',
#                              '9': 'phone_number'}
#         }
#         self.output_function = {
#             'country_code': {'+92': 'Pakistan'},
#             'network_code': {'0': 'Jazz', '1': 'Zong', '2': 'Jazz', '3': 'Ufone', '4': 'Telenor',
#                              '5': 'Zong', '6': 'Zong', '7': 'Zong', '8': 'Zong', '9': 'Zong'}
#         }
#         self.current_state = 'start'

#     def check(self, input_string):
#         country = ""
#         for symbol in input_string:
#             if symbol not in self.alphabet:
#                 return "Invalid"
#             next_state = self.transition_function[self.current_state].get(symbol)
#             if next_state is None:
#                 return "Invalid"
#             self.current_state = next_state
#             if self.current_state == 'country_code':
#                 country = self.output_function['country_code'].get(symbol)
#             elif self.current_state == 'phone_number' and len(input_string) != 13:
#                 return "Invalid"
#             elif self.current_state == 'phone_number':
#                 network_code = input_string[4]  
#                 network_provider = self.output_function['network_code'].get(network_code)
#                 if network_provider is None:
#                     return "Network provider not found for network code: " + network_code
#                 return "Valid, Country: " + str(country) + ", Network Provider: " + str(network_provider)

#         return "Invalid"

# phone_checker = PhoneNumberChecker()
# phone_number = input("Enter the phone number (e.g., +923313733874): ")
# result = phone_checker.check(phone_number)
# print(result)
