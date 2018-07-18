import datetime
from datetime import timedelta
from copy import deepcopy
from operator import attrgetter


def is_weekday(day):
    '''
    One Input: datetime object
    Output: Returns True if the day passed as argument is a weekday
            or False if it's a weekend day.
    '''
    return day.weekday() < 5


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
        self.daysSinceLastDuty = 0
        self.soldierDutiesList = deepcopy(Duty.dutiesDict)
        self.id = Soldier.soldier_counter
        Soldier.soldier_counter += 1

    # 'less than' magic method. Compares dutiesDone between two instances
    def __lt__(self, other):
        return self.dutiesDone < other.dutiesDone

    # Represent by print full name plus dutiesDone
    def __repr__(self):
        return("{} {} -> Duties: {}, {}, {}".format(self.last_name, self.first_name, self.dutiesDone, self.dutiesDoneWeekdays, self.dutiesDoneWeekends))

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
    def getCandidatePrivates(cls):
        '''
        Generates two lists, one with armed and the other with unarmed privates,
        that've done the least duties, and therefore are candidates for duties
        Output: A tuple of two lists, each containing Private instances.
        '''
        privatesWithMinDuties = Private.getPrivatesWithMinDuties(Private.availablePrivates())
        availableUnarmedPrivates = Private.getPrivates(privatesWithMinDuties, False)
        print(f"Unarmed candidates: {availableUnarmedPrivates}")  # for testing
        availableArmedPrivates = Private.getPrivates(privatesWithMinDuties, True)
        print(f"Armed candidates: {availableArmedPrivates}")  # for testing
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
                private.daysSinceLastDuty = None

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

    def add_leave(self, name, start_date, end_date):
        pass


class HelperPrivate():
    '''
    Helper methods to Private class
    '''
    pass


class Matcher():
    '''
    The class the matches privates with Duties
    '''

    def __init__(self):
        pass

    # A function that contains what is needed for testing purposes
    def match(self):

        # create a list with the unarmed privates that that have the least duties,
        # comparing to other privates

        availableArmedPrivates, availableUnarmedPrivates = Private.getCandidatePrivates()
        unarmedDuties = Duty.getDuties(False)
        armedDuties = Duty.getDuties(True)

        # Adding duties to available privates.
        # When a duty is added to a soldier, both soldier and duty are
        # removed from the corresponding availability list

        # First, iterate over unarmed duties
        # i'm using a copy of the list, so I can mutate the original one
        for duty in list(unarmedDuties):
            print("Duty: {}".format(duty))  # for testing

            # first iterate over available unarmed privates
            # cause unarmed privates can only do unarmed duties
            if len(availableUnarmedPrivates) > 0:
                print(availableUnarmedPrivates[0])  # for testing
                availableUnarmedPrivates[0].add_Duty(str(duty), today)
                del availableUnarmedPrivates[0]
                unarmedDuties.remove(duty)

        # Then, iterate over available armed privates
        # (not enough unarmed privates for unarmed privates)
            elif len(availableArmedPrivates) > 0:
                print(availableArmedPrivates[0])
                availableArmedPrivates[0].add_Duty(str(duty), today)
                del availableArmedPrivates[0]
                unarmedDuties.remove(duty)

            else:
                print("Not enough available privates")
                availableArmedPrivates, availableUnarmedPrivates = Private.getCandidatePrivates()

                # first iterate over available unarmed privates
                # cause unarmed privates can only do unarmed duties
                if len(availableUnarmedPrivates) > 0:
                    print(availableUnarmedPrivates[0])  # for testing
                    availableUnarmedPrivates[0].add_Duty(str(duty), today)
                    del availableUnarmedPrivates[0]
                    unarmedDuties.remove(duty)

            # Then, iterate over available armed privates
            # (not enough unarmed privates for unarmed privates)
                elif len(availableArmedPrivates) > 0:
                    print(availableArmedPrivates[0])
                    availableArmedPrivates[0].add_Duty(str(duty), today)
                    del availableArmedPrivates[0]
                    unarmedDuties.remove(duty)
                # break

        print("Unarmed Duties:     {}".format(unarmedDuties))  # for testing
        print("---")

        for duty in list(armedDuties):
            print("Duty: {}".format(duty))  # for testing

            if len(availableArmedPrivates) > 0:
                print(availableArmedPrivates[0])
                availableArmedPrivates[0].add_Duty(str(duty), today)
                del availableArmedPrivates[0]
                armedDuties.remove(duty)
            else:
                print("Error! Not enough privates")
                availableArmedPrivates, availableUnarmedPrivates = Private.getCandidatePrivates()

                if len(availableArmedPrivates) > 0:
                    print(availableArmedPrivates[0])
                    availableArmedPrivates[0].add_Duty(str(duty), today)
                    del availableArmedPrivates[0]
                    armedDuties.remove(duty)

        print("Armed Duties:     {}".format(armedDuties))  # for testing
        print("---")

        print(Private.availablePrivates())  # for testing
        # for private in Private.availablePrivates():
        # print(private.soldierDutiesList)
        print("============================================")


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


####### FOR TESTING #######
todayObject = datetime.date.today()  # + timedelta(days=1)
today = todayObject.strftime("%Y-%m-%d")
initial_setup()


todayObject = datetime.date.today() + timedelta(days=1)
today = todayObject.strftime("%Y-%m-%d")

m = Matcher()
h = HelperPrivate()

for i in range(7):  # test
    # Create a var with today's date in from of YYYY-MM-DD
    today = todayObject.strftime("%Y-%m-%d")
    print("{} {}".format(today, is_weekday(todayObject)))
    print("---")
    m.match()
    Private.calculateDaysPassed()
    todayObject += timedelta(days=1)

print(Private.sort(Private.allPrivates, 'dutiesDone'))


####### FOR TESTING #######


# def matchDutyWithSolider(duty, duties_list, soldier_list):
#   print(soldier_list[0]) # for testing
#   soldier_list[0].add_Duty(str(duty), today)
#   del soldier_list[0]
#   duties_list.remove(duty)


# def test2():
# unarmedDuties = getDuties(False)
# armedDuties = getDuties(True)

# availableArmedPrivates, availableUnarmedPrivates = Private.getCandidatePrivates()

# for duty in unarmedDuties:
#   if len(availableUnarmedPrivates) > 0:
#     matchDutyWithSolider(duty, unarmedDuties, availableUnarmedPrivates)
#   elif len(availableArmedPrivates) > 0:

#     matchDutyWithSolider(duty, unarmedDuties, availableArmedPrivates)

#   else:
#     availableArmedPrivates, availableUnarmedPrivates = Privage.getCandidatePrivates()
#     if len(availableUnarmedPrivates) > 0:
#       matchDutyWithSolider(duty, unarmedDuties, availableUnarmedPrivates)
#     elif len(availableArmedPrivates) > 0:
#       matchDutyWithSolider(duty, unarmedDuties, availableArmedPrivates)
#     else:
#       print("---Error1--")


# for duty in armedDuties:
#   if len(availableArmedPrivates) > 0:
#     matchDutyWithSolider(duty, armedDuties, availableArmedPrivates)
#   else:
#     availableArmedPrivates, availableUnarmedPrivates = Private.getCandidatePrivates()
#     if len(availableArmedPrivates) > 0:
#       matchDutyWithSolider(duty, armedDuties, availableArmedPrivates)
#     else:
#       print("---Error2--")
