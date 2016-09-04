class StateBase(object):
    def entry(self, event):
        pass

    def exit(self, event):
        pass

    def do(self, event):
        pass


class StateMachine(StateBase):
    def __init__(self, transitions, currentState, onStateChanged=None):
        self.__transitions = {}
        for (fromState, event, toState, guard, action) in transitions:
            transition = self.__transitions.get(fromState)
            if transition is None:
                transition = self.__transitions[fromState] = {}

            toStates = transition.get(event)
            if toStates is None:
                toStates = transition[event] = []

            toStates.append((toState, guard, action))

        self.setCurrentState(currentState)
        self.onStateChanged = onStateChanged


    def setCurrentState(self, currentState):
        self.__curState = currentState
        self.__curStateTransition = self.__transitions.get(currentState)

    def getCurrentState(self):
        return self.__curState

    def changeState(self, toState, action, evt):
        self.__curState.exit(evt)

        if action is not None:
            action(evt)

        if self.onStateChanged is not None:
            self.onStateChanged(self.__curState, toState)

        self.setCurrentState(toState)
        self.__curState.entry(evt)


    def do(self, event):
        changed = False
        toStates = self.__curStateTransition.get(event)
        if toStates is not None:
            for (toState, guard, action) in toStates:
                if guard is None or guard(event):
                    changed = True
                    self.changeState(toState, action, event)
                    break

        if not changed:
            self.__curState.do(event)

