# GMU-DAEN690-FoodTraceability

Foodborne illness is a significant issue worldwide. The U.S. Centers for Disease Control (CDC) estimates that there are 48 million cases of foodborne disease in the US every year, causing 128,000 hospitalizations and 3,000 fatalities. Complex supply chains make tracking food contamination difficult and time-consuming for health organizations. Another challenge is the lack of availability of supply chain network data for backtracking to the source. The proposed Product tracking system aims to solve this by simulating data and automating the identification of potential sources of contamination within the supply chain network faster. Such a system could improve food safety thereby protecting public health and preventing financial losses. Data is generated based on the FDA (Food and Drug Administration) rule for maintaining additional traceability for different Critical Tracking events (CTE), which are different events in the supply chain. The objective of the project is to predict the contaminated nodes in the supply chain and to develop a graph database to store all the supply chain that was generated during phase 1 of the project. 

## Data Generation

In order to generate data, download the repository to your local drive. 

There are three ways to generate data:

1. Web App User Interface
2. Terminal Application
3. Python API

# Web App User Interface

In a terminal or code editor, change your working directory to GMU-DAEN690-FoodTraceability

Install data_generation/requirements.txt

The Web App User Interface is built using Dash in Python. The file is data_generation/simulation_web_app.py.

To set this up on your own machine:
1. Run data_generation/simulation_web_app.py in either your terminal or code editor.
2. In a web browser go to http://localhost:8050

# Terminal Application

In a terminal or code editor, change your working directory to GMU-DAEN690-FoodTraceability

Install data_generation/requirements.txt

Run data_generation/simulate_supply_chain.py

In the terminal, answer each question with an integer and press Enter.

# Python API

In data_generation, there is a file titled simulation_functions.

To use this in Python code, do:

from simulation_functions import supply_chain_simulation

supply_chain_simulation is an object that has attributes:
- entityCount (INT): the number of business entities in the supply chain 
- foodCount (INT): the number of food items to simulate 
- startDate (STR): the earliest date for an item to begin going through the supply chain. Must be in format YYYY-MM-DD 
- endDate (STR): the latest date for an item to begin going through the supply chain. Must be in format YYYY-MM-DD 
- contamination_rate (INT): the odds that a food item will be randomly contaminated at each event (this does not include cross-contamination). The odds are 1 in X. So if you put X=10,000, it is a 1 in 10,000 chance that the item will be contaminated. 
- selectedFoods (LIST): a list of the food categories to use in data generation. This is from the FDA Food Traceability List. The possibilities are exactly: Herbs (fresh), Leafy greens (fresh), Cheese, Nut butters, Melons, Peppers, Sprouts, Tropical Tree Fruits, Seafood, Ready-to-eat deli salads, Tomatoes, Shell eggs, Cucumbers (fresh), and Fruit.
- create_csv (BOOL): this is whether or not to automatically download csv files of the data

Once you have created the object, simply perform the method run_simulation().




