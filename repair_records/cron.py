from accounts.models import Factory
from .models import Equipment, RepairRecord, RepairType
from datetime import datetime


def update_prob_breaking():
    repair_types = get_repair_types()
    equations = get_equations()

    # iterate by Equipments
    for equipment in Equipment.objects.all():
        # get repair_records for past 3 months, splitted by months
        repair_records = get_repair_records(equipment)
        print(repair_records)

        # count them by their types
        results = []
        for repair_record in repair_records:
            if not repair_record:
                continue
            type_count = count_types(repair_record, repair_types)
            print(type_count)

            # calculate using formula
            result = calculate(
                equations[equipment.section.factory.id], type_count)
            results.append(result)

        print(results)

        # if the result of previous month is largen than 1,
        # then increment prob_breaking by 0.1
        if len(results) and results[0] is not None and results[0] >= 1:
            equipment.prob_breaking += 0.1
            print("increase happened")
        # if the results of past 3 months is smaller than 1,
        # then decrease prob_breaking by 0.1
        for result in results:
            if result is None or result >= 1:
                break
        else:
            if equipment.prob_breaking > 0 and len(results) == 3:
                equipment.prob_breaking -= 0.1
                print("decrease happened")

        equipment.save()


def get_repair_records(equipment: Equipment):
    # get past 3 months
    month = datetime.today().month
    year = datetime.today().year
    data = []

    for i in range(3):
        month, year = get_prev_month(month, year)
        data.append(
            RepairRecord.objects.filter(
                equipment=equipment,
                created_at__year=str(year),
                created_at__month=str(month)
            )
        )

    return data


def get_prev_month(month: int, year: int):
    if month == 1:
        return (12, year - 1)
    return (month - 1, year)


def get_repair_types():
    data = [x['codename']
            for x in RepairType.objects.all().values('codename').distinct()]
    # we are sorting, becuase there could a type which is substring of another
    # this is a problem while using equation for calculation
    data.sort(reverse=True)
    return data


def count_types(repair_record, repair_types):
    return {x: repair_record.filter(repair_type__codename=x)
            .count() for x in repair_types}


def get_equations():
    return {x.id: x.equation for x in Factory.objects.all()}


def calculate(equation, type_count):
    for key, value in type_count.items():
        equation = equation.replace(key, str(value))

    equation = ''.join('0' if char.isalpha() else char for char in equation)

    try:
        result = eval(equation)
    except Exception as e:
        print(e)
        result = None

    return result
