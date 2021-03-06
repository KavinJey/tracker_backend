from datetime import date, timedelta

from django.db.models import Sum

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from tracker_backend.trackerAPI.expenses.models import Expense


class DailyReport(APIView):
    """
    Gets a report of your total expenses for today
    """

    # Gets a report of expenses today
    def get(self, request, pk):

        # Determines the today's ISO-8601 value
        today = date.today()

        # Initializes an empty dict for storing report data
        report_data = {}

        # Queryset of all Expense objects from specified date range
        queryset = Expense.objects.filter(user=self.request.user, date=today)

        # Checks if queryset is not empty
        if not queryset.exists():

            # Returns error if no expenses are found in current week for current User in database
            return Response(data={"error": "Report cannot be generated. No expenses found today."},
                            status=status.HTTP_404_NOT_FOUND)

        # Updates the total amount of money spent on expenses in specified date range
        report_data.update({"expense_total": queryset.aggregate(Sum('value'))['value__sum']})

        # Initializes an empty dict for storing each category found in specified date range
        category_data = {}

        # Queryset of all distinct categories in specified date range
        category_set = Expense.objects.filter(user=self.request.user, date=today).values('category').distinct()

        # Iterates through all distinct categories determined above
        for c in category_set:

            # Queryset of all expenses made in a distinct category in specified date range
            day_category_set = Expense.objects.filter(user=self.request.user, date=today,
                                                      category__iexact=c['category'])

            # Updates the total amount of money spent on distinct category in specified date range
            # Key turned to lowercase string for readability purposes
            category_data.update({str(c['category']).lower(): day_category_set.aggregate(Sum('value'))['value__sum']})

            # Initializes an empty dict for storing each type found in a certain category found in specified date range
            type_data = {}

            # Queryset of all distinct types in a certain category found in specified date range
            type_set = Expense.objects.filter(user=self.request.user, date=today,
                                              category__iexact=c['category']).values('type').distinct()

            # Iterates through all distinct types in a certain category found in specified date range
            for t in type_set:

                # Queryset of all expenses made in a distinct type in a certain category in specified date range
                day_type_set = Expense.objects.filter(user=self.request.user, date=today,
                                                      category__iexact=c['category'], type=t['type'])

                # Updates the total amount of money spent on distinct type in a certain category in specified date range
                # Key turned to lowercase string for readability purposes
                type_data.update({str(t['type']).lower(): day_type_set.aggregate(Sum('value'))['value__sum']})

            # Updates category_data with type_data
            # Key turned to lowercase string for readability purposes
            category_data.update({str(c['category']+'_type_total').lower(): type_data})

        # Updates report_data with category_data
        report_data.update({'category_total': category_data})

        # Returns report_data as JSON response
        return Response(data=report_data, status=status.HTTP_200_OK)


