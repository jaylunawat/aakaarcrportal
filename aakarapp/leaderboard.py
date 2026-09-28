from .models import taskEight, taskFive, taskFour, taskOne, taskSeven, taskSix, taskThree, taskTwo, TaskZero


def leaderboard(request):
    task1 = taskThree.objects.all()
    task2 = taskTwo.objects.all()
    task3 = taskOne.objects.all()
    task4 = taskFour.objects.all()
    task5 = taskFive.objects.all()
    task6 = taskSix.objects.all()
    task7 = taskSeven.objects.all()
    task8 = taskEight.objects.all()
    leaderboard  = {}
    for obj in task1:
        if leaderboard.get(obj.crid):
            leaderboard[obj.crid] += obj.marks
        else:
            leaderboard[obj.crid] = obj.marks
    for obj in task2:
        if leaderboard.get(obj.crid):
            leaderboard[obj.crid] += obj.marks
        else:
            leaderboard[obj.crid] = obj.marks
    for obj in task3:
        if leaderboard.get(obj.crid):
            leaderboard[obj.crid] += obj.marks
        else:
            leaderboard[obj.crid] = obj.marks
    for obj in task4:
        if leaderboard.get(obj.crid):
            leaderboard[obj.crid] += obj.marks
        else:
            leaderboard[obj.crid] = obj.marks
    for obj in task5:
        if leaderboard.get(obj.crid):
            leaderboard[obj.crid] += obj.marks
        else:
            leaderboard[obj.crid] = obj.marks
    for obj in task6:
        if leaderboard.get(obj.crid):
            leaderboard[obj.crid] += obj.marks
        else:
            leaderboard[obj.crid] = obj.marks
    for obj in task7:
        if leaderboard.get(obj.crid):
            leaderboard[obj.crid] += obj.marks
        else:
            leaderboard[obj.crid] = obj.marks
    for obj in task8:
        if leaderboard.get(obj.crid):
            leaderboard[obj.crid] += obj.marks
        else:
            leaderboard[obj.crid] = obj.marks   
    sorted_leaderboard = {k: leaderboard[k] for k in sorted(leaderboard)}
    top_five_crids = list(sorted_leaderboard.items())[:5]
    render(request, "leaderboard.html", {"top_crids": top_five_crids})
