from flask import Flask, render_template, request
import pandas as pd
from numpy import arange
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import urllib

app = Flask(__name__)

def filter_by_city(city):
    if city == "chicago":
        data = chicago
    elif city == "new york city":
        data = new_york_city
    elif city == "washington dc":
        data = washington
    else:
        data = pd.concat([chicago, new_york_city, washington], join='outer', ignore_index=True)
    return data

def filter_by_month(data, month):
    months_to_number = {"january":1, "february":2, "march":3, "april":4,
    "may":5,"june":6}

    #create bool mask to know which rows of the data are the desired month
    start_mask = data["Start Time"].map(lambda x: x.month) == months_to_number[month]
    end_mask = data["End Time"].map(lambda x: x.month) == months_to_number[month]
    month_mask = [any(tup) for tup in zip(start_mask, end_mask)]
    data = data.loc[month_mask]
    return data

def filter_by_day(data, day):
    #create another bool mask for day
    start_mask = data["Start Time"].map(lambda x: x.day) == int(day)
    end_mask = data["End Time"].map(lambda x: x.day) == int(day)
    day_mask = [any(tup) for tup in zip(start_mask, end_mask)]
    data = data.loc[day_mask]
    return data

def collect_data_metrics(data, data_metrics):
    data_metrics["total trips"] = data.shape[0]
    data_metrics["total hours"] = round(data["Trip Duration"].sum()/3600, 1) #trip duration is in seconds
    data_metrics["average minutes per trip"] = round((data["Trip Duration"].sum()/60)/data_metrics["total trips"], 0)
    data_metrics["most popular start station"] = data["Start Station"].mode()[0]
    data_metrics["most popular end station"] = data["End Station"].mode()[0]
    data_metrics["most popular trip"] = data["Start Station"].str.cat(data["End Station"], sep=" to ").mode()[0]
    data_metrics["number subscribers"] = data[data["User Type"] == "Subscriber"]["User Type"].count()
    data_metrics["number customers"] = data[data["User Type"] == "Customer"]["User Type"].count()
    if "Gender" in data.columns:
        data_metrics["number males"] = data[data["Gender"] == "Male"]["User Type"].count()
        data_metrics["number females"] = data[data["Gender"] == "Female"]["User Type"].count()
        data_metrics["percent reporting gender"] = round((data_metrics["number males"] + data_metrics["number females"])/data_metrics["total trips"]*100, 2)
    if "Birth Year" in data.columns:
        data_metrics["most popular birth year"] = int(data["Birth Year"].mode()[0])
        data_metrics["average birth year"] = int(data["Birth Year"].mean())
    return data_metrics

#create a histogram to be passed to index.html - following example in this gist: https://gist.github.com/tebeka/5426211
#and this stackoverflow answer: https://stackoverflow.com/questions/44091516/passing-a-plot-from-matpotlib-to-a-flask-view
def create_histogram(hist_data):
    fig = plt.figure()
    figure_bins = arange(25)
    plt.hist(hist_data, bins=figure_bins)
    plt.title("Hourly rentals for selected data")
    plt.xlabel("hour (in military time)")
    plt.ylabel("number of rentals")
    img = BytesIO() #create buffer
    fig.savefig(img, format='png') #save figure to the buffer
    img.seek(0) #rewind the buffer
    plot = urllib.parse.quote(base64.b64encode(img.read()).decode()) #base64 encode and URL-escape
    return plot

@app.route("/", methods=["GET", "POST"])
def bikeshare():
    data_metrics = {} #need to declare these as empty b/c first request is "GET", but these still get passed to index.html
    plot = None
    if request.form: #makes sure it is a "POST" request and prevents 400 error
        city = request.form['city']
        month = request.form['month']
        day = request.form['day']

        #filter data by city
        data = filter_by_city(city)

        #convert start and end times to Timestamp
        data["Start Time"] = data["Start Time"].apply(lambda x: pd.Timestamp(x))
        data["End Time"] = data["End Time"].apply(lambda x: pd.Timestamp(x))

        #filter data by month (data is only first 6 months of year)
        if month != "all":
            data = filter_by_month(data, month)

        #filter by day of the month
        if day != "all":
            data = filter_by_day(data, day)

        #collect data metrics
        data_metrics['city'] = city
        data_metrics['month'] = month
        data_metrics['day'] = day
        if day != "all":
            data_metrics['day of the week'] = data.loc[data.index[0], "Start Time"].weekday_name
        data_metrics = collect_data_metrics(data, data_metrics)

        #create histogram of the number of rentals by hour of the day
        num_rentals_by_hour = pd.Series(data["Start Time"].map(lambda x: x.hour))
        plot = create_histogram(num_rentals_by_hour)

    return render_template("index.html", data_metrics=data_metrics, plot=plot)

if __name__ == '__main__':
    chicago = pd.read_csv("chicago.csv")
    new_york_city = pd.read_csv("new_york_city.csv")
    washington = pd.read_csv("washington.csv")

    app.run()