class WeeklyReport(APIView):
    """
    Gets a report of your total expenses for the current week
    """

    # Gets a report of expenses in current week
    def get(self, request, pk):

        # Determines the today's and the week's start (Sunday of current week) ISO-8601 values
        today = date.today()
        week_start = today - timedelta(days=today.isoweekday() % 7)

        # Initializes an empty dict for storing report data
        report_data = {}

        # Queryset of all Expense objects from specified date range
        queryset = Expense.objects.filter(user=self.request.user, date__range=[week_start, today])

        # Checks if queryset is not empty
        if not queryset.exists():

            # Returns error if no expenses are found in current week for current User in database
            return Response(data={"error": "Report cannot be generated. No expenses found in current week."},
                            status=status.HTTP_404_NOT_FOUND)

        # Updates the total amount of money spent on expenses in specified date range
        report_data.update({"expense_total": queryset.aggregate(Sum('value'))['value__sum']})

        # Initializes an empty dict for storing each category found in specified date range
        category_data = {}

        # Queryset of all distinct categories in specified date range
        category_set = Expense.objects.filter(user=self.request.user, date__range=[week_start, today])\
            .values('category').distinct()

        # Iterates through all distinct categories determined above
        for c in category_set:

            # Queryset of all expenses made in a distinct category in specified date range
            week_category_set = Expense.objects.filter(user=self.request.user, date__range=[week_start, today],
                                                       category__iexact=c['category'])

            # Updates the total amount of money spent on distinct category in specified date range
            # Key turned to lowercase string for readability purposes
            category_data.update({str(c['category']).lower(): week_category_set.aggregate(Sum('value'))
            ['value__sum']})

            # Initializes an empty dict for storing each type found in a certain category found in specified date range
            type_data = {}

            # Queryset of all distinct types in a certain category found in specified date range
            type_set = Expense.objects.filter(user=self.request.user, date__range=[week_start, today],
                                              category__iexact=c['category']).values('type').distinct()

            # Iterates through all distinct types in a certain category found in specified date range
            for t in type_set:

                # Queryset of all expenses made in a distinct type in a certain category in specified date range
                week_type_set = Expense.objects.filter(user=self.request.user, date__range=[week_start, today],
                                                       category__iexact=c['category'], type=t['type'])

                # Updates the total amount of money spent on distinct type in a certain category in specified date range
                # Key turned to lowercase string for readability purposes
                type_data.update({str(t['type']).lower(): week_type_set.aggregate(Sum('value'))['value__sum']})

            # Updates category_data with type_data
            # Key turned to lowercase string for readability purposes
            category_data.update({str(c['category']+'_type_total').lower(): type_data})

        # Updates report_data with category_data
        report_data.update({'category_total': category_data})

        # Initializes an empty dict for storing each date found in specified date range
        date_data = {}

        # Queryset of all distinct dates in specified date range
        date_set = Expense.objects.filter(user=self.request.user, date__range=[week_start, today]).values('date')\
            .distinct().order_by('-date')

        # Iterates through all distinct dates in specified date range
        for d in date_set:

            # Queryset of all expenses made on a certain date in specified date range
            week_date_set = Expense.objects.filter(user=self.request.user, date=d['date'])

            # Updates the total amount of money spent on distinct date in specified date range
            # Key turned to string for dict purposes
            date_data.update({str(d['date']): week_date_set.aggregate(Sum('value'))['value__sum']})

        # Updates report_data with date_data
        report_data.update(({'date_total': date_data}))

        # Returns report_data as JSON response
        return Response(data=report_data, status=status.HTTP_200_OK)


class MonthlyReport(APIView):
    """
    Gets a report of your total expenses for the current month
    """

    # Gets a report of expenses in current month
    def get(self, request, pk):

        # Determines the today's and the month's start (1st of current month) ISO-8601 values
        today = date.today()
        month_start = today.replace(day=1)

        # Initializes an empty dict for storing report data
        report_data = {}

        # Queryset of all Expense objects from specified date range
        queryset = Expense.objects.filter(user=self.request.user, date__range=[month_start, today])

        # Checks if queryset is not empty
        if not queryset.exists():

            # Returns error if no expenses are found in current month for current User in database
            return Response(data={"error": "Report cannot be generated. No expenses found in current month."},
                            status=status.HTTP_404_NOT_FOUND)

        # Updates the total amount of money spent on expenses in specified date range
        report_data.update({"expense_total": queryset.aggregate(Sum('value'))['value__sum']})

        # Initializes an empty dict for storing each category found in specified date range
        category_data = {}

        # Queryset of all distinct categories in specified date range
        category_set = Expense.objects.filter(user=self.request.user, date__range=[month_start, today])\
            .values('category').distinct()

        # Iterates through all distinct categories determined above
        for c in category_set:

            # Queryset of all expenses made in a distinct category in specified date range
            month_category_set = Expense.objects.filter(user=self.request.user, date__range=[month_start, today],
                                                        category__iexact=c['category'])

            # Updates the total amount of money spent on distinct category in specified date range
            # Key turned to lowercase string for readability purposes
            category_data.update({str(c['category']).lower(): month_category_set.aggregate(Sum('value'))
            ['value__sum']})

            # Initializes an empty dict for storing each type found in a certain category found in specified date range
            type_data = {}

            # Queryset of all distinct types in a certain category found in specified date range
            type_set = Expense.objects.filter(user=self.request.user, date__range=[month_start, today],
                                              category__iexact=c['category']).values('type').distinct()

            # Iterates through all distinct types in a certain category found in specified date range
            for t in type_set:

                # Queryset of all expenses made in a distinct type in a certain category in specified date range
                month_type_set = Expense.objects.filter(user=self.request.user, date__range=[month_start, today],
                                                        category__iexact=c['category'], type=t['type'])

                # Updates the total amount of money spent on distinct type in a certain category in specified date range
                # Key turned to lowercase string for readability purposes
                type_data.update({str(t['type']).lower(): month_type_set.aggregate(Sum('value'))['value__sum']})

            # Updates category_data with type_data
            # Key turned to lowercase string for readability purposes
            category_data.update({str(c['category']+'_type_total').lower(): type_data})

        # Updates report_data with category_data
        report_data.update({'category_total': category_data})

        # Initializes an empty dict for storing each date found in specified date range
        date_data = {}

        # Queryset of all distinct dates in specified date range
        date_set = Expense.objects.filter(user=self.request.user, date__range=[month_start, today]).values('date')\
            .distinct().order_by('-date')

        # Iterates through all distinct dates in specified date range
        for d in date_set:

            # Queryset of all expenses made on a certain date in specified date range
            month_date_set = Expense.objects.filter(user=self.request.user, date=d['date'])

            # Updates the total amount of money spent on distinct date in specified date range
            # Key turned to string for dict purposes
            date_data.update({str(d['date']): month_date_set.aggregate(Sum('value'))['value__sum']})

        # Updates report_data with date_data
        report_data.update(({'date_total': date_data}))

        # Returns report_data as JSON response
        return Response(data=report_data, status=status.HTTP_200_OK)


