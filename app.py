import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.figure_factory as ff
import plotly.graph_objs as go

# Import Data
df = pd.read_csv("athlete_events.csv")
region_df = pd.read_csv("noc_regions.csv")

# Preprocess df
def preprocess():
    global df,region_df
    # filtering for summer olympics
    df = df[df["Season"]=="Summer"]
    #merge with region_df
    df = df.merge(region_df,on= "NOC",how = "left")
    # dropping duplicates
    df.drop_duplicates(inplace = True)
    # OHE medals
    df = pd.concat([df,pd.get_dummies(df["Medal"])],axis = 1)
    return df

df = pd.read_csv("athlete_events.csv")
region_df = pd.read_csv("noc_regions.csv")
df = preprocess()

def participating_nations_over_time(df):
    nations_over_time = df.drop_duplicates(["Year", "region"])["Year"].value_counts().reset_index().sort_values("Year")
    nations_over_time.rename(columns={"Year": "Edition"}, inplace=True)
    fig = px.line(nations_over_time, x="Edition", y="count")
    return fig

def athletes_over_year(df):
    year = df["Year"].sort_values().unique()
    events = []
    for i in year:
        a = df[df["Year"] == i]["Name"].unique().shape[0]
        events.append(a)
    fig = px.line( x = year,y  = events,labels={"x": "Edition", "y": "Number of Athletes"})
    return fig

def year_wise_medal_tally(df,country):
    temp_df = df.dropna(subset = ["Medal"])
    temp_df.drop_duplicates(subset = ["Team","NOC","Games","Year","City","Sport","Event","Medal"],inplace = True)
    new_df = temp_df[temp_df["region"]==country]
    final_df = new_df.groupby("Year").count()["Medal"].reset_index()
    fig  = px.line(final_df,x = "Year",y = "Medal")
    return fig,final_df
def events_over_year(df):
    year = df["Year"].sort_values().unique()
    events = []
    for i in year:
        a = df[df["Year"] == i]["Event"].unique().shape[0]
        events.append(a)
    fig = px.line( x = year,y  = events,labels={"x": "Edition", "y": "Number of Events"})
    return fig

def weight_v_height(df,sport):
    athlete_df = df.drop_duplicates(subset=["Name", "region"])
    athlete_df["Medal"].fillna("No Medal", inplace=True)
    if sport != "Overall":
        temp_df = athlete_df[athlete_df["Sport"] == sport]
        return temp_df
    else:
        return athlete_df
def most_successful(df,sport):
    temp_df = df.dropna(subset =["Medal"])
    if sport != "Overall":
        temp_df = temp_df[temp_df["Sport"]==sport]
    return temp_df["Name"].value_counts().reset_index().head(15).merge(df,on = "Name").drop_duplicates("Name")[["Name","count","Sport","region"]].reset_index(drop =True).rename(columns = {"count":"Total Medal Won"})

def medal_tally(df):
    medal_tally = df.drop_duplicates(subset=["Team", "NOC", "Games", "City", "Sport", "Event", "Medal"])
    medal_tally = medal_tally.groupby("NOC").sum()[["Gold", "Silver", "Bronze"]].sort_values("Gold",
                                                                                             ascending=False).reset_index()
    medal_tally["total"] = medal_tally["Gold"] + medal_tally["Silver"] + medal_tally["Bronze"]
    return medal_tally

def country_year_list(df):

    years = df["Year"].unique().tolist()
    years.sort()

    years.insert(0, "Overall")

    country = np.unique(df["region"].dropna().values).tolist()
    country.sort()
    country.insert(0, "Overall")
    return years, country

def country_most_successful(df, country):
    temp_df = df.dropna(subset=["Medal"])

    temp_df = temp_df[temp_df["region"] == country]
    return temp_df["Name"].value_counts().reset_index().head(10).merge(df, on="Name").drop_duplicates("Name")[
        ["Name", "count", "Sport"]].reset_index(drop = True)
def country_event_heatmap(df,country):
    temp_df = df.dropna(subset=["Medal"])
    temp_df.drop_duplicates(subset=["Team", "NOC", "Games", "Year", "City", "Sport", "Event", "Medal"], inplace=True)
    new_df = temp_df[temp_df["region"] == country]
    pt = new_df.pivot_table(index="Sport", columns="Year", values="Medal", aggfunc="count").fillna(0).astype(int)
    return pt
