import datetime
from datetime import timedelta
from copy import deepcopy


# def today_is_weekday():
#     '''
#     Helper function.
#     Returns True if today is a weekday or false if today is a weekend day.
#     '''
#     return datetime.date.today().weekday() < 5


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
        self.soldierDutiesList = deepcopy(Duty.dutiesDict)
        self.id = Soldier.soldier_counter
        Soldier.soldier_counter += 1

    # 'less than' magic method. Compares dutiesDone between two instances
    def __lt__(self, other):
        return self.dutiesDone < other.dutiesDone

    # Represent by print full name plus dutiesDone
    def __repr__(self):
        return("{} {} -> Duties: {}, {}, {}".format(self.last_name, self.first_name, self.dutiesDone, self.dutiesDoneWeekdays, self.dutiesDoneWeekends))

    # Now I can use 'dutiesDone', that automatically returns either dutiesDoneWeekdays or dutiesDoneWeekends, dependind of whether it's weekday or not, instead of having to check everytime.
    @property
    def dutiesDone(self):
        self._dutiesDone = self.dutiesDoneWeekdays if is_weekday(
            todayObject) else self.dutiesDoneWeekends
        return self._dutiesDone


class Private(Soldier):
    '''
    A child class of Soldier that is specific only for privates.
    '''
    availablePrivates = []
    availableArmedPrivates = []
    availableUnarmedPrivates = []

    def __init__(self, first_name, last_name, mobile_phone, somatiki_ikanotita, armed):
        super().__init__(first_name, last_name, mobile_phone)
        self.somatiki_ikanotita = somatiki_ikanotita
        self.armed = armed
        self.available = True

        # Each Private instance is being append to a list based on the armed parameter
        if self.armed == True:
            Private.availableArmedPrivates.append(self)
        else:
            Private.availableUnarmedPrivates.append(self)

        # Append object to a generic list, containing both armed and unarmed privates
        Private.availablePrivates.append(self)

    # Add a new duty to the private instance.
    def add_Duty(self, duty_name, date):
        # print(type(date))
        if is_weekday(todayObject):
            self.dutiesDoneWeekdays += 1
        else:
            self.dutiesDoneWeekends += 1

        self.lastDuty = date
        self.soldierDutiesList[duty_name].append(date)

    def add_leave(self, name, start_date, end_date):
        pass


class Matcher:
    '''
    The class the matches privates with Duties
    '''

    def __init__(self):
        pass

    def sortPrivatesByMinDuties(self, some_list):
        '''
        Input: a list with Private instances
        Output: a list
        '''
        return sorted(some_list, key=lambda private: private.dutiesDone)

    def getPrivatesWithMinDuties(self, some_list):
        '''
        Input: a list with Private instances
        Output: a list
        '''
        privatesList = self.sortPrivatesByMinDuties(some_list)
        # return list(filter(lambda private: private.dutiesDone==privatesList[0], privatesList))
        return list(filter(lambda private: private.dutiesDoneWeekdays == privatesList[0].dutiesDoneWeekdays if is_weekday(todayObject) else private.dutiesDoneWeekends == privatesList[0].dutiesDoneWeekends, privatesList))

    def getPrivates(self, some_list, armed):
        '''
        Get a sublist of privates, by passing a list of privates and a bool: if private is armed or not
        Two Inputs: a list and a boolean
        Output: One list with
        '''
        return list(filter(lambda private: private.armed == armed, some_list))

    def getCandidatePrivates(self):
        '''
        Generates two lists, one with armed and the other with unarmed privates,
        that've done the least duties, and therefore are candidates for duties
        Output: A tuple of two lists, each containing Private instances.
        '''
        privatesWithMinDuties = self.getPrivatesWithMinDuties(Private.availablePrivates)
        availableUnarmedPrivates = self.getPrivates(privatesWithMinDuties, False)
        print(f"Unarmed candidates: {availableUnarmedPrivates}")  # for testing
        availableArmedPrivates = self.getPrivates(privatesWithMinDuties, True)
        print(f"Armed candidates: {availableArmedPrivates}")  # for testing
        return (availableArmedPrivates, availableUnarmedPrivates)

    def getDuties(self, armed):
        '''
        Gets either armed or unarmed duties, depending on the input
        Input: a boolean
        Output: a list with duties
        '''
        return list(filter(lambda duty: duty.armed == armed, Duty.dutiesList))

    # A function that contains what is needed for testing purposes
    def match(self):

        # create a list with the unarmed privates that that have the least duties,
        # comparing to other privates
        privatesWithMinDuties = self.getPrivatesWithMinDuties(Private.availablePrivates)

        availableArmedPrivates, availableUnarmedPrivates = self.getCandidatePrivates()
        unarmedDuties = self.getDuties(False)
        armedDuties = self.getDuties(True)

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
                availableArmedPrivates, availableUnarmedPrivates = self.getCandidatePrivates()

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
                availableArmedPrivates, availableUnarmedPrivates = self.getCandidatePrivates()

                if len(availableArmedPrivates) > 0:
                    print(availableArmedPrivates[0])
                    availableArmedPrivates[0].add_Duty(str(duty), today)
                    del availableArmedPrivates[0]
                    armedDuties.remove(duty)

        print("Armed Duties:     {}".format(armedDuties))  # for testing
        print("---")

        print(Private.availablePrivates)  # for testing
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


# FOR TESTING
todayObject = datetime.date.today()  # + timedelta(days=1)
today = todayObject.strftime("%Y-%m-%d")
initial_setup()

m = Matcher()

for i in range(7):  # test
    # Create a var with today's date in from of YYYY-MM-DD
    today = todayObject.strftime("%Y-%m-%d")
    print("{} {}".format(today, is_weekday(todayObject)))
    print("---")
    m.match()
    todayObject += timedelta(days=1)


# FOR TESTING


# def matchDutyWithSolider(duty, duties_list, soldier_list):
#   print(soldier_list[0]) # for testing
#   soldier_list[0].add_Duty(str(duty), today)
#   del soldier_list[0]
#   duties_list.remove(duty)


# def test2():
# unarmedDuties = getDuties(False)
# armedDuties = getDuties(True)

# availableArmedPrivates, availableUnarmedPrivates = getCandidatePrivates()

# for duty in unarmedDuties:
#   if len(availableUnarmedPrivates) > 0:
#     matchDutyWithSolider(duty, unarmedDuties, availableUnarmedPrivates)
#   elif len(availableArmedPrivates) > 0:

#     matchDutyWithSolider(duty, unarmedDuties, availableArmedPrivates)

#   else:
#     availableArmedPrivates, availableUnarmedPrivates = getCandidatePrivates()
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
#     availableArmedPrivates, availableUnarmedPrivates = getCandidatePrivates()
#     if len(availableArmedPrivates) > 0:
#       matchDutyWithSolider(duty, armedDuties, availableArmedPrivates)
#     else:
#       print("---Error2--")
