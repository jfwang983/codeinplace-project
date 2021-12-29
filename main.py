import os
import tkinter as tk

class Data:
    provinces = {}

    def __init__(self, file):
        self.provinces = {}
        for line in file:
            self.raw_file = file
            info = line.split(",")
            if info[0] != "Province_State" and info[0] != "Recovered":
                self.provinces[info[0]] = Information(info)


class Information:
    def __init__(self, data):
        self.raw_data = data
        self.province = data[0]
        self.total_cases = self.get_data(data[5])
        self.total_deaths = self.get_data(data[6])
        self.current_cases = self.get_data(data[8])
        self.total_tested = self.get_data(data[11])

    def get_data(self, info):
        if info == "":
            return "No data"
        else:
            return float(info)

    def display(self):
        return str(self.province) + " -\nTotal Cases: " + str(self.total_cases) + "\nCurrent Cases: " + str(
            self.current_cases) + "\nTotal Deaths: " + str(self.total_deaths) + "\nTotal Tested: " + str(
            self.total_tested) + "\n"


class Date:
    def __init__(self, file):
        name = str(file.name[31:41])
        self.data = Data(file)
        self.month = int(name[0:2])
        self.day = int(name[3:5])
        self.year = int(name[6:10])

    def compare_to(self, date):
        if self.year != date.year:
            return self.year - date.year
        elif self.month != date.month:
            return self.month - date.month
        else:
            return self.day - date.day

    def display(self):
        return str(self.month) + "/" + str(self.day) + "/" + str(self.year)


class Collector:
    dates = {}
    recent_averages = {}

    def __init__(self):
        count = 0
        directory = "csse_covid_19_daily_reports_us"
        for filename in os.listdir(directory):
            self.dates[count] = Date(open(os.path.join(directory, filename)))
            count = count + 1
        self.chronological_sort()

    def chronological_sort(self):
        for i in range(len(self.dates.keys())):
            for j in range(len(self.dates.keys())):
                if self.dates[j].compare_to(self.dates[i]) > 0:
                    temp = self.dates[j]
                    self.dates[j] = self.dates[i]
                    self.dates[i] = temp

    def get_recent_averages(self):
        provinces = self.dates[1].data.provinces
        days_in_advance = 14
        start_index = len(self.dates.keys()) - days_in_advance - 1
        average = 0.0
        for i in provinces.keys():
            average = 0.0
            for j in range(days_in_advance):
                average = average + (self.dates[start_index + j + 1].data.provinces[i].total_cases - self.dates[start_index + j].data.provinces[i].total_cases)
            self.recent_averages[i] = average/days_in_advance
        with open("statedata.txt","r") as file:
            for line in file:
                list_line = line.split(",")
                # units = average proportion of people per square mile that have covid
                self.recent_averages[list_line[0]] = self.recent_averages[list_line[0]]/float(list_line[1])
        for i in self.recent_averages.keys():
            average = average + self.recent_averages[i]
        average = average/(len(self.recent_averages.keys()))
        return average


class Gui:
    def __init__(self):
        window = tk.Tk()
        window.geometry("1000x300")
        window.title("CovidCompare")
        # Input Frame Set-up
        self.input_frame = tk.Frame(borderwidth=3)
        self.input_frame.pack()
        question_label = tk.Label(master=self.input_frame, text="Enter U.S. State/Province:")
        state_entry = tk.Entry(master=self.input_frame, width=50)
        question_label.grid(row=0, column=0, sticky="e")
        state_entry.grid(row=0, column=1)
        # Option Frame Set-up
        self.option_frame = tk.Frame()
        self.option_frame.pack(fill=tk.X, ipadx=5, ipady=5)
        submit_button = tk.Button(master=self.option_frame, text="Display Data", command=self.submit)
        submit_button.pack(padx=10, ipadx=10)
        # Error Frame Set-up
        self.error_frame = tk.Frame(borderwidth=3)
        self.error_frame.pack()
        error_label = tk.Label(master=self.error_frame, fg="red", text="")
        error_label.grid(row=0, column=0, sticky="e")
        # Comparer Frame Set-up
        self.compare_frame = tk.Frame(borderwidth=3)
        self.compare_frame.pack()
        compare_label = tk.Label(master=self.compare_frame, text="")
        recommendation_label = tk.Label(master=self.compare_frame, text="")
        compare_label.grid(row=0, column=0, sticky="e")
        recommendation_label.grid(row=1, column=0, sticky="e")
        self.state = state_entry
        self.error = error_label
        self.compare = compare_label
        self.recommendation = recommendation_label
        self.collector = Collector()
        window.mainloop()

    def submit(self):
        provinces = self.collector.dates[1].data.provinces
        state_value = self.state.get()
        input_valid = True
        try:
            provinces[state_value]
            self.error["text"] = ""
        except Exception:
            input_valid = False
            self.error["text"] = "Error: \"" + state_value + "\" is not a valid State/Province"
            self.compare["text"] = ""
            self.recommendation["text"] = ""
        if input_valid:
            recent_average = self.collector.get_recent_averages()
            status = ""
            recommendation = ""
            if recent_average == self.collector.recent_averages[state_value]:
                status = "Status: These past two weeks, " + state_value + "\'s average proportion of people with COVID-19 per square mile is equal to the nationwide average."
                recommendation = "Recommendation: Based on this trend, I think that you can safely pursue normal activities (without large crowds)."
            elif recent_average < self.collector.recent_averages[state_value]:
                status = "Status: These past two weeks, " + state_value + "\'s average proportion of people with COVID-19 per square mile is greater than the nationwide average."
                recommendation = "Recommendation: Based on this trend, I think that you would remain alert and slightly cut back on non-essential activities."
            else:
                status = "Status: These past two weeks, " + state_value + "\'s average proportion of people with COVID-19 per square mile is less than the nationwide average."
                recommendation = "Recommendation: Based on this trend, I think that you can safely pursue normal activities (without large crowds)."
            self.compare["text"] = status
            self.recommendation["text"] = recommendation


gui = Gui()