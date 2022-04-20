from calendar import MONDAY, week
from email import message
from operator import truediv
from datetime import date
from lightbulb.ext import tasks

import pyrebase
import hikari
import lightbulb
import datetime


firebaseConfig = {
  "apiKey": "AIzaSyDsv9SrHoCtK7l7GEp2rYVuzpAgkszsx64",
  "authDomain": "citb331-bot.firebaseapp.com",
  "databaseURL": "https://citb331-bot-default-rtdb.europe-west1.firebasedatabase.app",
  "projectId": "citb331-bot",
  "storageBucket": "citb331-bot.appspot.com",
  "messagingSenderId": "26434995499",
  "appId": "1:26434995499:web:2c063c38e233afab78f16e",
  "measurementId": "G-KWDXTQVPB9"
}

firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()

#Push data
# data = {"name":"Jason", "age": 20, "address": ["New York", "Sofia"]}
# db.push(data)

#Push data but with key
# data = {"name":"Jason", "age": 20, "address": ["New York", "Sofia"]}
# db.child("Jason").set(data)

#another example
# db.child("Branch").child("Employee").child("Male employees").push(data)

bot = lightbulb.BotApp(
    token='OTY0NDU2MDcwNzkxNzIwOTYw.Ylk5tg.dEeA3T_JXReZR7N_RsKBP0rxJQQ',
    default_enabled_guilds=(964449149963603988)
)

tasks.load(bot)

# @bot.listen(hikari.StartedEvent)
# async def on_start(event):
#     print('Bot has started!')

async def callback(self, ctx):
    await ctx.respond("callback")

@tasks.task(h=24, auto_start=True)
async def daily_reminder():
    today = date.today()

    #logic to check for upcoming tests
    tmp = []
    tests = db.child("Tests").child(today.year).get()
    upcomingTests = []
    if tests.val() == None:
        tmp.append('```')
        tmp.append('Upcoming tests:\n')
        tmp.append('None upcoming tests yet.')
        tmp.append('```')
    else:
        for test in tests.each():
            if(today.month <= int(test.val()['date'][3:5]) and today.day <= int(test.val()['date'][0:2])):
                upcomingTests.append(test.val())

        tmp.append('```')
        tmp.append('Upcoming tests:\n')
        for test in upcomingTests:
            tmp.append(test['date'] + " - " + test['start'] + "\t" + test['groups'][:-2] + '\n')
        tmp.append('```') 

    #logic for hw deadline check
    helper = [0,1,2,3,4,5,6]
    deadline_homework = db.child("Homeworks").child(today.year).get()
    days_till_homework_deadline = helper[(int(deadline_homework.val()['deadline'])) - datetime.date.today().isoweekday()]

    #logic for project deadline check
    project_deadline = db.child("Projects").child(today.year).get()
    if(project_deadline.val() == None):
        days_till_project_deadline = 'No deadline yet.'
    else:
        deadline = datetime.date(today.year, project_deadline.val()['month'], project_deadline.val()['day'])
        diff = deadline - datetime.date.today()
        days_till_project_deadline = diff.days


    #logic to structure the reminder message
    daily_reminder = '> **Daily reminder:** \n'
    tests = ''.join(tmp) 
    homework = '```Days until homework deadline:\n' + str(days_till_homework_deadline) + '```'
    project = '```Days until project deadline:\n' + str(days_till_project_deadline) + '```'
    msg = daily_reminder + tests + '\n' + homework + '\n' + project
    await bot.rest.create_message(965355965186715700, msg)


@bot.command
@lightbulb.command('ping', 'Checks if the bot is working.')
@lightbulb.implements(lightbulb.SlashCommand)
async def ping(ctx):
    await ctx.respond('Pong.')

@bot.command
@lightbulb.command('info', 'Get course information')
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def group_info(ctx):
    pass

@group_info.child
@lightbulb.command('general', 'Shows general information about the course.')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def subcommand(ctx):
    general = db.child("General").get()
    if(general.val() == None):
        return await ctx.respond("No general info available yet.")
    await ctx.respond(general.val())

@group_info.child
@lightbulb.command('schedule', 'Shows lectures schedule by groups.')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def subcommand(ctx):
    year = date.today().year
    groups = db.child("Groups").child(year).get()
    if(groups.val() == None):
        await ctx.respond("Group schedule still unavailable.")
    else:
        l = []
        l.append('```')
        i = 1
        for group in groups.each():
            if(group.val() == None):
                continue
            if(group.val()['day'] == 'd' or group.val()['timeframe'] == 'hh:mm'):
                l.append("Group " + str(i) + ":\tTo be announced\n")
            else:
                l.append("Group " + str(i) + ":\t" + group.val()['day'] + " " + group.val()['timeframe'] + '\n')
            i += 1
        l.append('```')      
        s = ''.join(l)
        await ctx.respond(s)

