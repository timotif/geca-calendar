from ics import Event
# c = Calendar()
# e = Event()
# e.name = "My cool event"
# e.begin = '2021-09-05 00:00:00'
# e.end = '2021-09-06 01:00:00'
# e.make_all_day()
# c.events.add(e)
# print(c.events)
# # [<Event 'My cool event' begin:2014-01-01 00:00:00 end:2014-01-01 00:00:01>]
# with open('./my.ics', 'w') as my_file:
#     my_file.writelines(c)
# # and it's done !


def save_to_calendar(calendar, project, filename='my.ics'):
    c = calendar
    e = Event()
    e.name = project.name
    e.begin = project.date_start
    e.end = project.date_end
    e.make_all_day()
    c.events.add(e)
    with open(f'./{filename}', 'w') as my_file:
        my_file.writelines(c)