class YearlyReport(APIView):
    """
    Gets a report of your total expenses for the current year
    """

    # Gets a report of expenses in current year
    def get(self, request, pk):

        # Determines the today's and the year's start (1st of current year) ISO-8601 values
        today = date.today()
        year_start = today.replace(month=1, day=1)

        # Initializes an empty dict for storing report data
        report_data = {}

        # Queryset of all Expense objects from specified date range
        queryset = Expense.objects.filter(user=self.request.user, date__range=[year_start, today])

        # Checks if queryset is not empty
        if not queryset.exists():

            # Returns error if no expenses are found in current year for current User in database
            return Response(data={"error": "Report cannot be generated. No expenses found in current year."},
                            status=status.HTTP_404_NOT_FOUND)

        # Updates the total amount of money spent on expenses in specified date range
        report_data.update({"expense_total": queryset.aggregate(Sum('value'))['value__sum']})

        # Initializes an empty dict for storing each category found in specified date range
        category_data = {}

        # Queryset of all distinct categories in specified date range
        category_set = Expense.objects.filter(user=self.request.user, date__range=[year_start, today])\
            .values('category').distinct()

        # Iterates through all distinct categories determined above
        for c in category_set:

            # Queryset of all expenses made in a distinct category in specified date range
            year_category_set = Expense.objects.filter(user=self.request.user, date__range=[year_start, today],
                                                       category__iexact=c['category'])

            # Updates the total amount of money spent on distinct category in specified date range
            # Key turned to lowercase string for readability purposes
            category_data.update({str(c['category']).lower(): year_category_set.aggregate(Sum('value'))
            ['value__sum']})

            # Initializes an empty dict for storing each type found in a certain category found in specified date range
            type_data = {}

            # Queryset of all distinct types in a certain category found in specified date range
            type_set = Expense.objects.filter(user=self.request.user, date__range=[year_start, today],
                                              category__iexact=c['category']).values('type').distinct()

            # Iterates through all distinct types in a certain category found in specified date range
            for t in type_set:

                # Queryset of all expenses made in a distinct type in a certain category in specified date range
                year_type_set = Expense.objects.filter(user=self.request.user, date__range=[year_start, today],
                                                       category__iexact=c['category'], type=t['type'])

                # Updates the total amount of money spent on distinct type in a certain category in specified date range
                # Key turned to lowercase string for readability purposes
                type_data.update({str(t['type']).lower(): year_type_set.aggregate(Sum('value'))['value__sum']})

            # Updates category_data with type_data
            # Key turned to lowercase string for readability purposes
            category_data.update({str(c['category']+'_type_total').lower(): type_data})

        # Updates report_data with category_data
        report_data.update({'category_total': category_data})

        # Initializes an empty dict for storing each date found in specified date range
        date_data = {}

        # Queryset of all distinct dates in specified date range
        date_set = Expense.objects.filter(user=self.request.user, date__range=[year_start, today]).values('date')\
            .distinct().order_by('-date')

        # Iterates through all distinct dates in specified date range
        for d in date_set:

            # Queryset of all expenses made on a certain date in specified date range
            year_date_set = Expense.objects.filter(user=self.request.user, date=d['date'])

            # Updates the total amount of money spent on distinct date in specified date range
            # Key turned to string for dict purposes
            date_data.update({str(d['date']): year_date_set.aggregate(Sum('value'))['value__sum']})

        # Updates report_data with date_data
        report_data.update(({'date_total': date_data}))

        # Returns report_data as JSON response
        return Response(data=report_data, status=status.HTTP_200_OK)