def fetch_medal_tally(df,year,country):
    medal_df = df.drop_duplicates(subset= ["Team","NOC","Games","City","Sport","Event","Medal"])
    flag = 0
    if year == "Overall" and country == "Overall":
        temp_df = medal_df
    if year == "Overall" and country != "Overall":
        flag = 1
        temp_df = medal_df[medal_df["region"] == country]
    if year != "Overall" and country == "Overall":
        temp_df = medal_df[medal_df["Year"] == year]
    if year != "Overall" and country != "Overall":
        temp_df = medal_df[(medal_df["Year"] == year) & (medal_df["region"] == country)]
    if flag == 1:
        x = temp_df.groupby("Year").sum()[["Gold","Silver","Bronze"]].sort_values("Year",ascending = True).reset_index()
    else:
        x = temp_df.groupby("region").sum()[["Gold","Silver","Bronze"]].sort_values("Gold",ascending = False).reset_index()
    x["total"] = x["Gold"]+x["Silver"]+x["Bronze"]
    return pd.DataFrame(x)



st.sidebar.title("OLYMPIC ANALYSIS")
st.sidebar.image("https://tse4.mm.bing.net/th?id=OIP.AL2we6lSVRsooRq5XPpK8QAAAA&pid=Api&P=0&h=180")
user_menu  = st.sidebar.radio(
    "Select an option",
    ("Medal Tally","Overall Analysis","Country wise Analysis","Athlete wise Analysis")
)

if user_menu == "Medal Tally":
    st.sidebar.header("Medal Tally")
    years,country = country_year_list(df)
    selected_year = st.sidebar.selectbox("Select Year",years)
    selected_country = st.sidebar.selectbox("Select Country", country)
    medal_tally = fetch_medal_tally(df,selected_year,selected_country)
    if selected_year == "Overall" and selected_country == "Overall":
        st.title("Overall Tally")
    if selected_year != "Overall" and selected_country == "Overall":
        st.title(f"Overall Tally in {selected_year}")
    if selected_year == "Overall" and selected_country != "Overall":
        st.title(f"{selected_country.upper()} Overall Performance")
    if selected_year != "Overall" and selected_country != "Overall":
        st.title(f"{selected_country.upper()} performance in {selected_year}'s Olympics")
    st.table(medal_tally)


if user_menu == "Overall Analysis":
    editions =df["Year"].unique().shape[0]-1
    cities =df["City"].unique().shape[0]
    sports =df["Sport"].unique().shape[0]
    events =df["Event"].unique().shape[0]
    athletes =df["Name"].unique().shape[0]
    nations =df["region"].unique().shape[0]
    col1, col2, col3 = st.columns(3)
    with col1:
        st.header("Editions")
        st.title(editions)
    with col2:
        st.header("Hosts")
        st.title(cities)
    with col3:
        st.header("Sports")
        st.title(sports)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.header("Events")
        st.title(events)
    with col2:
        st.header("Nations")
        st.title(nations)
    with col3:
        st.header("Athletes")
        st.title(athletes)
    st.title("Participating nations over the years")
    st.plotly_chart(participating_nations_over_time(df))
    st.title("Events over the years")
    st.plotly_chart(events_over_year(df))
    st.title("Athletes over the years")
    st.plotly_chart(athletes_over_year(df))
    st.title("No of Events over time (Every Sport)")
    fig,ax = plt.subplots(figsize=(20,20))
    x = df.drop_duplicates(["Year", "Sport", "Event"])
    ax = sns.heatmap(x.pivot_table(index="Sport", columns="Year", values="Event", aggfunc="count").fillna(0).astype(int),
                annot=True)
    st.pyplot(fig)


    st.title("Most Successful Athletes")
    sport_list = df["Sport"].unique().tolist()
    sport_list.sort()
    sport_list.insert(0,"Overall")

    selected_sport  = st.selectbox("Select a Sport",sport_list)
    st.table(most_successful(df,selected_sport))

