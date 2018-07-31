import datetime
import csv
from datetime import timedelta
from copy import deepcopy
from operator import attrgetter
from functools import total_ordering


@total_ordering
class MinType(object):
    def __le__(self, other):
        return True

    def __eq__(self, other):
        return (self is other)

    def __repr__(self):
        return "Min"


@total_ordering
class MaxType(object):
    def __ge__(self, other):
        return True

    def __le__(self, other):
        return False

    def __eq__(self, other):
        return (self is other)

    def __repr__(self):
        return "Max"


Min = MinType()
Max = MaxType()


def is_weekday(day):
    '''
    One Input: datetime object
    Output: Returns True if the day passed as argument is a weekday
            or False if it's a weekend day.
    '''
    return day.weekday() < 5


def diffBtwDates(start_date, end_date):
    '''
    Calculate the difference (in days) between two dates
    Two inputs: string in the format 'YYYY-MM-DD'
    Output: Integer with the difference between the dates
    '''
    day_difference = datetime.datetime.strptime(end_date, '%Y-%m-%d').date() - \
        datetime.datetime.strptime(start_date, '%Y-%m-%d').date()

    return int(day_difference / datetime.timedelta(days=1))


def str_to_bool(s):
    '''
    Converts True & False strings into boolean
    Input: a string
    '''
    if s == 'True':
        return True
    elif s == 'False':
        return False
    else:
        raise ValueError


class Duty():
    '''
    Duty as a class
    '''
    dutiesDict = {}
    dutiesList = []
    dailyDuties = {}

    def __init__(self, name, armed):
        self.name = name
        self.armed = armed
        Duty.dutiesDict[self.name] = []
        Duty.dutiesList.append(self)

    def __repr__(self):
        return("{}".format(self.name))

    @classmethod
    def getDuties(cls, armed):
        '''
        Gets either armed or unarmed duties, depending on the input
        Input: a boolean
        Output: a list with duties
        '''
        return list(filter(lambda duty: duty.armed == armed, Duty.dutiesList))


class Soldier():
    '''
    A parent class that creates a soldier instance.
    '''
    soldier_counter = 0

    def __init__(self, first_name, last_name, mobile_phone, lastDuty=None):
        self.first_name = first_name
        self.last_name = last_name
        self.mobile_phone = mobile_phone
        self.dutiesDoneWeekdays = 0
        self.dutiesDoneWeekends = 0
        self.lastDuty = lastDuty
        self.daysSinceLastDuty = Max
        self.soldierDutiesList = deepcopy(Duty.dutiesDict)
        self.id = Soldier.soldier_counter
        Soldier.soldier_counter += 1

    # 'less than' magic method. Compares dutiesDone between two instances
    def __lt__(self, other):
        return self.dutiesDone < other.dutiesDone

    # Represent by print full name plus dutiesDone
    def __repr__(self):
        return("{} {} (Duties: {}, {} - Days: {} - Available: {})".format(self.last_name, self.first_name, self.dutiesDoneWeekdays, self.dutiesDoneWeekends, self.daysSinceLastDuty, self.available))

    @property
    def dutiesDone(self):
        '''
        Now I can use 'dutiesDone', that automatically returns either
        dutiesDoneWeekdays or dutiesDoneWeekends, dependind of whether it's
        weekday or not, instead of having to check everytime.
        '''
        self._dutiesDone = self.dutiesDoneWeekdays if is_weekday(
            todayObject) else self.dutiesDoneWeekends
        return self._dutiesDone