@group_info.child
@lightbulb.command('tests', 'Shows upcoming test dates.')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def subcommand(ctx):
    today = date.today()
    # this gets the current year in order to organize the data in Tests/CurrentYear path, however it only makes sense if 
    # the course takes place in a spring semester as it would guarantee that the test is always during current year
    tests = db.child("Tests").child(today.year).get()
    upcomingTests = []
    if tests.val() == None:
        return await ctx.respond('No upcoming tests (yet :smiling_imp:).')
    for test in tests.each():
        if(today.month <= int(test.val()['date'][3:5]) and today.day <= int(test.val()['date'][0:2])):
            upcomingTests.append(test.val())
    if(len(upcomingTests) == 0):
        return await ctx.respond('No upcoming tests (yet :smiling_imp:).') 
    tmp = []
    tmp.append('```')
    for test in upcomingTests:
        tmp.append(test['date'] + " - " + test['start'] + "\t" + test['groups'][:-2] + '\n')
    tmp.append('```')      
    s = ''.join(tmp)    
    await ctx.respond(s)
    


@bot.command
@lightbulb.command('create', 'Used to create objects.')
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def group_create(ctx):
    pass

@group_create.child
@lightbulb.option('count', '# of groups', type=int)
@lightbulb.option('year', 'year', type=int)
@lightbulb.command('groups', 'Creates groups for a selected year.')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def add(ctx):
    roles = await ctx.member.fetch_roles()
    isAuthorized = False
    for role in roles:
        if role.name == 'admin' or role.name == 'moderator':
            isAuthorized = True
            break
    if(isAuthorized == True):
        data = {}
        for i in range(1, ctx.options.count + 1):
            data[i] = {"day": "d", "timeframe": "hh:mm"}
        db.child("Groups").child(ctx.options.year).set(data)
        await ctx.respond(str(ctx.options.count) + " groups created for " + str(ctx.options.year))
    else:
        await ctx.respond("You don't have permissions to use this command.")

@group_create.child
@lightbulb.option('end', 'closing hour', type=str)
@lightbulb.option('start', 'starting hour', type=str)
@lightbulb.option('date', 'formatting has to be dd.mm', type=str)
@lightbulb.option('groups', 'group ids in CSV format (e.g. 1,2,3)', type=str)
@lightbulb.command('test_event', 'Creates a test event for selected groups.')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def add(ctx):
    roles = await ctx.member.fetch_roles()
    isAuthorized = False
    for role in roles:
        if role.name == 'admin' or role.name == 'moderator':
            isAuthorized = True
            break
    if(isAuthorized == True):
        if(len(ctx.options.date) != 5):
            return await ctx.respond("Formatting should be dd.mm")
        year = date.today().year
        # this gets the current year in order to organize the data in Tests/CurrentYear path, however it only makes sense if 
        # the course takes place in a spring semester as it would guarantee that the test is always during current year
        group_ids = ctx.options.groups.split(',')
        groups = ""
        for group in group_ids:
            groups += "Group " + group + ", "
        data = {"groups": groups,"date":ctx.options.date,"start": ctx.options.start, "end": ctx.options.end}
        db.child("Tests").child(year).push(data)
        await ctx.respond("Test event created successfully.")
    else:
        await ctx.respond("You don't have permissions to use this command.")

@group_create.child
@lightbulb.option('day', 'Set day', type=int)
@lightbulb.option('month', 'Set month', type=int)
@lightbulb.command('project_deadline', 'Sets deadline for current year\'s project.')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def add(ctx):
    roles = await ctx.member.fetch_roles()
    isAuthorized = False
    for role in roles:
        if role.name == 'admin' or role.name == 'moderator':
            isAuthorized = True
            break
    if(isAuthorized == True):
        data = {"day": ctx.options.day, "month": ctx.options.month}
        year = date.today().year
        # this gets the current year in order to organize the data in Tests/CurrentYear path, however it only makes sense if 
        # the course takes place in a spring semester as it would guarantee that the test is always during current year
        db.child("Projects").child(year).set(data)
        await ctx.respond("Project deadline successfully set for " + str(ctx.options.day) + '.' + str(ctx.options.month))
    else:
        await ctx.respond("You don't have permissions to use this command.")

