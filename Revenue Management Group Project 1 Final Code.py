## Revenue Management Group Project



#################################################### Part 1 ############################################################
# Import necessary libraries
from selenium import webdriver
import pandas as pd
from re import sub
import timeit
import itertools
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Section 1: Generate all possible combinations
# Create a list of all possible combos
x = [60, 54, 48, 36]
combos = []

for i in itertools.product(x, repeat=14):
    if i[0] >= i[1] >= i[2] >= i[3] >= i[4] >= i[5] >= i[6] >= i[7] >= i[8] >= i[9] >= i[10] >= i[11] >= i[12] >= i[13]:
        combos.append(i)

check = pd.DataFrame(combos)

# Convert combos to list format and ensure each combo starts with 60
combos_list = []

for i in combos:
    combos_list.append(list(i))

# First step in each combo is always 60
for i in combos_list:
    i.insert(0, 60)

# Assign an ID to each combo
for i in range(len(combos_list)):
    combos_list[i].insert(0, i)

# Convert list of combos to DataFrame and rename columns
combos_df = pd.DataFrame(combos_list)
combos_df = combos_df.rename(columns={0: "combo_number"})

# Section 2: Setup Selenium WebDriver
browser = webdriver.Chrome()
browser.get("http://www.randhawa.us/games/retailer/nyu.html")

# Wait for the necessary buttons to be clickable
maintain = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.ID, "maintainButton")))
dc_10 = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.ID, "tenButton")))
dc_20 = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.ID, "twentyButton")))
dc_40 = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.ID, "fortyButton")))

# Section 3: Divide combos into manageable sections
section_1 = combos_list[0:100]
section_2 = combos_list[101:200]
section_3 = combos_list[201:300]
section_4 = combos_list[301:400]
section_5 = combos_list[401:500]
section_6 = combos_list[501:680]

data = []

# Section 4: Main scraping script
# Iterate through the first section of combos
s = section_6

# Start timing the execution
start = timeit.default_timer()
for i in s:
    for t in range(2):  # Perform 2 replications of each combo
        for j in range(1, len(i) - 1):
            # Perform clicks based on combo values
            if i[j + 1] < i[j] and i[j + 1] == 54:
                dc_10.click()
            elif i[j + 1] < i[j] and i[j + 1] == 48:
                dc_20.click()
            elif i[j + 1] < i[j] and i[j + 1] == 36:
                dc_40.click()
                break
            else:
                maintain.click()
        
        # Extract results from the table
        for tr in browser.find_elements(By.XPATH, '//table[@id="result-table"]//tr'):
            tds = tr.find_elements(By.TAG_NAME, 'td')
            if tds:
                data.append([i[0]] + [t] + [int(td.text) for td in tds])
        
        # Extract revenue and perfect values
        revenue = int(sub(r'[^\d.]', '', browser.find_element(By.ID, "rev").text))
        perfect = int(sub(r'[^\d.]', '', browser.find_element(By.ID, "perfect").text))
        data.append([i[0], t, 16, revenue, perfect, 1 - revenue/perfect])
        
        # Reset for the next replication
        browser.find_element(By.CLASS_NAME, "button").click()

# Stop timing the execution
stop = timeit.default_timer()
print('Time: ', stop - start)

# Section 5: Save data to CSV
# Transfer data to a DataFrame and then save in CSV
emptydf6 = []
emptydf6 = emptydf6 + data

df6 = pd.DataFrame(emptydf6, columns=["combo", "replication", "week", "price", "sales", "remain_invent"])

# Define the directory path where you want to save the CSV file
directory = r"C:\Users\aadel\OneDrive\Documents\Mcgill Masters\4. Summer Term 2\Revenue Management"

# Define the file name
file_name = "output_section6.csv"

# Define the full file path
file_path = directory + "\\" + file_name

# Save the DataFrame to a CSV file
df6.to_csv(file_path, index=False)


# Section 6: Combine multiple CSV files into one

import os

# Define the directory and file name patterns
directory = r"C:\Users\aadel\OneDrive\Documents\Mcgill Masters\4. Summer Term 2\Revenue Management"
file_patterns = [f"output_section{i}.csv" for i in range(1, 7)]
combined_file_name = "combined_output.csv"
combined_file_path = os.path.join(directory, combined_file_name)

# Initialize an empty DataFrame for the combined data
combined_df = pd.DataFrame()

# Iterate through each file and concatenate them
for i, file_name in enumerate(file_patterns):
    file_path = os.path.join(directory, file_name)
    df = pd.read_csv(file_path)
    
    if i == 0:
        # For the first file, include the headers
        combined_df = df
    else:
        # For subsequent files, exclude the headers
        combined_df = pd.concat([combined_df, df], ignore_index=True)

# Save the combined DataFrame to a new CSV file
combined_df.to_csv(combined_file_path, index=False)




############################################# PART 2 ###########################################################


##SECTION 1
import pandas as pd

# Load the dataset
df = pd.read_csv("C:/Users/aadel/OneDrive/Documents/Mcgill Masters/4. Summer Term 2/Revenue Management/combined_output.csv")

# Separate row 16 information into a separate dataframe
row_16_data = df[df['week'] == 16].copy()
df = df[df['week'] != 16]

# Remove unnecessary rows (e.g., week 16)
df = df[df['week'] <= 15]

# Rename the columns of row_16_data
row_16_data = row_16_data.rename(columns={
    'price': 'Your_revenue',
    'sales': 'Perfect_foresight_strategy',
    'remain_invent': 'Difference'
})

# Sort row 16 data by the "Difference" column and select the top 100 rows
top_100_combos = row_16_data.nsmallest(100, 'Difference')

