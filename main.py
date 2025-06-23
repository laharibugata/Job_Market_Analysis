from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import webbrowser

def get_database():
    CONNECTION_STRING = "mongodb+srv://username:password@cluster0.37lvyjg.mongodb.net/"
    client = MongoClient(CONNECTION_STRING)
    return client

def get_dataframe(collection):
    cursor = collection.find()
    return pd.DataFrame(list(cursor))

if __name__ == '__main__':
    dbname = get_database()
    # print(dbname)
    collection = dbname['LinkedIn']
    files = collection.list_collection_names()

    job_skills = get_dataframe(collection['job_skills'])
    job_industries = get_dataframe(collection['job_industries'])
    company_industries = get_dataframe(collection['company_industries'])
    job_postings = get_dataframe(collection['job_postings'])
    companies = get_dataframe(collection['companies'])
    benefits = get_dataframe(collection['benefits'])
    company_specialities = get_dataframe(collection['company_specialities'])
    employee_counts = get_dataframe(collection['employee_counts'])

    # Analyzing the job market
    jp = job_postings[
        ['job_id', 'company_id', 'location', 'formatted_experience_level', 'max_salary', 'med_salary', 'min_salary',
         'formatted_experience_level']]
    # years = np.random.choice([2021, 2022, 2023], size=len(jp))
    # np.random.seed(42)
    jp = jp.copy()
    jp.loc[:, 'year'] = np.random.choice([2021, 2022, 2023], size=len(jp))
    jp['company_id'].fillna(0, inplace=True)
    jp['company_id'] = jp['company_id'].apply(np.int64)
    # preview the df
    jp = jp.loc[:, ~jp.columns.duplicated()]
    #jp

    jp['max_salary'] = job_postings['max_salary'].fillna(
        job_postings.groupby('formatted_experience_level')['max_salary'].transform('mean')
    )

    jp['med_salary'] = job_postings['med_salary'].fillna(
        job_postings.groupby('formatted_experience_level')['med_salary'].transform('mean')
    )

    jp['min_salary'] = job_postings['min_salary'].fillna(
        job_postings.groupby('formatted_experience_level')['min_salary'].transform('mean')
    )

    jp['salary'] = jp[['max_salary', 'med_salary', 'min_salary']].mean(axis=1)

    jp = pd.merge(jp, company_industries, on='company_id')

    jp = jp.drop(columns=['_id'])

    jp1 = jp.head(20).copy()

    # 1. Salary distributions across job categories and locales
    plt.figure(figsize=(12, 6))
    sns.boxplot(x='industry', y='salary', hue='location', data=jp1)
    plt.title('Salary Distribution Across Job Categories and Locales')
    plt.xticks(rotation=45)
    plt.savefig('/Users/bhaskarpramodchennupalli/Documents/DBMS Project/SalDistJob_1.png')
    #plt.show()

    # 2. Analyze salary differences with experience

    plt.figure(figsize=(12, 6))
    sns.lineplot(x='formatted_experience_level', y='salary', hue='industry', data=jp)
    plt.title('Salary Differences with Experience')
    plt.savefig('/Users/bhaskarpramodchennupalli/Documents/DBMS Project/SalDistJob_2.png')
    #plt.show()

    # 3. Determine trends in salary increase over time
    plt.figure(figsize=(12, 6))
    sns.lineplot(x='year', y='salary', hue='industry', data=jp)
    plt.title('Trends in Salary Increase Over Time')
    plt.savefig('/Users/bhaskarpramodchennupalli/Documents/DBMS Project/SalDistJob_3.png')
    #plt.show()

    # Explore the distribution of job roles
    companies_count = jp.groupby('company_id').size().reset_index(name='count')
    companies_count = pd.merge(companies_count, companies[['company_id', 'name']], on='company_id')
    companies_count = companies_count.sort_values('count', ascending=False)
    top_companies_count = companies_count.head(10).copy()
    plt.figure(figsize=(12, 6))
    # Assuming 'name' is the column you want to count
    # companies_counts = companies_count['name'].value_counts().nlargest(10)
    sns.barplot(x=top_companies_count['name'], y=top_companies_count['count'], palette='viridis')
    plt.title('Top 10 In-Demand Companies')
    plt.xlabel('Company')
    plt.ylabel('Number of Job Postings')
    plt.savefig('/Users/bhaskarpramodchennupalli/Documents/DBMS Project/SalDistJob_4.png')
    #plt.show()

    # Explore the geographic distribution of job postings
    companies_avg_salary = jp.groupby('company_id').agg({'salary': 'mean'}).reset_index()
    companies_avg_salary = pd.merge(companies_avg_salary, companies[['company_id', 'name']], on='company_id')
    companies_avg_salary = companies_avg_salary.sort_values(['salary'], ascending=False)
    company_avg_salary = companies_avg_salary.head(10).copy()
    # Explore the geographic distribution of job postings
    plt.figure(figsize=(12, 6))
    # companies_industries = companies_industry['name'].value_counts().nlargest(10)  # Display top 10 locations
    sns.barplot(x=company_avg_salary.name, y=company_avg_salary.salary, palette='plasma')
    plt.title('Top 10 Average Salary')
    plt.xlabel('Company')
    plt.ylabel('Average Salary')
    plt.xticks(rotation=45)
    plt.savefig('/Users/bhaskarpramodchennupalli/Documents/DBMS Project/SalDistJob_5.png')
    #plt.show()

    # Explore the distribution of industries
    plt.figure(figsize=(12, 6))
    industry_counts = jp['industry'].value_counts().nlargest(10)  # Display top 10 industries
    sns.barplot(x=industry_counts.values, y=industry_counts.index, palette='magma')
    plt.title('Top 10 Industries with Most Job Postings')
    plt.xlabel('Number of Job Postings')
    plt.ylabel('Industry')
    plt.savefig('/Users/bhaskarpramodchennupalli/Documents/DBMS Project/SalDistJob_6.png')
    #plt.show()

    company_details = jp['company_id'].value_counts().nlargest(10)  # Display top 10 companies
    #print(company_details)

    company_count = jp.groupby('company_id').size().reset_index(name='total_job_postings')

    company_count = pd.merge(company_count, companies[['company_id', 'name']], on='company_id')

    salaries_count = pd.merge(company_count, jp[['company_id', 'salary']], on='company_id')

    salaries_count = salaries_count.sort_values(by='salary', ascending=False)

    salaries_count.drop_duplicates(subset=['company_id'], inplace=True)

    salaries_count = salaries_count.head(10).copy()

    # Assess the size distribution of companies

    plt.figure(figsize=(10, 6))
    sns.barplot(x='name', y='salary', data=salaries_count, palette='Set2')
    plt.title('Companies with Highest Salary')
    plt.xlabel('Company Name')
    plt.ylabel('Highest Salary')
    plt.xticks(rotation=45)
    plt.savefig('/Users/bhaskarpramodchennupalli/Documents/DBMS Project/SalDistJob_7.png')
    #plt.show()

    # Identify top industries
    plt.figure(figsize=(12, 6))
    top_industries = jp['salary'].value_counts().nlargest(10)  # Display top 10 industries
    sns.barplot(x=top_industries.values, y=top_industries.index, palette='coolwarm')
    plt.title('Top 10 Salaries with Most Job Postings')
    plt.xlabel('Number of Job Postings')
    plt.ylabel('Salary')
    plt.savefig('/Users/bhaskarpramodchennupalli/Documents/DBMS Project/SalDistJob_8.png')
    #plt.show()

    salary_location = pd.merge(company_count, jp[['company_id', 'location', 'salary']], on='company_id')

    salary_location.drop_duplicates(subset=['company_id'], inplace=True)

    salary_location['salary'] = pd.to_numeric(salary_location['salary'], errors='coerce')

    avg_salary_location = salary_location.groupby('location')['salary'].mean().reset_index()

    avg_salary_location = avg_salary_location.head(10).copy()

    plt.figure(figsize=(12, 6))
    # geo_distribution = jp['salary'].value_counts().nlargest(10)  # Display top 10 locations
    sns.barplot(x=avg_salary_location.location, y=avg_salary_location.salary, palette='viridis')
    plt.title('Top 10 Locations with Avg Salary')
    plt.xlabel('Average Salary')
    plt.ylabel('Location')
    plt.xticks(rotation=45)
    plt.savefig('/Users/bhaskarpramodchennupalli/Documents/DBMS Project/SalDistJob_9.png')
    #plt.show()

    preferred_industry = input("Enter your preferred industry: ")
    preferred_location = input("Enter your preferred location: ")
    preferred_salary = float(input("Enter your preferred salary: ") or "0.00")

    job_recommendations = pd.merge(jp[['job_id', 'company_id', 'location', 'salary', 'industry']],
                                   companies[['company_id', 'name']], on='company_id')

    filtered_companies = job_recommendations[
        # (job_recommendations['industry'] == preferred_job_role) &
        # (job_recommendations['location'] == preferred_location) &
        (job_recommendations['salary'] >= preferred_salary)
    ]

    if preferred_industry != '':
        filtered_companies = filtered_companies[
            (job_recommendations['industry'] == preferred_industry)
        ]

    if preferred_location != '':
        filtered_companies = filtered_companies[
            (job_recommendations['location'] == preferred_location)
        ]

    ranked_companies = filtered_companies.sort_values(by='salary', ascending=False)

    ranked_companies.drop_duplicates(subset=['job_id'], inplace=True)

    top_ranked_companies = ranked_companies[['salary', 'name']].copy()

    top_ranked_companies.drop_duplicates(subset=['name'], inplace=True)

    plt.figure(figsize=(10, 6))
    plt.bar(top_ranked_companies['name'][:5], top_ranked_companies['salary'][:5], color='blue')
    plt.xlabel('Company')
    plt.ylabel('Salary')
    plt.title('Top 5 Companies for Preferred Job Role')
    plt.xticks(rotation=45)
    plt.savefig('/Users/bhaskarpramodchennupalli/Documents/DBMS Project/SalDistJob_10.png')
    #plt.show()

    webbrowser.open('file:///Users/bhaskarpramodchennupalli/Documents/DBMS Project/index.html')
    #print('/Users/bhaskarpramodchennupalli/Documents/DBMS Project/index.html')