if user_menu == "Country wise Analysis":
    st.sidebar.title("Year wise Medal Tally")
    country_list = df["region"].dropna().unique().tolist()
    country_list.sort()
    selected_country = st.sidebar.selectbox("Select a Country",country_list)
    fig,table = year_wise_medal_tally(df,selected_country)
    st.header(f"{selected_country} Medal Tally over the years")
    st.table(table)
    st.plotly_chart(fig)

    st.title(f"{selected_country}'s Sports Heatmap")
    fig, ax = plt.subplots(figsize=(15, 15))
    ax = sns.heatmap(country_event_heatmap(df, selected_country),annot = True)
    st.pyplot(fig)

    st.title(f"Top 10 athletes of {selected_country}")
    st.table(country_most_successful(df, selected_country))

if user_menu == ("Athlete wise Analysis"):
    athlete_df = df.drop_duplicates(subset=["Name", "region"])
    x1 = athlete_df["Age"].dropna()
    x2 = athlete_df[athlete_df["Medal"] == "Gold"]["Age"].dropna()
    x3 = athlete_df[athlete_df["Medal"] == "Silver"]["Age"].dropna()
    x4 = athlete_df[athlete_df["Medal"] == "Bronze"]["Age"].dropna()
    fig = ff.create_distplot([x1, x2, x3, x4], ["Overall Age", "Gold Medalist", "Silver Medalist", "Bronze Medalist"],
                             show_hist=False, show_rug=False)
    fig.update_layout(autosize = False, width = 1000, height = 600)
    st.title("Distribution of Age")
    st.plotly_chart(fig)

    athlete_df = df.drop_duplicates(subset=["Name", "region"])

    x = []
    name = []

    famous_sports = ["Basketball", "Judo", "Football", "Tug-Of-War", "Athletics", "Swimming", "Badminton", "Sailing",
                     "Gymnastics", "Art Competitions", "Handball", "Weightlifting", "Wrestling", "Water Polo", "Hockey",
                     "Rowing", "Fencing", "Shooting", "Boxing", "Taekwondo", "Cycling", "Diving", "Canoeing", "Tennis",
                     "Golf", "Softball", "Archery", "Volleyball", "Synchronized Swimming", "Table Tennis", "Baseball",
                     "Rhythmic Gymnastics", "Rugby Sevens", "Beach Volleyball", "Triathlon", "Rugby", "Polo",
                     "Ice Hockey"]

    for sport in famous_sports:
        temp_df = athlete_df[athlete_df["Sport"] == sport]
        ages = temp_df[temp_df["Medal"] == "Gold"]["Age"].dropna().tolist()

        x.append(ages)
        name.append(sport)

    fig = ff.create_distplot(x, name,show_hist=False, show_rug=False)
    fig.update_layout(autosize=False, width=1000, height=600)
    st.title("Distribution of Age wrt Sports (Gold Medalist)")
    st.plotly_chart(fig)

    sport_list = df["Sport"].unique().tolist()
    sport_list.sort()
    sport_list.insert(0, "Overall")
    st.title("Height vs Weight")
    selected_sport = st.selectbox("Select a Sport", sport_list)
    temp_df = weight_v_height(df, selected_sport)
    fig,ax = plt.subplots()
    ax = sns.scatterplot(data = temp_df,x = "Weight",y = "Height",hue = "Medal",style = "Sex",s = 60)

    st.pyplot(fig)

    athlete_df2 = df.drop_duplicates(subset=["Name", "region", "Year"])
    men = athlete_df2[athlete_df2["Sex"] == "M"].groupby("Year").count()["Name"].reset_index()
    women = athlete_df2[athlete_df2["Sex"] == "F"].groupby("Year").count()["Name"].reset_index()
    final = men.merge(women,on = "Year",how = "left")
    final.fillna(0,inplace= True)

    final.rename(columns={"Name_x": "Male", "Name_y": "Female"}, inplace=True)
    fig = px.line(final, x="Year", y=["Male", "Female"])
    st.title("Men vs Women Participation Over the Years")
    st.plotly_chart(fig)


st.sidebar.image("https://t4.ftcdn.net/jpg/01/14/13/69/360_F_114136983_jUTScoeTJyXR6md5T3c4sINbuLT67D0g.jpg")