class Private(Soldier):
    '''
    A child class of Soldier that's specific for soldders with Private rank.
    '''
    # class lists
    allPrivates = []
    allArmedPrivates = []
    allUnarmedPrivates = []

    def __init__(self, first_name, last_name, mobile_phone, somatiki_ikanotita, armed, available=True):
        super().__init__(first_name, last_name, mobile_phone)
        self.somatiki_ikanotita = somatiki_ikanotita
        self.armed = armed
        self.available = available
        self.availableLeaves = {'Kanoniki': 15, 'Timitiki': 0}
        self.ableToDoduties = deepcopy(self.soldierDutiesList)
        self.tempUnableToDo = {}

        # Each Private instance is being append to a list based on the armed parameter
        if self.armed == True:
            Private.allArmedPrivates.append(self)
        else:
            Private.allUnarmedPrivates.append(self)

        # Append object to a generic list, containing both armed and unarmed privates
        Private.allPrivates.append(self)

    @classmethod
    def availablePrivates(self):
        return list(filter(lambda private: private.available == True, Private.allPrivates))

    @classmethod
    def sort(cls, some_list, attr):
        return sorted(some_list, key=attrgetter(attr))

    @classmethod
    def getPrivatesWithMinDuties(self, some_list):
        '''
        Input: a list with Private instances
        Output: a filterd and ordered list
        '''
        privatesList = Private.sort(some_list, 'dutiesDone')
        return list(filter(lambda private:
                           private.dutiesDone == privatesList[0].dutiesDone, privatesList))

    @classmethod
    def getPrivates(cls, some_list, armed):
        '''
        Get a sublist of privates, by passing a list of privates and a bool: if private is armed or not
        Two Inputs: a list and a boolean
        Output: One list with
        '''
        return list(filter(lambda private: private.armed == armed, some_list))

    @classmethod
    def getCandidatePrivates(cls, func):
        '''
        Generates two lists, one with armed and the other with unarmed privates,
        that've done the least duties, and therefore are candidates for duties
        Output: A tuple of two lists, each containing Private instances.
        '''
        # privates = Private.getPrivatesWithMinDuties(Private.availablePrivates())
        privates = func(Private.availablePrivates())
        availableUnarmedPrivates = Private.getPrivates(privates, False)
        # print(f"Unarmed candidates: {availableUnarmedPrivates}")  # for testing
        availableArmedPrivates = Private.getPrivates(privates, True)
        # print(f"Armed candidates: {availableArmedPrivates}")  # for testing
        return (availableArmedPrivates, availableUnarmedPrivates)

    @classmethod
    def calculateDaysPassed(cls):
        '''
        Calculate how many days have passed since each private had a duty
        '''
        for private in Private.availablePrivates():
            if private.lastDuty != None:
                day_difference = todayObject - \
                    datetime.datetime.strptime(private.lastDuty, '%Y-%m-%d').date()
                # day difference in days
                private.daysSinceLastDuty = int(day_difference / datetime.timedelta(days=1))
            else:
                private.daysSinceLastDuty = Max

    @classmethod
    def getPrivatesWithMostDays(cls, some_list):
        '''
        Input: a list with Private instances
        Output: a filterd and ordered list
        '''
        cls.calculateDaysPassed()
        privatesList = Private.sort(some_list, 'daysSinceLastDuty')
        return list(filter(lambda private:
                           private.daysSinceLastDuty == privatesList[-1].daysSinceLastDuty, privatesList))
        # return tempList

    def add_Duty(self, duty_name, date):
        '''
        Add a new duty to a private.
        Two Inputs: string with name of duty and string with date
        '''
        if is_weekday(todayObject):
            self.dutiesDoneWeekdays += 1
        else:
            self.dutiesDoneWeekends += 1

        self.lastDuty = date
        self.soldierDutiesList[duty_name].append(date)

    def add_leave(self, leave_type, start_date, end_date):
        '''
        3 Inputs: string with type of leave and two dates in form of 'YYYY-MM-DD'
        '''
        leaveDays = diffBtwDates(start_date, end_date)

        # Allow leave only if enough days of the specific leave type are available
        if self.availableLeaves[leave_type] > leaveDays:
            self.availableLeaves[leave_type] -= leaveDays

            # if there is no key for this date, create one and asign an empty list
            # so I append multiple privates to that date key
            if start_date not in LeavesCalculator.Departures.keys():
                LeavesCalculator.Departures[start_date] = []
            LeavesCalculator.Departures[start_date].append(self)

            if end_date not in LeavesCalculator.Arrivals.keys():
                LeavesCalculator.Arrivals[end_date] = []
            LeavesCalculator.Arrivals[end_date].append(self)
        else:
            print(f'Error!\n{self.availableLeaves[leave_name]} leave days left, while tried to get {leaveDays} days of leave.')

    def increase_available_leaves(self, leave_type, days_of_leave):
        '''
        Increases available days for a specific type of leave.
        It also creates the type of leave if it's not existed yet.
        2 Inputs: one string and one integer
        '''
        if leave_type not in self.availableLeaves.keys():
            self.availableLeaves[leave_type] = days_of_leave
        else:
            self.availableLeaves[leave_type] += days_of_leave

    def add_free_of_duty(self, free_type, start_date, days):
        end_date = (datetime.datetime.strptime(
            start_date, '%Y-%m-%d').date() + timedelta(days=days)).strftime('%Y-%m-%d')

        if free_type == 'ΕΥ':
            if start_date not in FreeOfDutyHandler.freeOfDutyStart.keys():
                FreeOfDutyHandler.freeOfDutyStart[start_date] = []
            FreeOfDutyHandler.freeOfDutyStart[start_date].append(self)

            if end_date not in FreeOfDutyHandler.freeOfDutyEnd.keys():
                FreeOfDutyHandler.freeOfDutyEnd[end_date] = []
            FreeOfDutyHandler.freeOfDutyEnd[end_date].append(self)

        elif free_type == 'ΕΟ':
            if start_date not in FreeOfDutyHandler.freeOfStandingStart.keys():
                FreeOfDutyHandler.freeOfStandingStart[start_date] = []
            FreeOfDutyHandler.freeOfStandingStart[start_date].append(self)

            if end_date not in FreeOfDutyHandler.freeOfStandingEnd.keys():
                FreeOfDutyHandler.freeOfStandingEnd[end_date] = []
            FreeOfDutyHandler.freeOfStandingEnd[end_date].append(self)
        else:
            print("ERROR!\nΔεν υπάρχει αυτό το είδος 'ελεύθερου'")


