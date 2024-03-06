import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sim_parameters
import helper
import datetime

class Run():
    def __init__(self,countries_csv_name, countries, sample_ratio, start_date, end_date):
        self.df = countries_csv_name
        self.countries = countries
        self.startDate = pd.to_datetime(start_date)
        self.endDate = pd.to_datetime(end_date)
        self.sampleRatio = sample_ratio
        self.samples = {}
        self.data = 0 
        self.summaryData = 0
    def createSamplePop(self):
        samples = {}
        df = self.df
        sampleratio = self.sampleRatio
        for i in range(df.shape[0]):
            country = df.iloc[i]['country']
            samplePop = int(df.iloc[i]['population']/sampleratio)
            less_5 = samplePop*df.iloc[i]['less_5']/100
            in5_to_14 = samplePop*df.iloc[i]['5_to_14']/100
            in15_to_24 = samplePop*df.iloc[i]['15_to_24']/100
            in25_to_64 = samplePop*df.iloc[i]['25_to_64']/100
            over_65 = samplePop*df.iloc[i]['over_65']/100

            if samples.get(country) is None:
                samples[country] = {
                    'less_5' : int(less_5),
                    '5_to_14' : int(in5_to_14),
                    '15_to_24' : int(in15_to_24),
                    '25_to_64' : int(in25_to_64),
                    'over_65' : int(over_65)
                }
        self.samples = samples
        
    
    def timeSeries(self):
        data = []
        for country in self.countries:
            person_id = 0
            for key, val in self.samples[country].items():
                for _ in range(val):
                    date = self.startDate
                    mc = MarkovChain(sim_parameters.TRASITION_PROBS, sim_parameters.HOLDING_TIMES,key)
                    while date <= self.endDate:
                        curr_state = mc.current_state()
                        stay_days = sim_parameters.HOLDING_TIMES[key][curr_state] 
                        if stay_days == 0:
                            data.append([person_id,key,country,date,0,curr_state])
                            date += datetime.timedelta(days=1)
                            mc.next_state()
                        else:
                            for x in range(1,1+stay_days):
                                if date > self.endDate:
                                    break
                                data.append([person_id,key,country,date,x,curr_state])
                                date += datetime.timedelta(days=1)
                            mc.next_state()
                    person_id += 1  
        return data
    
    def getTimeSeries(self):
        data = self.timeSeries()
        # print(self.data)
        temp = pd.DataFrame(data, columns=['person_id','age_group_name','country', 'date', 'staying_days','state'])
        # self.data = temp
        self.data = temp
        
    def summary(self):
        summary_data = []
        print(self.data)
        date = self.startDate
        while date <= self.endDate:
            for i in self.countries:
                dummy = self.data[self.data['date'] == date]
                states = dummy[dummy['country'] == i]['state'].value_counts()
                D = 0
                H = 0
                I = 0
                M = 0
                S = 0
                for x in states.index:
                    if x == 'H':
                         H = states[x]
                    elif x == 'D':
                         D = states[x]
                    elif x == 'I':
                         I = states[x]
                    elif x == 'M':
                         M = states[x]
                    elif x == 'S':
                         S = states[x]
                    
                summary_data.append([date,i,D,H,I,M,S])
            date += datetime.timedelta(days=1)
               
        temp = pd.DataFrame(summary_data, columns=['date', 'country', 'D', 'H', 'I', 'M', 'S'])
        self.summaryData = temp
        
    def saveTimeseries(self, filename):
        self.data.to_csv(filename)
    def saveSummary(self, filename):
        self.summaryData.to_csv(filename)
        
        
class MarkovChain:
    def __init__(self, transition_probabilities, holding_times, age_group):
        self.transtion_probabilities = transition_probabilities
        self.time_for_holding = holding_times
        self.age_group = age_group
        for i in transition_probabilities:
            
            self.probabilities_list = self.transtion_probabilities[i]

            sum_of_values = 0

            for j in self.probabilities_list:
                sum_of_values=sum(self.probabilities_list[j].values())
            if sum_of_values != 1:
                raise RuntimeError("The probabilities do not sum to 1")
        self.initial_state = "H"
        self.time= 0

    def get_states(self):
        return self.transtion_probabilities[self.age_group].keys()

    def current_state(self):
        return self.initial_state

    def set_state(self, new_state):
        self.initial_state = new_state
        self.time= 0

    def current_state_remaining_hours(self):
        time_curr = self.time_for_holding[self.age_group][self.initial_state]

        time = self.time
        return time_curr - time

    def next_state(self):
        
        random_state = np.random.choice(list(self.transtion_probabilities[self.age_group][self.initial_state].keys()), p=list(self.transtion_probabilities[self.age_group][self.initial_state].values()))


        self.set_state(random_state)

    def iterable(self):
        while 1:
            yield self.current_state()
    def simulate(self, hours):
        temp = {}
        temp=self.transtion_probabilities
        temp=dict.fromkeys(temp,0)
        for i in range(hours):
            curr_state = self.initial_weather
            self.time+= 1

            # get the next state
            nxt_state = self.next_state()
            if(curr_state != nxt_state):
                temp[curr_state] += 1

        lst = []
        for i in temp:
            tmp = temp[i]
            lst.append((tmp/hours)*100)
        return lst

    
    
def run(countries_csv_name, countries, sample_ratio, start_date, end_date):
    df = pd.read_csv(countries_csv_name)
    simulator = Run(df,countries,sample_ratio,start_date, end_date)
    simulator.createSamplePop()
    simulator.getTimeSeries()
    simulator.summary()
    simulator.saveTimeseries('a3-covid-simulated-timeseries.csv')
    simulator.saveSummary('a3-covid-summary-timeseries.csv')
    helper.create_plot('a3-covid-summary-timeseries.csv', countries)