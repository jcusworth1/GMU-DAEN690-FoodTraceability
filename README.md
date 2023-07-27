# GMU-DAEN690-FoodTraceability

Foodborne illness is a significant issue worldwide. The U.S. Centers for Disease Control (CDC) estimates that there are 48 million cases of foodborne disease in the US every year, causing 128,000 hospitalizations and 3,000 fatalities. Complex supply chains make tracking food contamination difficult and time-consuming for health organizations. Another challenge is the lack of availability of supply chain network data for backtracking to the source. The proposed Product tracking system aims to solve this by simulating data and automating the identification of potential sources of contamination within the supply chain network faster. Such a system could improve food safety thereby protecting public health and preventing financial losses. Data is generated based on the FDA (Food and Drug Administration) rule for maintaining additional traceability for different Critical Tracking events (CTE), which are different events in the supply chain. The objective of the project is to predict the contaminated nodes in the supply chain and to develop a graph database to store all the supply chain that was generated during phase 1 of the project. 

## Data Generation

In order to generate data, run the file simulate_supply_chain.py.

This can either be done in a terminal or in a code editor. Either way, the terminal will ask you to input two values:

1. Enter how many business entities exist in the supply chain
2. Enter how many food items you would like to simulate

For each input, enter a number and press enter.

After you input both values, a progress bar will appear as the data is generated