@group_create.child
@lightbulb.option('day', 'Formatting: [0, 6] where Monday = 0, Tuesday = 1 etc ', type=str)
@lightbulb.command('homework_deadline', 'Sets deadline for current year\'s homeworks (assuming it is a recurring event).')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def add(ctx):
    roles = await ctx.member.fetch_roles()
    isAuthorized = False
    for role in roles:
        if role.name == 'admin' or role.name == 'moderator':
            isAuthorized = True
            break
    if(isAuthorized == True):
        year = date.today().year
        # this gets the current year in order to organize the data in Tests/CurrentYear path, however it only makes sense if 
        # the course takes place in a spring semester as it would guarantee that the test is always during current year
        day = int(ctx.options.day)
        if (day >= 0 and day <= 6):
            weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            data = {"deadline": ctx.options.day}
            db.child("Homeworks").child(year).set(data)
            await ctx.respond("Homework deadline successfully set as " + weekdays[day])
        else:
            await ctx.respond("Incorrect value. Please use correct formatting.")
    else:
        await ctx.respond("You don't have permissions to use this command.")

@bot.command
@lightbulb.command('update', 'Update course information.')
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def group_update(ctx):
    pass

@group_update.child
@lightbulb.option('hour', 'hour', type=str)
@lightbulb.option('day', 'day', type=str)
@lightbulb.option('id', 'group id', type=int)
@lightbulb.option('year', 'year', type=int)
@lightbulb.command('group', 'Adds schedule for selected group.')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def add(ctx):
    roles = await ctx.member.fetch_roles()
    isAuthorized = False
    for role in roles:
        if role.name == 'admin' or role.name == 'moderator':
            isAuthorized = True
            break
    if(isAuthorized == True):
        group = db.child("Groups").child(ctx.options.year).child(ctx.options.id).get()
        if(group.val() == None):
            await ctx.respond("Group doesn't exist.")
        else:
            data = {"day": ctx.options.day, "timeframe": ctx.options.hour}
            db.child("Groups").child(ctx.options.year).child(ctx.options.id).set(data)
            await ctx.respond("Group scheduled successfully.")
    else:
        await ctx.respond("You don't have permissions to use this command.")


@bot.command
@lightbulb.command('cancel', 'Cancellation of lectures/groups/etc.')
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def group_cancel(ctx):
    pass

@group_cancel.child
@lightbulb.option('id', 'group id', type=int)
@lightbulb.option('year', 'year', type=int)
@lightbulb.command('group', 'Cancels selected group.')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def add(ctx):
    roles = await ctx.member.fetch_roles()
    isAuthorized = False
    for role in roles:
        if role.name == 'admin' or role.name == 'moderator':
            isAuthorized = True
            break
    if(isAuthorized == True):
        group = db.child("Groups").child(ctx.options.year).child(ctx.options.id).get()
        if(group.val() == None):
            await ctx.respond("Group doesn't exist.")
        else:
            data = {"day": "CANCELLED", "timeframe":""}
            db.child("Groups").child(ctx.options.year).child(ctx.options.id).set(data)
            await ctx.respond("Group cancelled successfully.")
    else:
        await ctx.respond("You don't have permissions to use this command.")

@group_cancel.child
@lightbulb.option('starting_hour', 'starting hour formatting formatting must match the test event\'s', type=str)
@lightbulb.option('date', 'date formatting must match the test event\'s', type=str)
@lightbulb.command('test_event', 'Cancels selected test event (by date and starting hour).')
@lightbulb.implements(lightbulb.SlashSubCommand)
async def add(ctx):
    roles = await ctx.member.fetch_roles()
    isAuthorized = False
    for role in roles:
        if role.name == 'admin' or role.name == 'moderator':
            isAuthorized = True
            break
    if(isAuthorized == True):
        year = date.today().year
        # this gets the current year in order to organize the data in Tests/CurrentYear path, however it only makes sense if 
        # the course takes place in a spring semester as it would guarantee that the test is always during current year
        test_events = db.child("Tests").child(year).get()
        if(test_events.val() == None):
            await ctx.respond("Selected test event doesn't exist. Please, double check your formatting!")
        else:
            for test in test_events.each():
                if(test.val()['date'] == ctx.options.date and test.val()['start'] == ctx.options.starting_hour):
                    db.child("Tests").child(year).child(test.key()).remove()
                    return await ctx.respond("Test event cancelled successfully.")
            await ctx.respond("Selected test event doesn't exist. Please, double check your formatting!")
    else:
        await ctx.respond("You don't have permissions to use this command.")                

bot.run()