from flask import Flask, render_template, request
#from pyfladesk import init_gui
import pandas as pd

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def bikeshare():
    data_metrics = {}
    if request.form: #makes sure it is a "POST" request and prevents 400 error
        city = request.form['city']
        month = request.form['month']
        day = request.form['day']

        #filter data by city
        if city == "chicago":
            data = chicago
        elif city == "new york city":
            data = new_york_city
        elif city == "washington dc":
            data = washington
        else:
            data = pd.concat([chicago, new_york_city, washington], join='outer', ignore_index=True)

        #convert start and end times to Timestamp
        data["Start Time"] = data["Start Time"].apply(lambda x: pd.Timestamp(x))
        data["End Time"] = data["End Time"].apply(lambda x: pd.Timestamp(x))

        #filter data by month (data is only first 6 months of year)
        if month != "all":
            months_to_number = {"january":1, "february":2, "march":3, "april":4,
            "may":5,"june":6}

            #create bool mask to know which rows of the data are the desired month
            start_mask = data["Start Time"].map(lambda x: x.month) == months_to_number[month]
            end_mask = data["End Time"].map(lambda x: x.month) == months_to_number[month]
            month_mask = [any(tup) for tup in zip(start_mask, end_mask)]
            data = data.loc[month_mask]

        #filter by day of the month
        if day != "all":
            #create another bool mask for day
            start_mask = data["Start Time"].map(lambda x: x.day) == int(day)
            end_mask = data["End Time"].map(lambda x: x.day) == int(day)
            day_mask = [any(tup) for tup in zip(start_mask, end_mask)]
            data = data.loc[day_mask]

        #collect data metrics
        data_metrics['city'] = city
        data_metrics['month'] = month
        data_metrics['day'] = day
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

    return render_template("index.html", data_metrics=data_metrics)

if __name__ == '__main__':
    chicago = pd.read_csv("chicago.csv")
    new_york_city = pd.read_csv("new_york_city.csv")
    washington = pd.read_csv("washington.csv")
    #init_gui(app)

    app.run(debug=True)