class Matcher():
    '''
    The class the matches privates with Duties
    '''

    def __init__(self):
        pass

    def privatesToDuties(self):
        privates = len(Private.availablePrivates())
        duties = len(Duty.dutiesList)
        return privates / duties

    def matchDutyWithPrivate(self, duty, privates_list, duty_list, today):
        # print(privates_list[0])  # for TESTING
        Duty.dailyDuties[duty] = f'{privates_list[0].last_name} {privates_list[0].first_name[0]}.'
        privates_list[0].add_Duty(str(duty), today)
        del privates_list[0]
        duty_list.remove(duty)

    # A function that contains what is needed for testing purposes
    def match(self, criteria):

        # print("Start matching")
        if criteria == 'dutiesDone':
            func = Private.getPrivatesWithMinDuties
        elif criteria == 'daysSinceLastDuty':
            func = Private.getPrivatesWithMostDays
        else:
            print("Error")
            raise Exception

        # create a list with the unarmed privates that that have the least duties,
        # comparing to other privates

        availableArmedPrivates, availableUnarmedPrivates = Private.getCandidatePrivates(func)

        unarmedDuties = Duty.getDuties(False)
        armedDuties = Duty.getDuties(True)

        # Adding duties to available privates.
        # When a duty is added to a soldier, both soldier and duty are
        # removed from the corresponding lity list

        # First, iterate over unarmed duties
        # i'm using a copy of the list, so I can mutate the original one
        for duty in list(unarmedDuties):
            # print("Duty: {}".format(duty))  # for testing

            # first iterate over available unarmed privates
            # cause unarmed privates can only do unarmed duties
            if len(availableUnarmedPrivates) > 0:
                self.matchDutyWithPrivate(duty, availableUnarmedPrivates, unarmedDuties, today)

        # Then, iterate over available armed privates
        # (not enough unarmed privates for unarmed privates)
            elif len(availableArmedPrivates) > 0:
                self.matchDutyWithPrivate(duty, availableArmedPrivates, unarmedDuties, today)

            else:
                print("Not enough available privates")
                availableArmedPrivates, availableUnarmedPrivates = Private.getCandidatePrivates(
                    func)

                # first iterate over available unarmed privates
                # cause unarmed privates can only do unarmed duties
                if len(availableUnarmedPrivates) > 0:
                    self.matchDutyWithPrivate(duty, availableUnarmedPrivates, unarmedDuties, today)

            # Then, iterate over available armed privates
            # (not enough unarmed privates for unarmed privates)
                elif len(availableArmedPrivates) > 0:
                    self.matchDutyWithPrivate(duty, availableArmedPrivates, unarmedDuties, today)

        # print("Unarmed Duties:     {}".format(unarmedDuties))  # for testing
        # print("---") # for testing

        for duty in list(armedDuties):
            # print("Duty: {}".format(duty))  # for testing

            if len(availableArmedPrivates) > 0:
                self.matchDutyWithPrivate(duty, availableArmedPrivates, armedDuties, today)
            else:
                print("Error! Not enough privates")
                availableArmedPrivates, availableUnarmedPrivates = Private.getCandidatePrivates(
                    func)

                if len(availableArmedPrivates) > 0:
                    self.matchDutyWithPrivate(duty, availableArmedPrivates, armedDuties, today)

        # print("Armed Duties:     {}".format(armedDuties))  # for testing
        # print("---") # for testing

        Private.calculateDaysPassed()
        # print(Private.availablePrivates())  # for testing


