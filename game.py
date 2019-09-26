import pygame


def mylog(s):
    print s

class Transition:
    def __init__(self, trigger_fn, exec_fn, name = ""):
        self.trigger_fn = trigger_fn # if ...
        self.exec_fn = exec_fn # then ...
        self.name = name

    def execute(self, model):
        self.exec_fn(model)

    def is_triggered(self, ctx):
        return self.trigger_fn(ctx)

# action's trigger function is run on input lists and such
class Action(Transition):
    pass

# event's trigger function is run on model
class Event(Transition):
    pass

class Model:
    pass

class View:
    def update_from_model(self, model):
        pass

class Game:
    def __init__(self):
        self.model = None
        self.view = None

        self.is_over = False

        self.possible_actions = []
        self.possible_events = []

    def quit(self):
        self.is_over = True

    def scan_actions(self):
        ctx = self.get_actions_ctx()
        return [a for a in self.possible_actions if a.is_triggered(ctx)]

    def scan_events(self):
        return [e for e in self.possible_events if e.is_triggered(self.model)]

    def get_actions_ctx():
        pass # unimplemented

    #def get_events_ctx():
    #    pass # unimplemented

    def add_event(self, t, e):
        self.possible_events.append(Event(t, e))

    def add_action(self, t, e):
        self.possible_actions.append(Action(t, e))

    def exec_actions(self, actions):
        # maybe side effects can be returned from here
        for a in actions:
            a.execute(self.model)

    def exec_events(self, events):
        # maybe side effects can be returned from here
        for e in events:
            e.execute(self.model)

    def update_view(self):
        self.view.update_from_model(self.model)

    def main_loop(self, speed = 10):

        pygame.init()

        clock = pygame.time.Clock()

        while not self.is_over:
            actions = self.scan_actions()
            self.exec_actions(actions)

            self.update_view()

            clock.tick(speed)

            events = self.scan_events()
            self.exec_events(events)

            self.update_view()

            clock.tick(speed)