# Get the combo numbers and replication numbers of the top 100 best performing combinations
top_100_combos_list = []
for index, row in top_100_combos.iterrows():
    combo = row['combo']
    replication = row['replication']
    top_100_combos_list.append((combo, replication))

## Define a function to simulate pricing strategy and track inventory and decisions
def simulate_strategy(df, combo, replication):
    # Initialize decision list to store decisions made at each week
    decision_list = []
    
    # Get combo ID
    combo_id = str(combo) + str(replication)
    
    # Filter data for specified combo and replication
    df_filtered = df[(df['combo'] == combo) & (df['replication'] == replication)].reset_index(drop=True)
    
    # Iterate through each week
    for index, row in df_filtered.iterrows():
        week = row['week']
        remain_invent = row['remain_invent']
        price = row['price']
        
        # Determine decision based on week and price
        if week == 1:
            decision = 'Maintain'
        elif price == 60 and df_filtered.iloc[index - 1]['price'] == 60:
            decision = 'Maintain'
        elif price == 54 and df_filtered.iloc[index - 1]['price'] == 54:
            decision = 'Maintain'
        elif price == 48 and df_filtered.iloc[index - 1]['price'] == 48:
            decision = 'Maintain'
        elif price == 36 and df_filtered.iloc[index - 1]['price'] == 36:
            decision = 'Maintain'
        elif price == 54 and df_filtered.iloc[index - 1]['price'] == 60:
            decision = '10%'
        elif price == 48 and df_filtered.iloc[index - 1]['price'] in [54, 60]:
            decision = '20%'
        elif price == 36 and df_filtered.iloc[index - 1]['price'] in [48, 54, 60]:
            decision = '40%'
        else:
            decision = 'NA'
        
        # Append week, remaining inventory, and decision to decision list
        decision_list.append([combo_id, week, remain_invent, decision])
    
    # Convert decision list to DataFrame
    decision_df = pd.DataFrame(decision_list, columns=['ID', 'Week', 'Remaining Inventory', 'Decision'])
    
    return decision_df

# Define a function to analyze decision DataFrame and generate rules
def analyze_pricing_strategies(merged_df):
    # Filter out rows where decision is not 10%, 20%, or 40%
    decision_df = merged_df[merged_df['Decision'].isin(['10%', '20%', '40%'])]
    
    # Group decision DataFrame by Decision and Week, then calculate the average remaining inventory
    grouped_df = decision_df.groupby(['Decision', 'Week'])['Remaining Inventory'].mean().reset_index()
    
    # Filter out only the rows where Decision is 10%, 20%, or 40%
    ten_percent_df = grouped_df[grouped_df['Decision'] == '10%']
    twenty_percent_df = grouped_df[grouped_df['Decision'] == '20%']
    forty_percent_df = grouped_df[grouped_df['Decision'] == '40%']
    
    # Calculate the average remaining inventory at which 10%, 20%, and 40% were triggered
    avg_inventory_10_percent = round(ten_percent_df['Remaining Inventory'].mean())
    avg_inventory_20_percent = round(twenty_percent_df['Remaining Inventory'].mean())
    avg_inventory_40_percent = round(forty_percent_df['Remaining Inventory'].mean())
    
    # Calculate the average week at which 10%, 20%, and 40% were triggered
    avg_week_10_percent = round(ten_percent_df['Week'].mean())
    avg_week_20_percent = round(twenty_percent_df['Week'].mean())
    avg_week_40_percent = round(forty_percent_df['Week'].mean())
    
    return {
        '10%': {'Average Remaining Inventory': avg_inventory_10_percent, 'Average Week': avg_week_10_percent},
        '20%': {'Average Remaining Inventory': avg_inventory_20_percent, 'Average Week': avg_week_20_percent},
        '40%': {'Average Remaining Inventory': avg_inventory_40_percent, 'Average Week': avg_week_40_percent}
    }

# Define the filter conditions for Section 2
filter_conditions = [
    {'label': 'Remain Invent > 1900 and <= 1925', 'condition': (df['week'] == 1) & (df['remain_invent'] > 1900) & (df['remain_invent'] <= 1925)},
    {'label': 'Remain Invent > 1925', 'condition': (df['week'] == 1) & (df['remain_invent'] > 1925)},
    {'label': 'Remain Invent <= 1900', 'condition': (df['week'] == 1) & (df['remain_invent'] <= 1900)}
]

# Loop through each filter condition
for filter_condition in filter_conditions:
    print(f"Results for filter: {filter_condition['label']}")
    
    # Apply the filter condition
    week_1_filtered_df = df[filter_condition['condition']]
    
    # Create a list to store the final combos and replications based on the filter
    final_combos_list = []
    for combo, replication in top_100_combos_list:
        if len(week_1_filtered_df[(week_1_filtered_df['combo'] == combo) & (week_1_filtered_df['replication'] == replication)]) > 0:
            final_combos_list.append((combo, replication))
    
    # Create an empty DataFrame to store the results
    merged_df = pd.DataFrame(columns=['ID', 'Week', 'Remaining Inventory', 'Decision'])
    
    # Iterate over the filtered combos and replications
    for combo, replication in final_combos_list:
        result_df = simulate_strategy(df, combo, replication)
        merged_df = pd.concat([merged_df, result_df])
    
    # Reset index of merged DataFrame
    merged_df.reset_index(drop=True, inplace=True)
    
    # Analyze pricing strategies for the filtered data
    pricing_strategies_analysis = analyze_pricing_strategies(merged_df)
    
    # Print the results
    print("Average Pricing Strategies:")
    for strategy, values in pricing_strategies_analysis.items():
        print(f"{strategy}:")
        print(f"  - Average Remaining Inventory: {values['Average Remaining Inventory']}")
        print(f"  - Average Week: {values['Average Week']}")
    print("\n" + "="*50 + "\n")