class LeavesCalculator():

    Departures = {}
    Arrivals = {}

    def __init__(self):
        pass

    @classmethod
    def calcDepartures(cls, dayObj):
        tommorowObj = dayObj + timedelta(days=1)
        tommorowStr = tommorowObj.strftime("%Y-%m-%d")

        if tommorowStr in cls.Departures.keys():
            for private in cls.Departures[tommorowStr]:
                private.available = False
                print(f'{private.last_name} is leaving on {dayObj}\n')

    @classmethod
    def calcArrivals(cls, dayObj):
        yesterdayObj = dayObj - timedelta(days=1)
        yesterdayStr = yesterdayObj.strftime("%Y-%m-%d")

        if yesterdayStr in cls.Arrivals.keys():
            for private in cls.Arrivals[yesterdayStr]:
                private.available = True
                print(f'{private.last_name} returned on {yesterdayObj}\n')


class FreeOfDutyHandler():

    freeOfDutyStart = {}
    freeOfDutyEnd = {}
    freeOfStandingStart = {}
    freeOfStandingEnd = {}

    def __init__(self):
        pass

    @classmethod
    def calc_free_of_duty_start(cls, dayObj):
        dayStr = dayObj.strftime("%Y-%m-%d")

        if dayStr in cls.freeOfDutyStart.keys():
            for private in cls.freeOfDutyStart[dayStr]:
                private.available = False
                print(f'Ο {private.last_name} {private.first_name[0]}. είναι ελεύθερος υπηρεσιών από {dayObj}.')

    @classmethod
    def calc_free_of_duty_end(cls, dayObj):
        dayStr = dayObj.strftime("%Y-%m-%d")

        if dayStr in cls.freeOfDutyEnd.keys():
            for private in cls.freeOfDutyEnd[dayStr]:
                private.available = True
                print(f'Ο {private.last_name} {private.first_name[0]}. δεν είναι πλέον ελεύθερος υπηρεσιών από {dayStr}.')

    @classmethod
    def calc_free_of_standing_start(cls, dayObj):
        dayStr = dayObj.strftime("%Y-%m-%d")

        standingDuties = ['ΤΑΞ1', 'ΤΑΞ2', 'ΤΑΞ3', 'ΤΑΞ4']

        if dayStr in cls.freeOfStandingStart.keys():
            for private in cls.freeOfStandingStart[dayStr]:
                for duty in standingDuties:
                    if duty in private.ableToDoduties.keys():
                        private.tempUnableToDo[duty] = private.ableToDoduties[duty]
                        del private.ableToDoduties[duty]
                print(f'Ο {private.last_name} {private.first_name[0]}. είναι ελεύθερος ορθοστασίας(ΤΑΞ) από {dayStr}.')

    @classmethod
    def calc_free_of_standing_end(cls, dayObj):
        dayStr = dayObj.strftime("%Y-%m-%d")

        standingDuties = ['ΤΑΞ1', 'ΤΑΞ2', 'ΤΑΞ3', 'ΤΑΞ4']

        if dayStr in cls.freeOfStandingEnd.keys():
            for private in cls.freeOfStandingEnd[dayStr]:
                for duty in standingDuties:
                    if duty in private.tempUnableToDo.keys():
                        private.ableToDoduties[duty] = private.tempUnableToDo[duty]
                        del private.tempUnableToDo[duty]
                print(f'Ο {private.last_name} {private.first_name[0]}. δεν είναι πλέον ελεύθερος ορθοστασίας(ΤΑΞ) από {dayStr}.')


imported_privates = []


