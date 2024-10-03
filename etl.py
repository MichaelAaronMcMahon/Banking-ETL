import pandas as pd
import re

#Extract data
dfx = pd.read_excel('bank.xlsx')
dfc = pd.read_csv('bank.csv')
dfb = pd.read_excel('branch.xlsx')

#Concatenate the two dataframes
df = pd.concat([dfx, dfc], ignore_index=True)

#Remove middle initial
df["First Name"] = df["First Name"].apply(lambda x: re.sub("\s.*", "", x))

#Add a column "Full Name" which is a combination of each customer's first and second name
df["Full Name"] = df["First Name"] + " " + df["Last Name"]

#Standardize branch capitalization
def replace(cap):
    return cap.group(1).upper() + cap.group(2).lower()
df["Branch"] = df["Branch"].apply(lambda x: re.sub(r"(^[a-zA-Z])(.*)", replace, x))

#Drop instances with invalid SSNs
dfSsn = df["SSN"].apply(lambda x: re.search(r"^[0-9]{9}$", str(x)))
for i in range(dfSsn.size):
    if dfSsn.loc[i] == None:
        df = df.drop([i])

#Fill missing balance values with the average balance
df["Balance"] = df["Balance"].fillna(df["Balance"].mean())

#Add a column "Balance Amount" which describes the relevant amount of each customer's balance
def percentile(balance):
    if balance <= df["Balance"].describe()["25%"]:
        return "Very Low"
    elif balance > df["Balance"].describe()["25%"] and balance <= df["Balance"].describe()["50%"]:
        return "Low"
    elif balance > df["Balance"].describe()["50%"] and balance <= df["Balance"].describe()["75%"]:
        return "High"
    else:
        return "Very High"
df["Balance Amount"] = df["Balance"].apply(lambda x: percentile(x))

#Join table with branch data
df = df.merge(dfb)

#Load to new CSV file
df.to_csv('transformed.csv', index=False)