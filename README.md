# Project: Army Duties

A script to automatically match and allocate privates to available duties every
day, as balanced as possible.

I created it in my free time inside the military base while serving in the greek
army, inspired by the will of privates not to have unfair treatment against
others. Those that served in the greek army, know what I'm taking about!

##  How matching/allocation works

The script first allocates the unarmed privates to duties that don't require a
rifle, and then in proceeds to the matching of armed privates to duties that
require a rifle (such as armed guard).

I created two methods to decide which private is a candidate for duty each day.

The first method check how many duties each private have and prioritise those
who have the least. It's worth noting that there are two sums of duties: one for
duties done in weekdays and one for duties done during the weekend.

The second method is experimental and tries to prioritise the privates who have
the most days since their last duty. This is achieved by calculating how
many days have passed since their last duty, sorting them by descending order,
and choosing first those at the top of the list.

Other features include the ability to add leave to a private (and therefore he
isn't considered available) and the ability to remove him from available privates
for some days due to health issues (free of duty).

## Future Goals - Know Issues

*If* I work on this script again, I would like to do the following improvements:

+ Improve matching logic to be export more balanced result.
+ Ability to handle more cornerstone cases, such as dealing with multiple-date
duties, balanced matching for privates that return from leave and others, privates
that can only do one specific duty and privates that can do duty only at specific
hours, due to others duties that they have (e.g. lawn mowing during specific hours)
+ More balanced matching among different duties, for each private.
+ Store previous days in disk/database.
+ Break script into multiple files.
+ Create an interface via terminal.

## Author

Christos Christou - https://github.com/Johnlock1/
