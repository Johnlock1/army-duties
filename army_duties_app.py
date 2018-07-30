import datetime
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


class Duty():
    '''
    Duty as a class
    '''
    dutiesDict = {}
    dutiesList = []

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
        return("{} {} (Duties: {}, {} - Days: {})".format(self.last_name, self.first_name, self.dutiesDoneWeekdays, self.dutiesDoneWeekends, self.daysSinceLastDuty))

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

    def __init__(self, first_name, last_name, mobile_phone, somatiki_ikanotita, armed):
        super().__init__(first_name, last_name, mobile_phone)
        self.somatiki_ikanotita = somatiki_ikanotita
        self.armed = armed
        self.available = True
        self.availableLeaves = {'Kanoniki': 15}

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
            print('Success')

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
        privates_list[0].add_Duty(str(duty), today)
        del privates_list[0]
        duty_list.remove(duty)

    # A function that contains what is needed for testing purposes
    def match(self, criteria):

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
                availableArmedPrivates, availableUnarmedPrivates = \
                    Private.getCandidatePrivates(func)

                # first iterate over available unarmed privates
                # cause unarmed privates can only do unarmed duties
                if len(availableUnarmedPrivates) > 0:
                    self.matchDutyWithPrivate(duty, availableUnarmedPrivates, unarmedDuties, today)

            # Then, iterate over available armed privates
            # (not enough unarmed privates for unarmed privates)
                elif len(availableArmedPrivates) > 0:
                    self.matchDutyWithPrivate(duty, availableArmedPrivates, unarmedDuties, today)

        print("Unarmed Duties:     {}".format(unarmedDuties))  # for testing
        print("---")

        for duty in list(armedDuties):
            # print("Duty: {}".format(duty))  # for testing

            if len(availableArmedPrivates) > 0:
                self.matchDutyWithPrivate(duty, availableArmedPrivates, armedDuties, today)
            else:
                print("Error! Not enough privates")
                availableArmedPrivates, availableUnarmedPrivates = \
                    Private.getCandidatePrivates(func)

                if len(availableArmedPrivates) > 0:
                    self.matchDutyWithPrivate(duty, availableArmedPrivates, armedDuties, today)

        print("Armed Duties:     {}".format(armedDuties))  # for testing
        print("---")

        Private.calculateDaysPassed()
        print(Private.availablePrivates())  # for testing
        # for private in Private.availablePrivates():
        # print(private.soldierDutiesList)
        print("============================================")


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


def initial_setup():
    # Creating new Duties
    th2 = Duty("Thalamofilakas_1", False)
    th1 = Duty("Thalamofilakas_2", False)
    th3 = Duty("Thalamofilakas_3", False)
    est = Duty("Estiatoras", False)
    tax = Duty("Taxiarchia", True)
    # skopia = armedGuard
    # peripolo = armedPatrol

    # Creating Privates objects
    chris = Private("Christos", "Christou", "6972735589", "I4", False)
    themis = Private("Themis", "Alexandridis", "690000001", "I4", False)
    betas = Private("Giannis", "Betas", "690000002", "I4", False)
    babas = Private("Thanasis", "Babas", "690000003", "I4", False)
    rokas = Private("Giorgos", "Rokas", "690000004", "I3", True)
    trachomas = Private("Pantelis", "Trachomas", "690000005", "I1", True)
    martin = Private("Giorgos", "Martinidis", "69000006", "I1", True)

    # Adding some duties to Privates # for testing
    themis.add_Duty("Thalamofilakas_2", today)

    # Adding Leaves # for testing
    chris.add_leave('Kanoniki', '2018-08-01', '2018-08-05')
    themis.add_leave('Kanoniki', '2018-08-01', '2018-08-02')



####### FOR TESTING #######
todayObject = datetime.date.today()  # + timedelta(days=1)
today = todayObject.strftime("%Y-%m-%d")
initial_setup()

todayObject = datetime.date.today() + timedelta(days=1)
today = todayObject.strftime("%Y-%m-%d")

m = Matcher()

print(LeavesCalculator.Arrivals)

for i in range(14):  # test
    # Create a var with today's date in from of YYYY-MM-DD
    today = todayObject.strftime("%Y-%m-%d")
    print("{} {}".format(today, is_weekday(todayObject)))
    print("---")
    LeavesCalculator.calcDepartures(todayObject)
    LeavesCalculator.calcArrivals(todayObject)
    m.match('dutiesDone')
    Private.calculateDaysPassed()
    todayObject += timedelta(days=1)


# print(Private.sort(Private.allPrivates, 'dutiesDone'))
# print(Private.getPrivatesWithMostDays(Private.allPrivates))

# Private.calculateDaysPassed()
# aList = Private.sort(Private.allPrivates, 'daysSinceLastDuty')
# for private in aList:
#     print(private)
#
# print("-")
# print(f"Last private: {aList[-1]}")
#
# print("-")
#
# print(f"Final: {Private.getPrivatesWithMostDays(Private.allPrivates)}")