class CSVHanlder():

    def __init__(self):
        pass

    def import_privates(self, filename):
        '''
        dummy method # for now
        '''
        with open(f'{filename}.csv', newline='') as f:
            reader = csv.reader(f)
            for row in reader:
                print(row)

    def export_privates(self, filename):
        '''
        dummy method # for now
        '''
        with open(f'{filename}.csv', 'w') as csvfile:
            fieldnames = ['last_name', 'first_name', ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            writer.writerow({'last_name': 'Christou', 'first_name': 'Christos'})

    def create_privates_from_cvs(self, filename):
        '''
        Generates Private object by reading a csv file.
        Input: a string. the filename, without the file extension
        '''
        with open(f'{filename}.csv', 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                imported_privates.append(Private(row[1], row[0], row[2], row[3],
                                                 str_to_bool(row[4]), str_to_bool(row[5])))


def initial_setup():
    # Creating new Duties
    th2 = Duty("Θ1", False)
    th1 = Duty("Θ2", False)
    th3 = Duty("Θ3", False)
    est1 = Duty("ΕΣΤ1", False)
    est2 = Duty("ΕΤΣ2", False)
    tax1 = Duty("ΤΑΞ1", True)
    tax2 = Duty("ΤΑΞ2", True)
    tax3 = Duty("ΤΑΞ3", True)
    tax4 = Duty("ΤΑΞ4", True)
    per1 = Duty("ΠΕΡ1", True)
    # kaay1 = Duty("Kaay1", True)
    # kaay2 = Duty("Kaay2", True)

    # Creating Privates objects
    # chris = Private("Christos", "Christou", "6972735589", "I4", False)
    # themis = Private("Themis", "Alexandridis", "690000001", "I4", False)
    # betas = Private("Giannis", "Betas", "690000002", "I4", False)
    # babas = Private("Thanasis", "Babas", "690000003", "I4", False)
    # rokas = Private("Giorgos", "Rokas", "690000004", "I3", True)
    # trachomas = Private("Pantelis", "Trachomas", "690000005", "I1", True)
    # martin = Private("Giorgos", "Martinidis", "69000006", "I1", True)
    #
    # # Adding some duties to Privates # for testing
    # themis.add_Duty("Thalamofilakas_2", today)
    #
    # # Adding Leaves # for testing
    # chris.add_leave('Kanoniki', '2018-08-01', '2018-08-05')
    # themis.add_leave('Kanoniki', '2018-08-01', '2018-08-02')
    # chris.increase_available_leaves('timitiki', 2)
    # chris.increase_available_leaves('timitiki', 1)
    #
    # print(chris.availableLeaves)


####### FOR TESTING #######
todayObject = datetime.date.today()  # + timedelta(days=1)
today = todayObject.strftime("%Y-%m-%d")
initial_setup()

# todayObject = datetime.date.today() + timedelta(days=1)
# today = todayObject.strftime("%Y-%m-%d")

h = CSVHanlder()
h.create_privates_from_cvs('Book2')

# add ΕΥ/ΕΥ to a private # TBA method
for private in Private.availablePrivates():
    if private.last_name == 'Γκούμας':
        private.add_free_of_duty('ΕΟ', '2018-08-01', 2)

m = Matcher()

# Daily routine
for i in range(10):
    # Create a var with today's date in from of YYYY-MM-DD
    today = todayObject.strftime("%Y-%m-%d")
    print("{} {}".format(today, is_weekday(todayObject)))
    # print("---")  # for testing

    # Calculate daily leaves and free of duties
    LeavesCalculator.calcDepartures(todayObject)
    LeavesCalculator.calcArrivals(todayObject)
    FreeOfDutyHandler.calc_free_of_duty_start(todayObject)
    FreeOfDutyHandler.calc_free_of_duty_end(todayObject)
    FreeOfDutyHandler.calc_free_of_standing_start(todayObject)
    FreeOfDutyHandler.calc_free_of_standing_end(todayObject)

    # make the matching / assigment
    m.match('dutiesDone')

    # Calc daily
    Private.calculateDaysPassed()

    # increment datetime object by one day
    todayObject += timedelta(days=1)

    print(Duty.dailyDuties)

    # Empty dailyDuties Dict
    Duty.dailyDuties = {}
    print("============================================")

# for testing
# for private in Private.availablePrivates():
#     print(private)
