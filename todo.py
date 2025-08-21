#!/usr/bin/env python3

import argparse
import pickle
import os
import uuid
from datetime import datetime, timedelta

#path to pickle file in home directory
PICKLE_FILE = os.path.expanduser("~/.todo.pickle")

def age_in_days(created):
    '''
    calculated age
    '''
    age = datetime.now() - created
    return f'{age.days}d'

def parse_due_date(due_string):
    '''
    parse due date from string: 'MM/DD/YYYY', 'friday', or 'tomorrow'.
    https://www.datacamp.com/tutorial/converting-strings-datetime-objects
    https://www.geeksforgeeks.org/python/python-find-yesterdays-todays-and-tomorrows-date/
    '''
    if not due_string:
        return None

    try:
        return datetime.strptime(due_string, "%m/%d/%Y")
    except ValueError:
        pass

    weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    due_string = due_string.strip().lower()
    today = datetime.now()

    if due_string == 'tomorrow':
        return today + timedelta(days=1)

    if due_string in weekdays:
        today_index = today.weekday()
        target_index = weekdays.index(due_string)
        delta_days = (target_index - today_index + 7) % 7 or 7
        return today + timedelta(days=delta_days)

    return None

class Task:
    """Representation of a task
  
    Attributes:
                - created - date
                - completed - date
                - name - string
                - unique id - number
                - priority - int value of 1, 2, or 3; 1 is default
                - due date - date, this is optional
    """
    def __init__(self, name, priority = 1, due_date = None):
        self.name = name
        self.priority = int(priority)
        self.id = uuid.uuid4().int
        self.created = datetime.now()
        self.due_date = due_date
        self.completed = None

    def mark_completed(self):
        self.completed = datetime.now()

    def is_done(self):
        return self.completed is not None


class Tasks:
    """A list of `Task` objects."""

    def __init__(self):
        """Read pickled tasks file into a list"""
        # List of Task objects
        self.tasks = []
        if os.path.exists(PICKLE_FILE):
            with open(PICKLE_FILE, "rb") as f:
                self.tasks = pickle.load(f)
        self.tasks.sort(key=lambda t: t.created)

    def pickle_tasks(self):
        """Picle your task list to a file"""
        # your code here
        with open(PICKLE_FILE, "wb") as f:
            pickle.dump(self.tasks, f)

    # Complete the rest of the methods, change the method definitions as needed
    def add(self, name, due=None, priority=1):
        '''
        Add a new task by using the --add command
        '''
        due_date = parse_due_date(due) if due else None
        task = Task(name, priority, due_date)
        self.tasks.append(task)
        self.pickle_tasks()
        print(f"Created task {task.id}")

    def list(self):
        '''
        Use the --list command to display a list of the not completed tasks sorted by the due date. If tasks have the same due date, sort by decreasing priority (1 is the highest priority). If tasks have no due date, then sort by decreasing priority.
        '''
        active_tasks = [t for t in self.tasks if not t.is_done()]
        active_tasks.sort(key=lambda t: (t.due_date or datetime.max, -t.priority))
        print(f"{'ID':<40} {'Age':<5} {'Due':<12} {'Priority':<8} Task")
        print("-" * 110)
        for t in active_tasks:
            due_str = t.due_date.strftime("%m/%d/%Y") if t.due_date else "-"
            age_str = age_in_days(t.created)
            print(f"{t.id:<40} {age_str:<5} {due_str:<12} {t.priority:<8} {t.name}")

    def report(self):
        '''
        List all tasks, including both completed and incomplete tasks, using the report command.
        '''
        all_tasks = sorted(self.tasks, key=lambda t: (t.due_date or datetime.max, -t.priority))
        print(f"{'ID':<40} {'Age':<5} {'Due':<12} {'Priority':<8} {'Task':<25} {'Created':<25} Completed")
        print("-" * 110)
        for t in all_tasks:
            due_str = t.due_date.strftime("%m/%d/%Y") if t.due_date else "-"
            age_str = age_in_days(t.created)
            created_str = t.created.strftime("%Y-%m-%d %H:%M")
            completed_str = t.completed.strftime("%Y-%m-%d %H:%M") if t.completed else "-"
            print(f"{t.id:<40} {age_str:<5} {due_str:<12} {t.priority:<8} {t.name:<25} {created_str:<25} {completed_str}")

    def done(self, task_id):
        '''
        Complete a task by passing the done argument and the unique identifier.
        '''
        task_id = int(task_id)
        task = next((t for t in self.tasks if t.id == task_id), None)
        if task:
            task.mark_completed()
            self.pickle_tasks()
            print(f"Completed task {task.id}")
        else:
            print("Task not found.")

    def delete(self, task_id):
        '''
        Delete a task by passing the --delete command and the unique identifier.
        '''
        task_id = int(task_id)
        original_len = len(self.tasks)
        self.tasks = [t for t in self.tasks if not t.id == task_id]
        if len(self.tasks) < original_len:
            self.pickle_tasks()
            print(f"Deleted task {task_id}")
        else:
            print("Task not found.")

    def query(self, terms):
        '''
        Search for tasks that match a search term using the --query command. Only return tasks are not completed in your results.
        '''
        matches = [t for t in self.tasks if not t.is_done() and any(term.lower() in t.name.lower() for term in terms)]
        matches.sort(key=lambda t: (t.due_date or datetime.max, -t.priority))
        print(f"{'ID':<40} {'Age':<5} {'Due':<12} {'Priority':<8} Task")
        print("-" * 50)
        for t in matches:
            due_str = t.due_date.strftime("%m/%d/%Y") if t.due_date else "-"
            age_str = age_in_days(t.created)
            print(f"{t.id:<40} {age_str:<5} {due_str:<12} {t.priority:<8} {t.name}")


def main():
    '''All the real work!'''
    parser = argparse.ArgumentParser(description="Command Line Task Manager")
    parser.add_argument('--add', type=str, help='Task description')
    parser.add_argument('--due', type=str, help='Due date (MM/DD/YYYY, weekday, or tomorrow)')
    parser.add_argument('--priority', type=int, choices=[1,2,3], default=1, help='Priority 1=low, 3=high')

    parser.add_argument('--list', action='store_true', help='List incomplete tasks')
    parser.add_argument('--report', action='store_true', help='Show all tasks')
    parser.add_argument('--done', type=str, help='Mark task done by ID prefix')
    parser.add_argument('--delete', type=str, help='Delete task by ID prefix')
    parser.add_argument('--query', type=str, nargs='+', help='Search tasks by keywords')

    args = parser.parse_args()
    tasks = Tasks()

    if args.add:
        tasks.add(args.add, args.due, args.priority)
    elif args.list:
        tasks.list()
    elif args.report:
        tasks.report()
    elif args.done:
        tasks.done(args.done)
    elif args.delete:
        tasks.delete(args.delete)
    elif args.query:
        tasks.query(args.query)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()